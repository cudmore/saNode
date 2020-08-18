"""
20200517
Robert Cudmore

Use napari to manually remove large vessels from mask.

Save results in _labeled_edited.tif

	Napari Keyboard:
		p: paint brush (draw around large vessel, removing small vessels befure mouse-click)
		z: zoom (e.g. PAN_ZOOM)
	
	My Mouse/Keyboard:
		mouse-click: set new label
		u: undo the last label assignment (e.g. the last click that set a new label)
		r: revert the selected label back to original label
			different than undo, any label set in the past can be reverted to original
		s: save labels as _labeled_edited.tif
		
		shift+m : switch between slice and blob select
			slice: will set a clicked label in one slice
			blob: will set a clicked label in all slice (be careful)
			
		shift+n : next file
		shift+p : previous file
		
	Notes:
		- 'Edit Labels' layer needs to be selected to respond to mouse clicks and edit labels
		- Can only edit in pan/zoom mode, select pan/zoom with "z" or click the magnifying glass icon
		
	todo:
		[fixed] We need a .csv to tell us the number of labels coming out of main analysis.
		This way we can make a new mask WITHOUT new labels created here
		
Troubleshooting:

	For conda, we need
	```
	conda install -c conda-forge contextlib2
	```
"""

import os, sys, json
import argparse

import numpy as np
import scipy
import skimage
import napari
import tifffile

#import bimpy

import aicsUtil

# 20200731, switched to contextlib2from contextlib2 import nullcontext # to have conditional 'with'

#from vascDen import myGetDefaultStackDict # vascDen.py needs to be in same folder
#import vascDen
import aicsUtil

