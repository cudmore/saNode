"""
20200806
"""

import os

from collections import OrderedDict

import numpy as np
import pandas as pd

import tifffile

import dask
import dask.array as da

import napari

import aicsUtil

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
	
# used for dask (degraded)
def myFileRead(filePath, commonShape, uFirstSlice=None, uLastSlice=None):
	"""
	File loading triggered from dask from_delayed and delayed
	handle missing files in dask array by returning correct shape
	
	todo: use commot type rather than hard coding dtype=np.uint8
	"""
	
	#print('x myFileRead() path:', filePath)
	if os.path.isfile(filePath):
		stackData = tifffile.imread(filePath)
		
		'''
		if '_ch1' in filePath:
			# don't crop
			pass
		else:			
			if uFirstSlice is not None and uLastSlice is not None:
				stackData[0:uFirstSlice-1, :, :] = 0
				stackData[uLastSlice+1:-1, :, :] = 0
		'''
		
	else:
		# all dtype in grid have to be the same
		stackData = np.zeros(commonShape, dtype=np.uint8)

	# convert masks to binary/bool_
	if filePath.endswith('_mask.tif'):
		#print('myFileRead() bool_', filePath)
		stackData = stackData.astype(np.bool_)

	return stackData

# used for dask (degraded)
def myFileRead0(filePath, commonShape, dtype=np.uint8, uFirstSlice=None, uLastSlice=None):
	"""
	File loading triggered from dask from_delayed and delayed
	handle missing files in dask array by returning correct shape
	
	todo: use commot type rather than hard coding dtype=np.uint8
	"""
	
	#print('x myFileRead() path:', filePath)
	if os.path.isfile(filePath):
		stackData = tifffile.imread(filePath)
		stackData = stackData.astype(dtype)
		'''
		if '_ch1' in filePath:
			# don't crop
			pass
		else:			
			if uFirstSlice is not None and uLastSlice is not None:
				stackData[0:uFirstSlice-1, :, :] = 0
				stackData[uLastSlice+1:-1, :, :] = 0
		'''
		
	else:
		# all dtype in grid have to be the same
		stackData = np.zeros(commonShape, dtype=dtype)

	# convert masks to binary/bool_
	'''
	if filePath.endswith('_mask.tif'):
		#print('myFileRead() bool_', filePath)
		stackData = stackData.astype(np.bool_)
	'''
	
	return stackData

def myGetBlock(aicsGridParam, channel, finalPostfixStr):
	"""
	One block/grid for each file (_ch2.tif, ch2_masked.tif, ...)
	
	finalPostfixStr: something like '', '_mask', etc
	
	"""
	masterFilePath = aicsGridParam['masterFilePath']
	gridShape = aicsGridParam['gridShape']
	nRow = gridShape[0]
	nCol = gridShape[1]
	commonShape = aicsGridParam['commonShape']
	
	#common_dtype = np.uint8 # set to bool_ for masks
	
	#
	integerGrid = getSnakeGrid(gridShape)
	print('myGetBlock() channel:', channel, 'finalPostfixStr:', finalPostfixStr, 'integerGrid:')
	print(integerGrid)

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
	
	useMasterFile = False
	if os.path.isfile(masterFilePath):
		# load
		useMasterFile = True
		dfMasterFile = pd.read_csv(masterFilePath)
		
	'''
	print('myGetBlock() channel:', channel, 'filenames:')
	for file in filenames:
		print('  ', file)
	'''
	
	'''
	lazyArray = []
	uFirstSlice = None
	uLastSlice = None
	for file in filenames:
		print('xxx file:', file)
		# file is full path
		# parse
		if useMasterFile:
			# todo: this needs to be way better organized
			fileNoPostfix = file.replace(postfixStr, '')
			fileNoPostfix += '.tif'
			uFile, uInclude, uFirstSlice, uLastSlice = aicsUtil.parseMasterFile('', fileNoPostfix, dfMasterFile=dfMasterFile)

		thisOne0 = dask.delayed(myFileRead)(file, commonShape, uFirstSlice=uFirstSlice, uLastSlice=uLastSlice)
		thisOne0 = da.from_delayed(thisOne0, shape=commonShape, dtype=common_dtype)
		lazyArray.append(thisOne0)
	# reshape 1d list into list of lists (nCol items list per nRow lists)
	lazyArray = [lazyArray[i:i+nCol] for i in range(0, len(lazyArray), nCol)]
		
	#for oneLazy in lazyArray:
	#	print('oneLazy:', oneLazy)

	# make a block
	x = da.block(lazyArray)
	
	# was this
	return x
	'''
	
	#
	# sat 20200815
	#
	# try to load everything into big ndarray
	big_dtype = np.uint8
	if finalPostfixStr == '_mask':
		big_dtype = np.bool_
	bigSlices = commonShape[0]
	bigRows = nRow * commonShape[1]
	bigCols = nCol * commonShape[2]
	bigShape = (bigSlices, bigRows, bigCols)
	print('making bigStack')
	bigStack = np.zeros(bigShape, dtype=big_dtype) # set to np.bool_ for masks
	print('bigStack.shape:', bigStack.shape, bigStack.dtype)
	fileIdx = 0
	for row in range(nRow):
		rowStart = row * commonShape[1]
		rowStop = rowStart + commonShape[1]
		for col in range(nCol):
			colStart = col * commonShape[2]
			colStop = colStart + commonShape[2]
			
			uFirstSlice = None
			uLastSlice = None
			
			file = filenames[fileIdx]
			if useMasterFile:
				# todo: this needs to be way better organized
				fileNoPostfix = file.replace(postfixStr, '')
				fileNoPostfix += '.tif'
				uFile, uInclude, uFirstSlice, uLastSlice = aicsUtil.parseMasterFile('', fileNoPostfix, dfMasterFile=dfMasterFile)
			oneBigData = myFileRead0(file, commonShape, dtype=big_dtype, uFirstSlice=uFirstSlice, uLastSlice=uLastSlice)
			
			bigStack[:,rowStart:rowStop, colStart:colStop] = oneBigData
			
			fileIdx += 1

	return bigStack
	
