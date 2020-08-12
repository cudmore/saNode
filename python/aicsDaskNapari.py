"""
20200806
"""

import os

from collections import OrderedDict

import numpy as np

import tifffile

import dask
import dask.array as da

import napari

def getSnakeGrid(gridShape):
	"""
	make nRow X nCol grid of snaked integers
	
	e.g.:
		0 1 2 3 4
		9 8 7 6 5
	"""
	nRow = gridShape[0]
	nCol = gridShape[1]
	
	# make nRow X nCol grid of integers
	tmpIntegerGrid = np.arange(1,nRow*nCol+1) # Values are generated within the half-open interval [start, stop)
	tmpIntegerGrid = np.reshape(tmpIntegerGrid, (nRow, nCol))
	# reverse numbers in every other row (to replicate 'snake' image acquisition)
	integerGrid = tmpIntegerGrid.copy()
	integerGrid[1::2] = tmpIntegerGrid[1::2,::-1]

	return integerGrid
	
def myFileRead(filePath,commonShape):
	"""
	File loading triggered from dask from_delayed and delayed
	handle missing files in dask array by returning correct shape
	"""
	if os.path.isfile(filePath):
		stackData = tifffile.imread(filePath)
	else:
		stackData = np.zeros(commonShape, dtype=np.uint8)

	return stackData

def myGetBlock(aicsGridParam, channel, finalPostfixStr):
	"""
	One block/grid for each file (_ch2.tif, ch2_masked.tif, ...)
	
	finalPostfixStr: something like '', '_mask', etc
	
	"""
	gridShape = aicsGridParam['gridShape']
	nRow = gridShape[0]
	nCol = gridShape[1]
	commonShape = aicsGridParam['commonShape']
	
	common_dtype = np.uint8
	
	integerGrid = getSnakeGrid(gridShape)
	print('integerGrid:', integerGrid)

	if channel == 1:
		postfixStr = '_ch1' + finalPostfixStr + '.tif'
	elif channel == 2:
		postfixStr = '_ch2' + finalPostfixStr + '.tif'
	elif channel == 3:
		postfixStr = '_ch3' + finalPostfixStr + '.tif'
	else:
		print('error: aicsDaskNapari() got bad channel:', channel)

	# make a list of file names following order of snake pattern in integerGrid
	filenames = [prefixStr + str(x).zfill(4) + postfixStr for x in integerGrid.ravel()]
	filenames = [os.path.join(path, x) for x in filenames]
	
	print('channel:', channel, 'filenames:')
	for file in filenames:
		print('  ', file)

	lazyArray = []
	for file in filenames:
		thisOne0 = dask.delayed(myFileRead)(file, commonShape)
		thisOne1 = da.from_delayed(thisOne0, shape=commonShape, dtype=common_dtype)
		lazyArray.append(thisOne1)
	# reshape 1d list into list of lists (nCol items list per nRow lists)
	lazyArray = [lazyArray[i:i+nCol] for i in range(0, len(lazyArray), nCol)]
	
	#for oneLazy in lazyArray:
	#	print('oneLazy:', oneLazy)

	# make a block
	x = da.block(lazyArray)
	
	return x
	
def aicsDaskNapari(aicsGridParam):
	"""
	folderPath: path to aicsAnalysis/ folder
	gridShape: (rows, col)
	
	notes:
		The aicsAnalysis/ folder .tif files are already trimmed
	"""

	path = aicsGridParam['path']
	prefixStr = aicsGridParam['prefixStr']
	channelList = aicsGridParam['channelList'] # makes postfics str
	commonShape = aicsGridParam['commonShape']
	commonVoxelSize = aicsGridParam['commonVoxelSize']
	gridShape = aicsGridParam['gridShape']
	finalPostfixList = aicsGridParam['finalPostfixList']

	rawBlockList = []
	napariChannelList = []
	napariPostfixList = []
	for channel in channelList:
		for finalPostfixStr in finalPostfixList:
			print('calling myGetBlock() channel:', channel, 'finalPostfixStr:', finalPostfixStr)
			rawBlock = myGetBlock(aicsGridParam, channel=channel, finalPostfixStr=finalPostfixStr)
			rawBlockList.append(rawBlock)
			napariChannelList.append(channel)
			napariPostfixList.append(finalPostfixStr)

	print('aicsDaskNapari() opening in Napari, grid size:', gridShape, ' please wait ...')
	# for napari
	tmpPath, windowTitle = os.path.split(path)
	scale = commonVoxelSize

	with napari.gui_qt():
		viewer = napari.Viewer(title='dask: ' + windowTitle)

		for idx, rawBlock in enumerate(rawBlockList):
			print(idx+!, 'of', len(rawBlockList), 'blocks')
			channelIdx = napariChannelList[idx]
			if channelIdx == 1:
				color = 'green'
			elif channelIdx == 2:
				color = 'red'
			thisPostfix = napariPostfixList[idx]
			minContrast = 0
			maxContrast = 255
			if thisPostfix in ['_mask']:
				minContrast = 0
				maxContrast = 1
				#
				# blank out mask slices when raw has low snr, where snr=max-min
				# this does not work, this gets min/max of ENTIRE grid
				theMin = rawBlockList[idx-1].min().compute()
				theMax = rawBlockList[idx-1].max().compute()
				print(rawBlockList[idx-1].shape, 'theMin:', theMin, 'theMax:', theMax)
				
			'''
			if thisPostfix == 'finalMask_edt':
				minContrast = 0
				maxContrast = 120
				color = 'fire'
			'''
			name = 'ch' + str(channelIdx) + ' ' + str(thisPostfix)
			myImageLayer = viewer.add_image(rawBlock, scale=scale, colormap=color,
						contrast_limits=(minContrast, maxContrast), opacity=0.6, visible=True,
						name=name)
		print('should be open?')
		
if __name__ == '__main__':

	
	path = '/Volumes/ThreeRed/nathan/20200717/aicsAnalysis'
	prefixStr = '20200717__A01_G001_'
	commonShape = (88,740,740)
	commonVoxelSize = (1, 0.3977476, 0.3977476)
	channelList = [1,2]
	gridShape = (11,4)
	finalPostfixList = ['', '_mask']
	
	aicsGridParam = OrderedDict()
	aicsGridParam['path'] = path
	aicsGridParam['prefixStr'] = prefixStr
	aicsGridParam['commonShape'] =  commonShape# shape of each stack in aicsAnalysis (already trimmed)
	aicsGridParam['commonVoxelSize'] = commonVoxelSize
	aicsGridParam['channelList'] = channelList
	aicsGridParam['gridShape'] = gridShape
	aicsGridParam['finalPostfixList'] = finalPostfixList
	
	aicsDaskNapari(aicsGridParam)