"""
A browser to show all stacks in grid and select first/last slice

Keyboard:
	'n' : next file
	'p' : previous file
	'f' : set first slice
	'l' : set last slice
	's': save .csv
"""

import os
from collections import OrderedDict

import napari

import bimpy

import aicsUtil

def _getChannelStr(channel):
	if channel == 1:
		chStr = '_ch1'
	elif channel == 2:
		chStr = '_ch2'
	return chStr
	
def getFileList(path, channel):
	"""
	Get all .tif files with _ch1 or _ch2
	"""
	
	chStr = _getChannelStr(channel)

	fileList = []
	limitFileNum = None #None #20
	numFiles = 0
	for file in os.listdir(path):
		filePath = os.path.join(path, file)
		
		if chStr in file and file.endswith('.tif'):
			fileList.append(filePath)
			numFiles += 1
			if limitFileNum is not None and numFiles > limitFileNum:
				print('REMEMBER LIMITING FILES TO limitFileNum:', limitFileNum)
				break
	return fileList
	
#def myLoadTiff(path, uFirstSlice, uLastSlice):
#	pass
	
def aicsSelectSlices(masterFilePath, path, removePrefix, channel):
	"""
	path: aicsAnalysis/ ... REMEMBER ... ONLY contains files we analyzed
	"""
	fileList = getFileList(path, channel)
	
	'''
	for file in fileList:
		print('file:', file)
	'''
	
	chStr = _getChannelStr(channel)

	theseFileType = ['', '_mask', '_labeled']
	theseFileType = ['', '_mask']
	
	numLayersPerFile = len(theseFileType)
	
	#
	# load all files
	print('loading files ...')

	# todo: fix this, I am fetching all file names from original raw folder
	# aicsAnalysis/ only has files analyzed with uInclude, we want rows to align with cell_db.csv
	fullFileList = getFileList(path + '/..', channel)
	rawDataNameDict = OrderedDict() # corresponds to Tiff files in cell_db.csv
	for file in fullFileList:
		tmpFolder, tmpFile = os.path.split(file)
		rawNameBase, tmpExt = tmpFile.split('.')
		tmpFileNameNoExtension = rawNameBase.replace('_ch1', '')
		tmpFileNameNoExtension = tmpFileNameNoExtension.replace('_ch2', '')
		#print('adding key:', tmpFileNameNoExtension)
		# corresponds to Tiff files in cell_db.csv
		rawDataNameDict[tmpFileNameNoExtension] = OrderedDict({'uFirstSlice':'', 'uLastSlice':'', 'uNumSlices':''})
	print('rawDataNameDict() has', len(rawDataNameDict.keys()), 'keys (e.g. files)')
	
	stackDataList = []
	stackNameList = []
	numLoaded = 0
	for file in fileList:
		if file.endswith(chStr + '.tif'):
			pass
		else:
			continue
		
		# make a dict() with all raw data files, regardless of uInclude
		# this keeps rows in sync with master cell_db.csv
		tmpFolder, tmpFile = os.path.split(file)
		rawNameBase, tmpExt = tmpFile.split('.')
		#rawNameBase, tmpExt = os.path.splitext(file)
		#rawDataName = rawNameBase.replace('_ch1', '')
		#rawDataName = rawDataName.replace('_ch2', '')
		tmpFileNameNoExtension = rawNameBase.replace('_ch1', '')
		tmpFileNameNoExtension = tmpFileNameNoExtension.replace('_ch2', '')
		
		'''
		print('adding key:', tmpFileNameNoExtension)
		rawDataNameDict[tmpFileNameNoExtension] = OrderedDict({'uFirstSlice':'', 'uLastSlice':''}) # corresponds to Tiff files in cell_db.csv
		'''
		
		uFile, uInclude, uFirstSlice, uLastSlice = aicsUtil.parseMasterFile(masterFilePath, file)
		if not uInclude:
			continue
		else:
			#print('  include:', file)
			pass
			
		# fill in rawDataNameDict
		print('*** aicsSelectSlices() uFile:', uFile, 'uFirstSlice:', uFirstSlice, 'uLastSlice:', uLastSlice)
		if uFirstSlice is not None:
			rawDataNameDict[uFile]['uFirstSlice'] = uFirstSlice
		if uLastSlice is not None:
			rawDataNameDict[uFile]['uLastSlice'] = uLastSlice
					
		for thisFileType in theseFileType:
			#thisPostfix = thisFileType + '.tif' # load (raw, mask, etc)
			loadThisFile = rawNameBase + thisFileType + '.tif'
			loadThisFile = os.path.join(tmpFolder, loadThisFile)
			#print('loadThisFile:', loadThisFile)
			if os.path.isfile(loadThisFile):
				#print(file)
				#stackData, tiffHeader = myLoadTiff(loadThisFile, uFirstSlice, uLastSlice)
				stackData, tiffHeader = bimpy.util.bTiffFile.imread(loadThisFile)
				stackDataList.append(stackData)
				
				# todo: this is way to complicated for what it does
				#print('loadThisFile:', loadThisFile)
				thisStackName = os.path.splitext(loadThisFile)[0] # remove .tif
				thisStackName = os.path.split(thisStackName)[1] # get name
				thisStackName = thisStackName.replace(removePrefix, '') # remove Olympus prefix
				thisStackName = thisStackName.replace('_ch1', '')
				thisStackName = thisStackName.replace('_ch2', '')
				stackNameList.append(thisStackName)
				numLoaded += 1
			
	print('  loaded', numLoaded, 'files')
	
	'''
	for k in enumerate(rawDataNameDict.keys()):
		print('rawDataNameDict:', k)
	'''
	
	# reverse for napari (first add_image shows up last in napari interface)
	stackDataList.reverse()
	stackNameList.reverse()
	
	'''
	for idx, stackName in enumerate(stackNameList):
		print(idx, 'stackName:', stackName)
	'''
	
	'''
	for idx, stackName in enumerate(rawDataNameList):
		print(idx, 'rawDataNameList:', stackName)
	'''
	
	#
	# open in Napari
	print('opening napari ...')
	scale = (1,1,1)
	numLayers = 0
	with napari.gui_qt():
		titleStr = 'aicsSelectSlices:' + path
		viewer = napari.Viewer(title=titleStr)
	
		blending = 'additive'
		opacity = 0.6
		visible = False
		
		for idx, stackData in enumerate(stackDataList):
			stackName = stackNameList[idx]
			
			stackType = 'raw'
			minContrast = 0
			maxContrast = 180
			colormap = 'gray'
			opacity = 1
			if stackName.endswith('_mask'):
				stackType = 'mask'
				colormap = 'cyan'
				minContrast = 0
				maxContrast = 1
				opacity = 0.6
			elif stackName.endswith('_labeled'):
				stackType = 'labeled'
				opacity = 0.6
				
			if stackType in ['raw', 'mask']:
				myImageLayer = viewer.add_image(stackData, scale=scale, contrast_limits=(minContrast, maxContrast),
						blending=blending, opacity=opacity, colormap=colormap, visible=visible, name=stackName)
				numLayers += 1
			elif stackType in ['labeled']:
				myImageLayer = viewer.add_labels(stackData, scale=scale,
								blending=blending, opacity=opacity, visible=visible, name=stackName)
				numLayers += 1
			
		print('  added', numLayers, 'layers')
		
		# select the first layer
		selectOneLayer(viewer, -1)
		# turn it on
		tmpName, tmpIdx = getSelectedLayer(viewer)
		toggleLayer(viewer, tmpName, True)
		#
		# adding functions to set 'first' and 'last' slice
		@viewer.bind_key('f')
		def setFirstSlice(viewer):
			setFirstLastSlice(viewer, 'uFirstSlice', rawDataNameDict)
			
		@viewer.bind_key('l')
		def setLastSlice(viewer):
			setFirstLastSlice(viewer, 'uLastSlice', rawDataNameDict)
			
		@viewer.bind_key('p')
		def nextFile(viewer):
			nextPreviousFile(viewer, 'previous', numLayersPerFile)

		@viewer.bind_key('n')
		def nextFile(viewer):
			nextPreviousFile(viewer, 'next', numLayersPerFile)
		
		@viewer.bind_key('s')
		def saveFile(viewer):
			mySave(masterFilePath, rawDataNameDict)
	