def aicsDaskNapari(aicsGridParam):
	"""
	folderPath: path to aicsAnalysis/ folder
	gridShape: (rows, col)
	
	notes:
		The aicsAnalysis/ folder .tif files are already trimmed
	"""

	masterFilePath = aicsGridParam['masterFilePath'] # 20200814, not used
	path = aicsGridParam['path']
	prefixStr = aicsGridParam['prefixStr']
	channelList = aicsGridParam['channelList'] # makes postfics str
	commonShape = aicsGridParam['commonShape']
	commonVoxelSize = aicsGridParam['commonVoxelSize']
	gridShape = aicsGridParam['gridShape']
	finalPostfixList = aicsGridParam['finalPostfixList']

	# todo: load master file one into df an dpass to other functions (or append to aicsGriddParams?
		
	rawBlockList = []
	napariChannelList = []
	napariPostfixList = []

	'''
	# make one slice with white grid
	myWhiteGrid = np.ones((1,500,500), dtype=np.bool_)
	rawBlockList.append(myWhiteGrid)
	napariChannelList.append(3)
	napariPostfixList.append('_grid')
	'''
	
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
			print('  ', idx+1, 'of', len(rawBlockList), 'blocks', rawBlock.dtype)
			channelIdx = napariChannelList[idx]
			color = 'gray'
			blending = 'additive'
			opacity = 1.0
			if channelIdx == 1:
				color = 'green'
			elif channelIdx == 2:
				color = 'red'
			thisPostfix = napariPostfixList[idx]
			minContrast = 0
			maxContrast = 255
			if thisPostfix in ['_mask', '_grid']:
				minContrast = 0
				maxContrast = 1
				#
				# blank out mask slices when raw has low snr, where snr=max-min
				# this does not work, this gets min/max of ENTIRE grid
				'''
				theMin = rawBlockList[idx-1].min().compute()
				theMax = rawBlockList[idx-1].max().compute()
				print(rawBlockList[idx-1].shape, 'theMin:', theMin, 'theMax:', theMax)
				'''
			'''
			if thisPostfix == 'finalMask_edt':
				minContrast = 0
				maxContrast = 120
				color = 'fire'
			'''
			name = 'ch' + str(channelIdx) + ' ' + str(thisPostfix)
			myImageLayer = viewer.add_image(rawBlock, scale=scale, colormap=color,
						contrast_limits=(minContrast, maxContrast), opacity=opacity, blending=blending, visible=True,
						name=name)
		
		# add grid of stack square
		triangle = np.array([[11, 13], [111, 113], [22, 246]])
		polygons = [triangle]
		shapeLayer = viewer.add_shapes(polygons, shape_type='polygon', edge_width=5,
                              edge_color='coral', face_color='royalblue')
                              
		@viewer.mouse_drag_callbacks.append
		def viewerMouseDrag(viewer, event):
			print('viewerMouseDrag() viewer:', viewer, 'event:', event)

		#
		print('should be open?')
		
if __name__ == '__main__':

	
	masterFilePath = 'aicsBatch/20200717_cell_db.csv'
	path = '/Volumes/ThreeRed/nathan/20200717/aicsAnalysis0'
	path = '/Users/cudmore/Desktop/aicsAnalysis0'
	prefixStr = '20200717__A01_G001_'
	commonShape = (88,740,740)
	commonVoxelSize = (1, 0.3977476, 0.3977476)
	channelList = [1,2]
	gridShape = (11,4)
	finalPostfixList = ['', '_mask']
	
	aicsGridParam = OrderedDict()
	aicsGridParam['masterFilePath'] = masterFilePath
	aicsGridParam['path'] = path
	aicsGridParam['prefixStr'] = prefixStr
	aicsGridParam['commonShape'] =  commonShape# shape of each stack in aicsAnalysis (already trimmed)
	aicsGridParam['commonVoxelSize'] = commonVoxelSize
	aicsGridParam['channelList'] = channelList
	aicsGridParam['gridShape'] = gridShape
	aicsGridParam['finalPostfixList'] = finalPostfixList
	
	aicsDaskNapari(aicsGridParam)