class myLabelEdit:

	def __init__(self, pathToRawTiff, masterFilePath, folderPath=None, channel=2, withContext=True, verbose=True):
		"""
		pathToRawTiff: if None then start traversing masterFIlePath
			otherwise: /Users/cudmore/box/data/nathan/20200116/20190116__A01_G001_0007_ch1.tif
		withContext: True if we need to build a 'with' context, alse context is already created like from in Jupyter notebook
		"""
		
		self.verbose = verbose
		self.isDirty = False
		self.mode = 'removeSlice' # from (removeBlob, removeSlice)
		self.masterFilePath = masterFilePath
		self.folderPath = folderPath
		self.channel = channel
		
		self.doOneFile = False
		self.currentRowIdx = None
		if pathToRawTiff:
			self.doOneFile = True
		else:
			self.doOneFile = False
			# get first file from master db
			fileIdx, baseFileName = aicsUtil.getNextFile(masterFilePath, rowIdx=None, getThis='next')
			fileName = baseFileName + '_ch' + str(channel) + '.tif'
			pathToRawTiff = os.path.join(folderPath, fileName)
			print('  fileIdx:', fileIdx, 'pathToRawTiff:', pathToRawTiff)
		
			self.currentRowIdx = fileIdx
		
		self.switchFile(pathToRawTiff)
		
		#
		# will not return
		self.myNapari(withContext=withContext)
		
		#
		# done
		print('Napari window closed ... myLabelEdit finished ...')
		
	def switchFile(self, pathToRawTiff):
		"""
		Use this to go to next file in the analysis
		"""
		print('=== switchFile() path:', pathToRawTiff)
		
		#
		# check if dirty
		if self.isDirty:
			# prompt user to save
			print('\n\nWARNING: AUTO SAVING BEFOR SWITCHING FILES !!!\n\n')
			self.save()
			
		#
		# switch
		self.isDirty = False
		
		tmpFolder, tmpFilename = os.path.split(pathToRawTiff)
		tmpFileNameNoExtension, tmpExtension = tmpFilename.split('.')
		
		# switch from analysis2 to analysisAics
		if tmpFolder.endswith('aicsAnalysis'):
			# already in analysis folder
			self.analysisPath = tmpFolder
			# todo: not needed
			'''
			if tmpFileNameNoExtension.endswith('_raw'):
				tmpFileNameNoExtension = tmpFileNameNoExtension.replace('_raw', '')
			'''
		else:
			self.analysisPath = os.path.join(tmpFolder, 'aicsAnalysis')
		self.baseFileName = tmpFileNameNoExtension
		self.baseFilePath = os.path.join(self.analysisPath, self.baseFileName )
		#self.baseFileNameNoChannel = aicsUtil.removeChannelFromName(self.baseFileName)
		
		print('  self.baseFileName', self.baseFileName)
		print('  self.baseFilePath', self.baseFilePath)
		#print('  self.baseFileNameNoChannel', self.baseFileNameNoChannel)
		
		#
		# masterFilePath
		uFile, uInclude, uFirstSlice, uLastSlice = aicsUtil.parseMasterFile(self.masterFilePath, pathToRawTiff)
		
		self.uFirstSlice = uFirstSlice
		self.uLastSlice = uLastSlice
		
		print('  uFile:', uFile)
		print('  uInclude:', uInclude)
		print('  uFirstSlice:', uFirstSlice)
		print('  uLastSlice:', uLastSlice)

		#
		# where we will save out edit
		self.editLabelPath = self.baseFilePath + '_labeled_edited.tif' # using _edited to match output of removeSmallVessels.py
		self.finalMaskPath = self.baseFilePath + '_mask_final.tif' # using _edited to match output of removeSmallVessels.py
		self.editLabelData = None
		self.editLabelName = 'edit labels' # the name of our edit labels in Napari
		self.editLabelName2 = 'final labels' # onlys used to intercept mouse clicks
		#self.editLabelName = 'final labels' # the name of our edit labels in Napari
		#self.myLabelsLayer = None # filled in by self.myNapari()
		
		#
		# to load analysis from vascDen.py
		self.stackDict = aicsUtil.myGetDefaultStackDict()
		#print('stackDict:', json.dumps(self.stackDict, indent=4))

		#
		# undo
		self.undoMode = []
		self.undoLabelNumber = []
		self.undoNewLabelNumber = []
		self.undoSliceNumber = []
		self.undoSliceData = []

		self.floodFillIterations = 0
		
		self.origNumLabels = None
		
		#
		# load raw analysis stacks
		self.loadTheseStacks = ['raw', 'filtered', 'threshold0', 'threshold1', 'threshold', 'labeled', 'finalMask', 'finalMask_hull', 'finalMask_edt']
		self.loadTheseStacks = ['raw', 'labeled', 'mask', 'finalMask_hull', 'finalMask_edt']
		#self.loadTheseStacks = ['raw', 'labeled', 'finalMask', 'finalMask_hull', 'finalMask_edt']
		self.loadTheseStacks = ['raw', 'labeled', 'mask']
		self.load() 
		
		# need to do this in self.load() BEFORE pruning first/last slice
		#origNumLabels = np.max(self.stackDict['labeled']['data'])
		#self.origNumLabels = origNumLabels
		
		print('  self.origNumLabels:', self.origNumLabels)
	
	################################################################################
	def _printStackParams(self, name, myStack):
		print('  ', name, myStack.shape, myStack.dtype, 'dtype.char:', myStack.dtype.char,
			'min:', np.min(myStack),
			'max:', np.max(myStack),
			'mean:', np.mean(myStack),
			'std:', np.std(myStack),
			)

	################################################################################
	def myPrint(self, message):
		if self.verbose:
			print('  ', message)
		self.viewer.status = message
		
	################################################################################
	def load(self):
		"""
		load stacks from analysis2/
		
		populate self.stackDict[stackName]['data']
		"""	
		
		#print('vascDenNapari.load()')
		#print('  analysis path:', self.analysisPath)
		
		uFirstSlice = self.uFirstSlice
		uLastSlice = self.uLastSlice
		
		for idx, (stackName,v) in enumerate(self.stackDict.items()):
			fileIdx = idx #+ 1
			stackNameInFile = '_' + stackName
			#print('load() stackName:', stackName)
			if stackName == 'raw':
				# raw data in aicsAnalysis has not postfix string
				stackNameInFile = ''
			elif not stackName in self.loadTheseStacks:
				continue
			# v is a dist of keys (type, data)
			#idxStr = '_' + str(fileIdx) + '_'
			#fileName = self.baseFileName + idxStr + stackName + '.tif'
			#fileName = self.baseFileName + '_' + stackNameInFile + '.tif'
			fileName = self.baseFileName + stackNameInFile + '.tif'
			filePath = os.path.join(self.analysisPath, fileName)
			
			if not os.path.isfile(filePath):
				print('  Warning: did not find file', filePath)
				continue
				
			print('  loading:', fileName)
			#
			data = tifffile.imread(filePath)

			# get original number of labels before we prune
			if stackName == 'labeled': # must be in self.loadTheseStacks
				origNumLabels = np.max(data)
				self.origNumLabels = origNumLabels

			#
			# strip u first/last
			if uFirstSlice is not None and (uFirstSlice>=0):
				print('  ', stackName, 'pruning uFirstSlice:', uFirstSlice)
				data[0:uFirstSlice-1,:,:] = 0
			if uLastSlice is not None and (uLastSlice>=0):
				print('  ', stackName, 'pruning uLastSlice:', uLastSlice)
				data[uLastSlice+1:-1,:,:] = 0
				
			self.stackDict[stackName]['data'] = data
			#print('   ', self.stackDict[stackName]['data'].shape)
			#

			# try and loaded edited labels
			if stackName == 'labeled':			
				if os.path.isfile(self.editLabelPath):
					tmpPath, tmpFilename = os.path.split(self.editLabelPath)
					print('  LOADING: labeled_edited.tif from:', tmpFilename)
					self.editLabelData = tifffile.imread(self.editLabelPath)
					#
					# strip u first/last
					if uFirstSlice is not None and (uFirstSlice>=0):
						print('  ', 'labeled_edited', 'pruning uFirstSlice:', uFirstSlice)
						self.editLabelData[0:uFirstSlice-1,:,:] = 0
					if uLastSlice is not None and (uLastSlice>=0):
						print('  ', 'labeled_edited', 'pruning uLastSlice:', uLastSlice)
						self.editLabelData[uLastSlice+1:-1,:,:] = 0
				else:
					print('  CREATING: editLabels from original labeled.tif')
					self.editLabelData = data.copy() # 'data' is original labeled
				
				self.finalLabeled = None
				self.updateFinalLabel(doUpdate=False)
				
				#print('    self.editLabelData.shape:', self.editLabelData.shape)
				
	def selectFinalLabels(self):
		"""
		"""
		for layer in self.viewer.layers:
			if layer.name == self.editLabelName2:
				layer.selected = True
			else:
				layer.selected = False

	def getEditLabelData(self, viewer):
		"""
		get layer.data named editLabelName
		"""
		for idx, layer in enumerate(viewer.layers):
			if layer.name == self.editLabelName:
				retIdx = idx
				break
		if viewer.layers is not None:
			return viewer.layers[retIdx].data
		else:
			return None
		
	def getEditLabelLayer(self, viewer):
		"""
		get layer named editLabelName
		"""
		for idx, layer in enumerate(viewer.layers):
			if layer.name == self.editLabelName:
				retIdx = idx
				break
		if viewer.layers is not None:
			return viewer.layers[retIdx]
		else:
			return None
		
	def setUndo(self, mode, labelNumber, newLabelNumber, sliceNum, data):
		"""
		add to undo list
		
		mode: (blob, slice)
		"""
		self.undoMode.append(mode)
		self.undoLabelNumber.append(labelNumber)
		self.undoNewLabelNumber.append(newLabelNumber)
		self.undoSliceNumber.append(sliceNum)
		self.undoSliceData.append(data.copy()) # copy is important

	def undo(self, viewer):
		if self.undoSliceData:
			undoMode = self.undoMode.pop()
			undoLabelNumber = self.undoLabelNumber.pop() # the label that was clicked on
			undoNewLabelNumber = self.undoNewLabelNumber.pop() # the label we originally created
			undoSliceNumber = self.undoSliceNumber.pop()
			undoSliceData = self.undoSliceData.pop()

			labelLayer = self.getEditLabelLayer(viewer)
			#labelData = self.getEditLabelData(viewer)
			if labelLayer is not None:
				if undoMode == 'removeBlob':
					labelLayer.data[:,:,:] = undoSliceData
					#labelData[:,:,:] = undoSliceData
				elif undoMode == 'removeSlice':
					labelLayer.data[undoSliceNumber,:,:] = undoSliceData
					#labelData[undoSliceNumber,:,:] = undoSliceData
				
				#
				#labelLayer = self.getEditLabelLayer(viewer)
				labelLayer.refresh()

				# set to the slice we just did uno on
				viewer.dims.set_point(0, undoSliceNumber) # set slice

				numUndoRemaining = len(self.undoLabelNumber)
				#statusStr = 'Did undo of label ' + str(undoNewLabelNumber) + ' back to original label ' + str(undoLabelNumber) + ' ' + str(numUndoRemaining) + ' undo remain.'
				statusStr = f'Did undo of {undoMode} label {undoNewLabelNumber} back to original label {undoLabelNumber}, {numUndoRemaining} undo remain.'
				self.myPrint(statusStr)
			
				if undoMode == 'removeBlob':
					self.updateFinalLabel() # update entire stack
				elif undoMode == 'removeSlice':
					self.updateFinalLabel(sliceNum=undoSliceNumber)

			self.isDirty = True
			
		else:
			statusStr = 'No undo data'
			self.myPrint(statusStr)
			#print(statusStr)
			#viewer.status = statusStr
			
	def save(self, viewer=None):
		"""
		save _v2 label layer
		"""	
		if viewer is None:
			viewer = self.viewer
		
		labelLayer = self.getEditLabelLayer(viewer)
		data = labelLayer.data # save this
		
		statusStr = 'Saving ' + self.editLabelPath
		self.myPrint(statusStr)
		#labelLayer.refresh()
		
		print('  ', data.shape)
		
		tifffile.imsave(self.editLabelPath, data)

		# save final mask
		statusStr = 'Saving ' + self.finalMaskPath
		self.myPrint(statusStr)
		# create final mask
		self.finalMask = np.where(self.finalLabeled > 0, 1, 0).astype(np.uint8)
		tifffile.imsave(self.finalMaskPath, self.finalMask)
		
		self.isDirty = False
		
		statusStr = 'Done saving ' + self.editLabelPath
		self.myPrint(statusStr)
		#print(statusStr)
		#viewer.status = statusStr
		
	def revertLabel(self, viewer=None):
		"""
		set the current lavel in edit labl back to self.origNumLabels
		
		not optimal
		"""
		if viewer is None:
			viewer = self.viewer
		
		mySlice = self.viewer.dims.point[0] # get the slice
		
		layer = self.getEditLabelLayer(viewer)
		cords = np.round(layer.coordinates).astype(int) # [z,x,y], remember x is down, y is right
		myCoords = (cords[1], cords[2]) # tuple

		val = layer.get_value() # the label clicked on

		if val is None:
			statusStr = "Revert got bad label value " + str(val)
			self.myPrint(statusStr)
			return
			
		#
		# only revert if it is a label we modified
		if val <= self.origNumLabels:
			statusStr = "Can't revert an original label. Label number " + str(val)
			self.myPrint(statusStr)
			#print(statusStr)
			#viewer.status = statusStr
			return
			
		#
		# set the selected label back to self.origNumLabels
		originalLabelData = self.stackDict['labeled']['data'] 
		originalVal = originalLabelData[mySlice, myCoords[0], myCoords[1]]
		
		sliceData = layer.data[mySlice,:,:]
		sliceData[sliceData==val] = originalVal
		layer.data[mySlice,:,:] = sliceData
		
		layer.refresh()
		
		self.updateFinalLabel(sliceNum=mySlice)
		
		self.isDirty = True
		
		statusStr = 'Reverted label ' + str(val) + ' back to original label ' + str(originalVal)
		self.myPrint(statusStr)

		print('    *** layer.data.shape:', layer.data.shape)
		
	def updateFinalLabel(self, sliceNum=None, doUpdate=True):
		"""
		final label is temporary, not loaded/saved
		"""
		#labeledData = self.stackDict['labeled']['data'] # original
		#self.editLabelData
		
		if sliceNum is None:
			# whole stack
			#print('updateFinalLabel() whole stack')
			self.finalLabeled = np.where(self.editLabelData > self.origNumLabels, 0, self.editLabelData)
			if doUpdate:
				self.myFinalLabelsLayer.data = self.finalLabeled
				self.myFinalLabelsLayer.refresh()
		else:
			# one slice
			#print('updateFinalLabel() sliceNum:', sliceNum)
			self.finalLabeled[sliceNum,:,:] = np.where(self.editLabelData[sliceNum,:,:] > self.origNumLabels, 0, self.editLabelData[sliceNum,:,:])
			# todo: we don't visualize this, could defer to saving?
			#self.finalMask[sliceNum,:,:] = np.where(self.finalLabeled[sliceNum,:,:] > 0, 1, 0).astype(np.uint8)
			if doUpdate:
				self.myFinalLabelsLayer.data[sliceNum,:,:] = self.finalLabeled[sliceNum,:,:]
				self.myFinalLabelsLayer.refresh()
		
	def editLabel(self, layer, event):
		"""
		Add a new label in the current slice, pixels under mouse pointer
		
		layer: has to be self.editLabelName
		"""

		print('=== editLabel() layer:', layer, 'floodFillIterations:', self.floodFillIterations)
		
		if layer.name != self.editLabelName2:
			# this never happens ???
			statusStr = 'mouse-click has to be in layer:' + self.editLabelName2 + ' ... NO ACTION TAKEN ...'
			self.myPrint(statusStr)
			return
		
		# mode can be (pan_zoom, pick, paint, fill)
		if layer.mode != 'pan_zoom':
			#print('can only edit in pan/zoom mode, select pan/zoom with "z" or click the magnifying glass icon')
			return
			
		# using member viewer in code !!! ???
		mySlice = self.viewer.dims.point[0] # get the slice

		#viewer.dims.set_point(axis, currentSlice) # set slice

		cords = np.round(layer.coordinates).astype(int) # [z,x,y], remember x is down, y is right
		myCoords = (cords[1], cords[2]) # tuple

		val = layer.get_value() # the label clicked on
		if val is None:
			statusStr = 'val was "None" ... not sure why'
			self.myPrint(statusStr)
			#print(statusStr)
			#layer.status = statusStr
			return
		
		if val > self.origNumLabels:
			statusStr = "Can't set a label again " + str(val)
			self.myPrint(statusStr)
			#print(statusStr)
			#layer.status = statusStr
			return
			
		# 20200813
		# editLabelData
		layer = self.myLabelsLayer
		
		currentNumberOfLabel = np.nanmax(layer.data)
		newLabel = currentNumberOfLabel + 1
			
		#
		#
		msg = ''
		myRegion = None
		if val > 0:
			
			if self.mode == 'removeBlob':
				print('=== editLabel() remove blob')
				self.setUndo(self.mode, val, newLabel, mySlice, layer.data)
				# 20200813, oh no, I have no idea why I need [:,:,:] on lhs -->> very bad !!!!
				layer.data[:,:,:] = np.where(layer.data==val, newLabel, layer.data)

				self.updateFinalLabel() # update entire stack -->> slow
			
			elif self.mode == 'removeSlice':
				sliceData = layer.data[mySlice,:,:]

				self.setUndo(self.mode, val, newLabel, mySlice, sliceData)

				newValue = newLabel
			
				floodFillIterations = self.floodFillIterations
				if floodFillIterations == 0: # control with keyboard +/-
					# was this
					# flood_fill on JUST the label clicked on
					myRegion = skimage.morphology.flood_fill(sliceData, myCoords, newValue)
					#self._printStackParams('myRegion', myRegion)
				else:
					# dilate
					sliceDataBool = scipy.ndimage.binary_dilation(sliceData, iterations=floodFillIterations)
					# needed to fit labels >256 in next flood_fill()
					sliceDataBool = sliceDataBool.astype(np.uint16)
					#onesInBool = np.count_nonzero(sliceDataBool == 1)
					#self._printStackParams('sliceDataBool', sliceDataBool)
					#print('    onesInBool:', onesInBool)
				
					# flood_fill on (0/1) binary_dilation
					myRegion2 = skimage.morphology.flood_fill(sliceDataBool, myCoords, newValue)		
					#newValueInMyRegion2 = np.count_nonzero(myRegion2 == newValue)
					#self._printStackParams('myRegion2', myRegion2)
					#print('    newValueInMyRegion2:', newValueInMyRegion2)

					# revert back to labels
					# create a region with original labels (sliceData) and new region (newValue)
					# was here
					myRegion = np.where((sliceData>0) & (myRegion2==newValue), newValue, sliceData)
					#self._printStackParams('myRegion', myRegion)
			
				layer.data[mySlice,:,:] = myRegion
				
				# new 20200813
				self.updateFinalLabel(sliceNum=mySlice)
			
			#
			layer.refresh()

			if myRegion is not None:
				numNewValueInRegion = np.count_nonzero(myRegion == newValue)
			else:
				numNewValueInRegion = None
			msg = f'Clicked at {cords} on label {val} which is now label {newLabel} with {numNewValueInRegion} pixels'
			self.myPrint(msg)
		
			self.isDirty = True
			
		else:
			msg = f'Clicked at {cords} on background which is ignored'
			self.myPrint(msg)
			

	def switchNapari(self):
		"""
		Switch Napari interface with  a new file
		"""
		
		print('switchNapari()')
		
		self.viewer.title = self.baseFileName
		
		for idx, (stackName,v) in enumerate(self.stackDict.items()):
			if not stackName in self.loadTheseStacks:
				continue

			type = v['type'] # (image, mask, label)
			data = v['data']
			
			if data is None:
				# not loaded
				print('  myNapari() stackName:', stackName, 'Warning: DID NOT FIND DATA')
				continue
			
			#print('  myNapari() stackName:', stackName, data.shape)
			
			if type == 'image':
				self.myImageLayer.data = data
				self.myImageLayer.name = stackName
			if type == 'mask':
				self.myMaskLayer.data = data
				self.myMaskLayer.name = stackName
			elif type == 'label':
				self.myLabelsLayer0.data = data
				self.myLabelsLayer0.name = stackName
				
				self.myLabelsLayer.data = self.editLabelData
				self.myLabelsLayer.name = self.editLabelName
			
				# not loaded/saved, show out final labels
				self.myFinalLabelsLayer.data = self.finalLabeled
				self.myFinalLabelsLayer.name = self.editLabelName2
				#

		# select slice
		if self.uLastSlice is not None and self.uFirstSlice >=0:
			self.viewer.dims.set_point(0, self.uFirstSlice-1) # set slice
		else:
			self.viewer.dims.set_point(0, 0) # set slice 0

		# select edit layers
		self.selectFinalLabels()

	def myNapari(self, withContext=True):
		if withContext:
		    cm = napari.gui_qt()
		else:
		    cm = nullcontext()

		#with napari.gui_qt():
		with cm:

			# this is super confusing, used from Jupyter notebooks
			self.viewer = napari.Viewer(title=self.baseFileName)
	
			for idx, (stackName,v) in enumerate(self.stackDict.items()):
				if not stackName in self.loadTheseStacks:
					continue

				type = v['type'] # (image, mask, label)
				data = v['data']
				
				if data is None:
					# not loaded
					print('  myNapari() stackName:', stackName, 'Warning: DID NOT FIND DATA')
					continue
				
				#print('  myNapari() stackName:', stackName, data.shape)
				
				if type == 'image':
					minContrast= 0 
					maxContrast = 180 #np.nanmax(data)
					self.myImageLayer = self.viewer.add_image(data, contrast_limits=(minContrast, maxContrast), visible=False, name=stackName)
				if type == 'mask':
					minContrast= 0 
					maxContrast = 1
					self.myMaskLayer = self.viewer.add_image(data, contrast_limits=(minContrast, maxContrast), opacity=0.66, visible=False, name=stackName)
				elif type == 'label':
					self.myLabelsLayer0 = self.viewer.add_labels(data, opacity=0.7, visible=False, name=stackName)
					print('editable layer name is:', stackName)
					
					# switch this to _v2
					editLabelData = self.editLabelData #data.copy()
					self.myLabelsLayer = self.viewer.add_labels(editLabelData, opacity=0.7, visible=False, name=self.editLabelName)
				
					# not loaded/saved, show out final labels
					finalLabeledData = self.finalLabeled #data.copy()
					self.myFinalLabelsLayer = self.viewer.add_labels(finalLabeledData, opacity=0.7, visible=True, name=self.editLabelName2)
					
			'''
			if self.myLabelsLayer is None:
				fakeData = np.ndarray((1,1,1))
				self.myLabelsLayer = self.viewer.add_labels(fakeData, opacity=0.7, visible=False, name='x ' + self.editLabelName)
			'''
			
			# set slice
			if self.uLastSlice is not None and self.uFirstSlice >=0:
				self.viewer.dims.set_point(0, self.uFirstSlice-1) # set slice
			
			# select edit layers
			self.selectFinalLabels()
			
			#
			# Callbacks
			#
			@self.viewer.bind_key('Shift-N')
			def myNextFile(viewer):
				if self.doOneFile:
					print('  only working on one file...')
				else:
					#nextTiff = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0014_ch2.tif'
					nextIdx, nextBase = aicsUtil.getNextFile(self.masterFilePath, rowIdx=self.currentRowIdx, getThis='next')
					if nextIdx is None or nextBase is None:
						print('no next file, done?')
						pass
					else:
						nextFileName = nextBase + '_ch' + str(self.channel) + '.tif'
						nextPath = os.path.join(self.folderPath, nextFileName)
						print(nextIdx, nextBase, nextPath)
						self.currentRowIdx = nextIdx
						#
						self.switchFile(nextPath)
						self.switchNapari()
				
			@self.viewer.bind_key('Shift-P')
			def myPrevFile(viewer):
				if self.doOneFile:
					print('  only working on one file...')
				else:
					#nextTiff = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0014_ch2.tif'
					nextIdx, nextBase = aicsUtil.getNextFile(self.masterFilePath, rowIdx=self.currentRowIdx, getThis='previous')
					if nextIdx is None or nextBase is None:
						print('no previous file, done?')
						pass
					else:
						nextFileName = nextBase + '_ch' + str(self.channel) + '.tif'
						nextPath = os.path.join(self.folderPath, nextFileName)
						print(nextIdx, nextBase, nextPath)
						self.currentRowIdx = nextIdx
						#
						self.switchFile(nextPath)
						self.switchNapari()
				
			@self.viewer.bind_key('Shift-M')
			def myChangeMode(viewer):
				if self.mode == 'removeBlob':
					self.mode = 'removeSlice'
				else:
					self.mode = 'removeBlob'
				statusStr = f'Mode is now {self.mode}'
				self.myPrint(statusStr)
			
			@self.viewer.bind_key('s')
			def mySave(viewer):
				self.save(viewer)

			@self.viewer.bind_key('r')
			def myRemove(viewer):
				self.revertLabel(viewer)
			
			@self.viewer.bind_key('u')
			def myUndo(viewer):
				self.undo(viewer)
			
			@self.viewer.bind_key('.')
			def myAdjustFloodFill_Plus(viewer):
				self.floodFillIterations += 1
				msgStr = f'Flood fill Iterations is now {self.floodFillIterations}'
				self.myPrint(msgStr)
				#print('  floodFillIterations:', self.floodFillIterations)
			
			@self.viewer.bind_key(',')
			def myAdjustFloodFill_Minus(viewer):
				self.floodFillIterations -= 1
				if self.floodFillIterations < 0:
					self.floodFillIterations = 0
				msgStr = f'Flood fill Iterations is now {self.floodFillIterations}'
				self.myPrint(msgStr)
				#print('  floodFillIterations:', self.floodFillIterations)
			
			# was this
			#@self.myLabelsLayer.mouse_drag_callbacks.append
			@self.myFinalLabelsLayer.mouse_drag_callbacks.append
			def get_connected_component_shape(layer, event):
				# todo: How can we get viewer in this callback??? Just using self.viewer
				self.editLabel(layer, event)
							