def mySave(masterFilePath, rawDataNameDict):
	basePath, tmpExt = os.path.splitext(masterFilePath)
	savePath = basePath + '_first_last.csv'
	
	print('savePath:', savePath)
	
	headerStr = 'file,uFirstSlice,uLastSlice,uNumSlices' + os.linesep # add an EOL
	
	lines = [headerStr]
	for k1, v1 in rawDataNameDict.items():
		# k1 is file name
		lineStr = k1 + ','
		for k2, v2 in v1.items():
			# v2 is value of (uFirst, uLast)
			lineStr += str(v2) + ','
		lineStr = lineStr[0:-1] # remove last comma
		lineStr += os.linesep # add an EOL
		#print(lineStr) 
		lines.append(lineStr)
	with open(savePath, 'w') as f:
		f.writelines(lines)
			
def setFirstLastSlice(viewer, doThis, rawDataNameDict):
	"""
	doThis: (firstSlice, lastSlice)
	"""
	mySlice = viewer.dims.point[0] # get the slice
	layerName, layerIdx = getSelectedLayer(viewer)
	layerName = layerName.replace('_mask', '')
	
	# cell_db.csv does not have any channels
	layerName = layerName.replace('_ch1', '')
	layerName = layerName.replace('_ch2', '')	
	filename = removePrefix + layerName
	
	if viewer.layers[layerIdx].visible == False:
		print('Warning: Can not setFirstLastSlice for non visible layer')
	else:
		#print(doThis, filename, mySlice)
		rawDataNameDict[filename][doThis] = mySlice
		
		'''
		for k, v in rawDataNameDict.items():
			print(k, v)
		'''
		
		# update uNumSlices
		uFirstSlice = rawDataNameDict[filename]['uFirstSlice']
		uLastSlice = rawDataNameDict[filename]['uLastSlice']
		uNumSlices = rawDataNameDict[filename]['uNumSlices']
		if uFirstSlice and uLastSlice:
			if uFirstSlice>=0 and uLastSlice>=0:
				uNumSlices = uLastSlice - uFirstSlice + 1
				rawDataNameDict[filename]['uNumSlices'] = uNumSlices
		
		#
		print('setFirstLast() filename:', filename, 'uFirstSlice:', uFirstSlice, 'uLastSlice:', uLastSlice, 'uNumSlices:', uNumSlices)
	
	
