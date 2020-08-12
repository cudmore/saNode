"""
A browser to show all stacks in grid and select first/last slice
"""

import os

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

	chStr = _getChannelStr(channel)

	fileList = []
	for file in os.listdir(path):
		filePath = os.path.join(path, file)
		
		if chStr in file:
			fileList.append(filePath)
	
	return fileList
	
def aicsSelectSlices(masterFilePath, path, channel):
	"""
	"""
	fileList = getFileList(path, channel)
	
	'''
	for file in fileList:
		print(file)
	'''
	
	chStr = _getChannelStr(channel)

	theseFileType = ['', '_mask', '_labeled']
	
	#
	# load all files
	print('loading files ...')
	stackDataList = []
	stackNameList = []
	for file in fileList:
		if file.endswith(chStr + '.tif'):
			pass
		else:
			continue
		
		uInclude, uFirstSlice, uLastSlice = aicsUtil.parseMasterFile(masterFilePath, file)
		if not uInclude:
			continue
		else:
			#print('  include:', file)
			pass
			
		tmpFolder, tmpFile = os.path.split(file)
		tmpFileNameNoExtension, tmpExt = tmpFile.split('.')
		for thisFileType in theseFileType:
			#thisPostfix = thisFileType + '.tif' # load (raw, mask, etc)
			thisFileBase = tmpFileNameNoExtension + thisFileType
			thisFileName = thisFileBase + '.tif'
			loadThisFile = os.path.join(tmpFolder, thisFileName)
			#if file.endswith(thisPostfix):
			if os.path.isfile(loadThisFile):
				#print(file)
				stackData, tiffHeader = bimpy.util.bTiffFile.imread(loadThisFile)
				stackDataList.append(stackData)
				
				removePrefix = '20200717__A01_G001_'
				thisStackName = thisFileBase.replace(removePrefix, '')
				stackNameList.append(thisStackName)
	
	# reverse for napari (first add_image shows up last in napari interface)
	stackDataList.reverse()
	stackNameList.reverse()
	
	'''
	for idx, stackName in enumerate(stackNameList):
		print(idx, 'stackName:', stackName)
	'''
	
	scale = (1,1,1)
	
	print('opening napari ...')
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
			elif stackType in ['labeled']:
				myImageLayer = viewer.add_labels(stackData, scale=scale,
								blending=blending, opacity=opacity, visible=visible, name=stackName)
			
if __name__ == '__main__':

	masterFilePath = 'aicsBatch/20200717_cell_db.csv'
	path = '/Volumes/ThreeRed/nathan/20200717/aicsAnalysis'
	channel = 2
	
	aicsSelectSlices(masterFilePath, path, channel)