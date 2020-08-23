import os, sys, time, glob, logging

from collections import OrderedDict

import numpy as np

import napari

import bimpy

def aicsOneNapari(path, channels=[1,2]):
	"""
	path: path to vasc raw stack
		e.g.: /Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0014_ch2.tif
		
	path to analysisAics/ folder'
	"""
	
	print('oneNapari() path:', path)
		
	rawPath, rawFile = os.path.split(path)
	rawFileNoExtension, tmpExtension = rawFile.split('.')
	
	analysisFolder = os.path.join(rawPath, 'aicsAnalysis')
	
	# 2 channels
	rawBaseName = rawFileNoExtension.replace('_ch1', '')
	rawBaseName = rawBaseName.replace('_ch2', '')
	#channels = [1,2]
	theseStacks = ['', '_filtered', '_mask', '_labeled', '_labeled_removed']
	theseStacks = ['', '_mask', '_labeled', '_labeled_removed']
	
	myNapariDict = OrderedDict()
	myNapariDict['path'] = None
	myNapariDict['channel'] = None
	myNapariDict['data'] = None
	myNapariDict['name'] = None
	myNapariDict['type'] = None # from (raw, mask, label)
	
	myNapariList = []
	
	for channel in channels:
		chStr = 'ch' + str(channel)
		for thisStack in theseStacks:
			thisFile = rawBaseName + '_' + chStr + thisStack + '.tif'
			thisPath = os.path.join(analysisFolder, thisFile)
			thisType = 'unknown'
			if thisStack in ['', '_filtered']:
				thisType = 'raw'
			elif thisStack == '_mask':
				thisType = 'mask'
			elif thisStack.startswith('_labeled'):
				thisType = 'labeled'
			
			#print(channel, thisStack, thisPath)
			
			if os.path.isfile(thisPath):
				#
				stackData, tiffHeader0 = bimpy.util.bTiffFile.imread(thisPath)
				#
				
				if thisType == 'raw':
					tiffHeader = tiffHeader0
				
				myNapariDict = myNapariDict.copy() # IMPORTANT
				myNapariDict['path'] = thisPath
				myNapariDict['channel'] = channel
				myNapariDict['data'] = stackData
				myNapariDict['name'] = chStr + thisStack
				myNapariDict['type'] = thisType
				
				print('  loaded myNapariDict:', myNapariDict['name'], myNapariDict['type'], myNapariDict['path'])

				myNapariList.append(myNapariDict)
			else:
				print('aicsOneNapari() did not find file:', thisPath)
				
	xVoxel = tiffHeader['xVoxel']
	yVoxel = tiffHeader['yVoxel']
	zVoxel = tiffHeader['zVoxel']
	
	#
	# get label and count for final labels (which then make mask)
	# visually inspect results and see if we need to increase 'removeSmallLabels'
	'''
	uniqueOrig, countsOrig = np.unique(labeledData, return_counts=True)
	origNumLabels = len(uniqueOrig)
	myPrettyPrint = np.asarray((uniqueOrig, countsOrig)).T
	print(myPrettyPrint)
	'''
	
	scale = (zVoxel, xVoxel, yVoxel)
	with napari.gui_qt():
		titleStr = 'aicsOneNapari:' + path
		viewer = napari.Viewer(title=titleStr)
	
		blending = 'additive'
		
		for oneNapari in myNapariList:
			data = oneNapari['data']
			channel = oneNapari['channel']
			name = oneNapari['name']
			type = oneNapari['type'] # from (raw, mask, labeled)
		
			opacity = 1.0
			visible = True
			
			if channel == 1:
				colormap = 'green'
			elif channel == 2:
				colormap = 'red'
				colormap = 'gray'
			
			if type in ['raw', 'filtered']:
				minContrast = 0
				maxContrast = 180
				myImageLayer = viewer.add_image(data, scale=scale, contrast_limits=(minContrast, maxContrast),
						blending=blending, opacity=opacity, colormap=colormap, visible=True, name=name)
			elif type == 'mask':
				if channel == 1:
					colormap = 'blue'
				elif channel == 2:
					colormap = 'magenta'
				minContrast = 0
				maxContrast = 1
				opacity = 0.6
				myImageLayer = viewer.add_image(data, scale=scale, contrast_limits=(minContrast, maxContrast),
						blending=blending, opacity=opacity, colormap=colormap, visible=visible, name=name)
			elif type == 'labeled':
				visible = False
				myImageLayer = viewer.add_labels(data, scale=scale,
								blending=blending, opacity=opacity, visible=visible, name=name)
						
if __name__ == '__main__':
	path = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0014_ch2.tif'
	path = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0014_ch1.tif'
	
	channels = [2]
	aicsOneNapari(path, channels=channels)
	
	
	