##############################################################################
if __name__ == '__main__':

	# todo: add argparse for command line
	
	parser = argparse.ArgumentParser(description = 'Process 2 channel hcn1 and vascular files into edt')
	parser.add_argument('tifPath', nargs='*', default='', help='path to original _ch1 .tif file')
	args = parser.parse_args() # args is a list of command line arguments

	if len(args.tifPath)>0:
		pathToRawTiff = args.tifPath[0]		
	else:
		#pathToRawTiff = '/Users/cudmore/box/data/nathan/20200116/20190116__A01_G001_0007_ch1.tif'
		#pathToRawTiff = '/Users/cudmore/box/data/nathan/20200116/20190116__A01_G001_0010_ch1.tif'
		#pathToRawTiff = '/Users/cudmore/box/data/nathan/20200116/20190116__A01_G001_0011_ch1.tif'

		pathToRawTiff = '/Users/cudmore/box/data/nathan/20200116/20190116__A01_G001_0014_ch1.tif'
		pathToRawTiff = '/Users/cudmore/box/data/nathan/20200518/20200518__A01_G001_0003_ch2.tif'
		
		masterFilePath = 'aicsBatch/20200717_cell_db.csv'
		pathToRawTiff = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0014_ch2.tif'
		
	if 0:
		# one file, this can work without masterFilePath
		myLabelEdit(pathToRawTiff, masterFilePath)
	
	if 1:
		# step through master db
		# we need folder and channel to recreate path to each file from master db !!!
		folderPath = '/Volumes/ThreeRed/nathan/20200717'
		channel = 2
		pathToRawTiff = ''
		myLabelEdit(pathToRawTiff, masterFilePath, folderPath=folderPath, channel=2)
	
	
	
	
	