def nextPreviousFile(viewer, doThis, numLayersPerFile):
	"""
	doThis: (next, previous)
	"""
	selectedLayerName, selectedLayerIdx = getSelectedLayer(viewer)
	rawLayerName = selectedLayerName.replace('_mask', '')
	print('rawLayerName:', rawLayerName, 'selectedLayerIdx:', selectedLayerIdx)

	# turn on next
	selectedLayerIdx = findLayerIdx(viewer, rawLayerName)
	
	if doThis == 'next':
		selectedLayerIdx -= numLayersPerFile
	elif doThis == 'previous':
		selectedLayerIdx += numLayersPerFile
	
	# bound
	if (selectedLayerIdx<0) or (selectedLayerIdx > len(viewer.layers)-1):
		return
	
	# turn off current
	#print('turning off', rawLayerName, 'selectedLayerIdx:', selectedLayerIdx)
	#toggleLayer(viewer, rawLayerName, False)
	print('turning off all layers')
	for layer in viewer.layers:
		layer.visible = False
		
	# turn on next
	rawLayerName = viewer.layers[selectedLayerIdx].name
	print('turning on', rawLayerName, 'selectedLayerIdx:', selectedLayerIdx)
	toggleLayer(viewer, rawLayerName, True)

	# select next
	selectOneLayer(viewer, selectedLayerIdx)

def getSelectedLayer(viewer):
	name = None
	idx = None
	for i, layer in enumerate(viewer.layers):
		if layer.selected:
			name = layer.name
			idx = i
			break
	return name, idx
		
def selectOneLayer(viewer, layerIdx):
	# turn all off
	for layer in viewer.layers:
		if layer.selected:
			layer.selected = False
	viewer.layers[layerIdx].selected = True
	
def findLayerIdx(viewer, thisLayerName):
	retIdx = None
	for idx, layer in enumerate(viewer.layers):
		if layer.name == thisLayerName:
			retIdx = idx
			break
	return retIdx
		
def toggleLayer(viewer, thisLayerName, isVisible):
	for layer in viewer.layers:
		if thisLayerName in layer.name:
			layer.visible = isVisible
		
########################################################
if __name__ == '__main__':

	masterFilePath = 'aicsBatch/20200717_cell_db.csv'
	path = '/Volumes/ThreeRed/nathan/20200717/aicsAnalysis'
	removePrefix = '20200717__A01_G001_'
	channel = 2
	
	aicsSelectSlices(masterFilePath, path, removePrefix, channel)