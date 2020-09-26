"""
20200815

View a grid of Tiff files in Napari

Keyboard:
	Shift-L: Turn count labels on/off (if on then can be slow)

"""

import os

import itertools # for itertools.product
from collections import OrderedDict

import numpy as np
import pandas as pd

import tifffile

import napari

import aicsUtil2 # does not import bimpy

############################################################
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

############################################################
def myFileRead0(filePath, commonShape, dtype=np.uint8, trimPercent=None, uFirstSlice=None, uLastSlice=None):
	"""
	File loading triggered from dask from_delayed and delayed
	handle missing files in dask array by returning correct shape

	todo: use commot type rather than hard coding dtype=np.uint8
	"""

	#print('x myFileRead() path:', filePath)
	if os.path.isfile(filePath):

		stackData = tifffile.imread(filePath)

		stackData = stackData.astype(dtype)

		if trimPercent is not None and trimPercent > 0:
			#print('myFileRead0() trimming', trimPercent, 'percent from', filePath)
			stackData = aicsUtil2.trimStack(stackData, trimPercent)

		'''
		if '_ch1' in filePath:
			# don't crop
			pass
		else:
			if uFirstSlice is not None and uLastSlice is not None:
				stackData[0:uFirstSlice-1, :, :] = 0
				stackData[uLastSlice+1:-1, :, :] = 0
		'''
		if uFirstSlice is not None and uLastSlice is not None:
			#print(f'  myFileRead0() cropping {uFirstSlice} {uLastSlice} {filePath}')
			stackData[0:uFirstSlice-1, :, :] = 0
			stackData[uLastSlice+1:-1, :, :] = 0

		# count pixels in first few labels
		'''
		if '_labeled' in filePath:
			print('  counting pixels in _labeled', filePath)
			maxLabel = np.max(stackData)
			print('    maxLabel:', maxLabel)

			labelCounts = np.bincount(np.ravel(stackData))

			#for i in range(1,maxLabel+1):
			for i, numPixels in enumerate(labelCounts):
				#numPixels = np.count_nonzero(stackData == i)
				if numPixels > 0:
					print('    label', i, numPixels)
		'''

	else:
		# bigStack in calling function already has all 0
		stackData = None
		'''
		# all dtype in grid have to be the same
		stackData = np.zeros(commonShape, dtype=dtype)
		'''
	# convert masks to binary/bool_
	'''
	if filePath.endswith('_mask.tif'):
		#print('myFileRead() bool_', filePath)
		stackData = stackData.astype(np.bool_)
	'''

	return stackData

############################################################
def getFileList(aicsParam, channel, finalPostfixStr, getAll=False):
	"""

	getAll: True will ignore masterFilePath (use to load all raw)
	"""

	path = aicsParam['path']
	masterFilePath = aicsParam['masterFilePath']
	prefixStr = aicsParam['prefixStr']
	gridShape = aicsParam['gridShape']
	doUseInclude = aicsParam['doUseInclude']

	useMasterFile = False
	dfMasterFile = None
	if os.path.isfile(masterFilePath):
		# load
		useMasterFile = True
		dfMasterFile = pd.read_csv(masterFilePath)

	if channel == 1:
		postfixStr = '_ch1' + finalPostfixStr + '.tif'
	elif channel == 2:
		postfixStr = '_ch2' + finalPostfixStr + '.tif'
	elif channel == 3:
		postfixStr = '_ch3' + finalPostfixStr + '.tif'
	else:
		print('error: getFileList() got bad channel:', channel)

	integerGrid = getSnakeGrid(gridShape) # m X n grid of snaked file indices 1,2,3,4, ... 8,7,6,5, ... ...
	aicsParam['snakeGrid'] = integerGrid

	# make a list of file names following order of snake pattern in integerGrid
	filenames = [prefixStr + str(x).zfill(4) + postfixStr for x in integerGrid.ravel()]
	filenames = [os.path.join(path, x) for x in filenames]

	finalFileList = []
	for file in filenames:
		uInclude = True
		if useMasterFile:
			# todo: this needs to be way better organized
			fileNoPostfix = file.replace(postfixStr, '')
			fileNoPostfix += '.tif'
			uFile, uInclude, uFirstSlice, uLastSlice = aicsUtil2.parseMasterFile('', fileNoPostfix, dfMasterFile=dfMasterFile)
		if not doUseInclude or uInclude:
			if os.path.isfile(file):
				finalFileList.append(file)
			else:
				# file not found, either postfix does not exist (like _mask)
				finalFileList.append(None)
		else:
			finalFileList.append(None)

	'''
	print('getFileList()')
	for file in finalFileList:
		print('  ', file)
	'''

	return finalFileList

def myGetBlock(aicsGridParam, channel, finalPostfixStr, getAll=False, smallDict=None):
	"""
	One block/grid for each file (_ch2.tif, ch2_masked.tif, ...)

	finalPostfixStr: something like '', '_mask', etc
	getAll: True will ignore masterFilePath (use to load all raw)

	todo: pass final dtype to load based on finalPostfixStr ('', '_mask', '_labeled', etc)
	"""

	dataPath = aicsGridParam['dataPath'] # used to save subset with smallDict
	masterFilePath = aicsGridParam['masterFilePath']
	gridShape = aicsGridParam['gridShape']
	nRow = gridShape[0]
	nCol = gridShape[1]
	commonShape = aicsGridParam['commonShape']
	trimPercent = aicsGridParam['trimPercent']
	doUseInclude = aicsGridParam['doUseInclude']
	doUseFirstLast = aicsGridParam['doUseFirstLast']

	#common_dtype = np.uint8 # set to bool_ for masks

	#
	'''
	integerGrid = getSnakeGrid(gridShape)
	print('myGetBlock() channel:', channel, 'finalPostfixStr:', finalPostfixStr, 'integerGrid:')
	print(integerGrid)
	'''

	if channel == 1:
		postfixStr = '_ch1' + finalPostfixStr + '.tif'
	elif channel == 2:
		postfixStr = '_ch2' + finalPostfixStr + '.tif'
	elif channel == 3:
		postfixStr = '_ch3' + finalPostfixStr + '.tif'
	else:
		print('error: myGetBlock() got bad channel:', channel)

	'''
	# make a list of file names following order of snake pattern in integerGrid
	filenames = [prefixStr + str(x).zfill(4) + postfixStr for x in integerGrid.ravel()]
	filenames = [os.path.join(path, x) for x in filenames]
	'''

	useMasterFile = False
	dfMasterFile = None
	if os.path.isfile(masterFilePath):
		# load
		useMasterFile = True
		dfMasterFile = pd.read_csv(masterFilePath)

	#
	# get list of files we will load, can be empty
	# getFileList() gives us files in snake order
	# none is either file not found or not in uInclude
	loadFileList = getFileList(aicsGridParam, channel, finalPostfixStr, getAll=getAll)

	# first time using all, see: https://stackoverflow.com/questions/6518394/how-to-check-if-all-items-in-the-list-are-none/6518435
	if all(v is None for v in loadFileList):
		# no files loaded
		return None

	# try to load everything into big ndarray
	big_dtype = np.uint8
	if finalPostfixStr == '_mask':
		big_dtype = np.bool_
	elif finalPostfixStr == '_labeled':
		big_dtype = np.uint16

	bigSlices = commonShape[0]
	bigRows = nRow * commonShape[1]
	bigCols = nCol * commonShape[2]
	bigShape = (bigSlices, bigRows, bigCols)
	print('      making bigStack shape:', bigShape, 'type:', big_dtype)
	bigStack = np.zeros(bigShape, dtype=big_dtype) # set to np.bool_ for masks

	#Head: 13 (20200811_SAN3_TOP)
	#Mid: 39  (20200811_SAN3_TOP)
	#Tail: 2 (20200814_SAN3_BOTTOM)
	'''
	smallDict = {
		'saveName': '0200811_SAN3_TOP_head', # will append _ch1/_ch2 to this
		'nRows': 3,
		'nCols': 3,
		'rowColIdxList': [(1,1), (1,2), (1,3),
					(2,1), (2,2), (2,3),
					(3,1), (3,2), (3,3),
					]
	}
	'''
	'''
	smallDict = {
		'saveName': '0200811_SAN3_TOP_mid', # will append _ch1/_ch2 to this
		'nRows': 3,
		'nCols': 3,
		'rowColIdxList': [(6,0), (6,1), (6,2),
					(7,0), (7,1), (7,2),
					(8,0), (8,1), (8,2),
					]
	}
	'''
	if smallDict is not None:
		smallRow = 0 # tells us position to save
		smallCol = 0
		smallShape = (bigSlices, smallDict['nRows']*commonShape[1], smallDict['nCols']*commonShape[2])
		smallStack = np.zeros(smallShape, dtype=big_dtype) # set to np.bool_ for masks

	fileIdx = 0
	for row in range(nRow):
		rowStart = row * commonShape[1]
		rowStop = rowStart + commonShape[1]
		for col in range(nCol):
			colStart = col * commonShape[2]
			colStop = colStart + commonShape[2]

			uFirstSlice = None
			uLastSlice = None

			#file = filenames[fileIdx]
			file = loadFileList[fileIdx]

			if file is not None:

				# file is None when file not found or not in uInclude
				if useMasterFile:
					# todo: this needs to be way better organized
					fileNoPostfix = file.replace(postfixStr, '')
					fileNoPostfix += '.tif'
					# don't use tmp_uInclude here (used in getFileList())
					uFile, tmp_uInclude, uFirstSlice, uLastSlice = aicsUtil2.parseMasterFile('', fileNoPostfix, dfMasterFile=dfMasterFile)

				#print('myGetBlock() row:', row, 'col:', col, 'file:', file)

				if not doUseFirstLast:
					uFirstSlice = None
					uLAstSLice = None

				oneBigData = myFileRead0(file, commonShape, dtype=big_dtype, trimPercent=trimPercent, uFirstSlice=uFirstSlice, uLastSlice=uLastSlice)

				try:
					bigStack[:,rowStart:rowStop, colStart:colStop] = oneBigData
				except (ValueError) as e:
					print('    !!! EXCEPTION in myGetBlock() file:', file)
					print('      ', e)
					print('      DID NOT ASSIGN STACK row:', row, 'col:', col)

				# abb 20200923 to save a subset
				if smallDict is not None and (row,col) in smallDict['rowColIdxList']:
					print(f'  smallDict {smallRow} {smallCol} from big {smallRow} {smallCol} file: {file}')
					smallRowStart = smallRow * commonShape[1] # shpu;d be in outer loop
					smallRowStop = smallRowStart + commonShape[1]
					smallColStart = smallCol * commonShape[2]
					smallColStop = smallColStart + commonShape[2]
					# todo: place in small
					smallStack[:,smallRowStart:smallRowStop, smallColStart:smallColStop] = oneBigData
					# increment
					smallCol += 1
					if smallCol == smallDict['nCols']:
						smallCol = 0
						smallRow += 1
				#else:
				#	print(f'  {row} {col} not in {smallDict["rowColIdxList"]}')

			# always increment mXn grid
			fileIdx += 1

	# save small
	if smallDict is not None:
		smallPath = os.path.join(dataPath, smallDict['saveName'])
		if not os.path.isdir(smallPath):
			print('making output folder:', smallPath)
			os.mkdir(smallPath)

		# save big to tiff for import of bigData into bImPy
		bigFile = smallDict['saveName'] + '_BIG_' + '_ch' + str(channel) + '.tif'
		bigPath = os.path.join(smallPath, bigFile)
		if os.path.isfile(bigPath):
			print('ERROR: you need to remove file and run again, bigPath:', bigPath)
		else:
			print('  saving bigPath:', bigPath)
			tifffile.imsave(bigPath, bigStack)

		smallFile = smallDict['saveName'] + '_ch' + str(channel) + '.tif'
		smallPath = os.path.join(smallPath, smallFile)
		if os.path.isfile(smallPath):
			print('ERROR: you need to remove file and run again, smallPath:', smallPath)
		else:
			print('  saving smallPath:', smallPath)
			tifffile.imsave(smallPath, smallStack)

	return bigStack

############################################################
def getShapeGrid(aicsGridParam):
	"""
	Make a list of shapes (polygons to be displayed in Napari as a shape layer
	"""
	shapeList = []

	gridShape = aicsGridParam['gridShape']
	nRow = gridShape[0]
	nCol = gridShape[1]
	commonShape = aicsGridParam['commonShape']
	commonVoxelSize = aicsGridParam['commonVoxelSize']

	for row in range(nRow):
		rowStart = row * commonShape[1] * commonVoxelSize[1]
		rowStop = rowStart + commonShape[1] * commonVoxelSize[1]
		for col in range(nCol):
			colStart = col * commonShape[2] * commonVoxelSize[2]
			colStop = colStart + commonShape[2] * commonVoxelSize[2]

			topLeft = [rowStart, colStart]
			topRight = [rowStart, colStop]
			bottomRight = [rowStop, colStop]
			bottomLeft = [rowStop, colStart]
			oneShape = [topLeft, topRight, bottomRight, bottomLeft]

			#print('row:', row, 'col:', col, 'polygon:', oneShape)

			shapeList.append(oneShape)


	return shapeList

def aicsGridNapari(aicsGridParam, smallDict=None):
	"""
	folderPath: path to aicsAnalysis/ folder
	gridShape: (rows, col)

	notes:
		The aicsAnalysis/ folder .tif files are already trimmed
	"""

	print('  aicsGridNapari() aicsGridParam:')
	for k, v in aicsGridParam.items():
		print('    ', k, ':', v)
	print('  smallDict is:', smallDict)

	masterFilePath = aicsGridParam['masterFilePath'] # 20200814, not used
	path = aicsGridParam['path']
	#prefixStr = aicsGridParam['prefixStr']
	channelList = aicsGridParam['channelList'] # makes postfics str
	commonShape = aicsGridParam['commonShape']
	commonVoxelSize = aicsGridParam['commonVoxelSize']
	gridShape = aicsGridParam['gridShape']
	finalPostfixList = aicsGridParam['finalPostfixList']
	#
	#trimPercent = aicsGridParam['trimPercent']

	# todo: load master file one into df an dpass to other functions (or append to aicsGriddParams?

	# if path does not contain aicsAnalysis then NEVER do anything but raw (e.g. don't do _mask)

	rawBlockList = []
	napariChannelList = []
	napariPostfixList = []

	numBlocks = len(list(itertools.product(channelList,finalPostfixList)))

	print('  building', numBlocks, 'blocks. Each block is a grid of images')
	blockNum = 0
	for channel in channelList:
		for finalPostfixStr in finalPostfixList:
			#print(blockNum, 'of', numBlocks, 'calling myGetBlock()', channel, finalPostfixStr)
			print(f'    {blockNum+1} of {numBlocks} calling myGetBlock() channel {channel}, finalPostfixStr "{finalPostfixStr}"')
			rawBlock = myGetBlock(aicsGridParam, channel=channel, finalPostfixStr=finalPostfixStr, smallDict=smallDict)
			if rawBlock is None:
				# no files found
				print('      aicsGridNapari() did not find files for block, channel:', channel, 'finalPostfixStr:', finalPostfixStr)
			else:
				rawBlockList.append(rawBlock)
				napariChannelList.append(channel)
				napariPostfixList.append(finalPostfixStr)

			'''
			# save to tiff for import of bigData into bImPy
			bigFile = 'bigData_ch' + str(channel) + '.tif'
			bigPath = os.path.join(aicsGridParam['dataPath'], bigFile)
			print('saving bigPath:', bigPath)
			tifffile.imsave(bigPath, rawBlock)
			'''

			#
			blockNum += 1

	if len(rawBlockList):
		# error
		pass

	bigStackShape = rawBlockList[0].shape
	aicsGridParam['bigStackShape'] = bigStackShape

	print('  aicsGridNapari() opening in Napari, grid size:', gridShape, ' please wait ...')
	# for napari
	tmpPath, windowTitle = os.path.split(path)
	tmpPath2, windowTitle2 = os.path.split(tmpPath)


	doCountLabels = False
	aicsGridParam['doCountLabels'] = doCountLabels

	with napari.gui_qt():
		title = f'aicsGridNapari: {windowTitle2}/{windowTitle}'
		viewer = napari.Viewer(title=title)
		viewer.metadata = aicsGridParam

		for idx, rawBlock in enumerate(rawBlockList):
			print('    ', idx+1, 'of', len(rawBlockList), 'blocks', rawBlock.dtype)
			channelIdx = napariChannelList[idx]

			thisPostfix = napariPostfixList[idx]

			# default for raw data ''
			thisType = 'image'
			visible = True
			color = 'gray'
			if channelIdx == 1:
				color = 'green'
			elif channelIdx == 2:
				color = 'red'
			blending = 'additive'
			opacity = 1.0
			minContrast = 0
			maxContrast = 160

			if thisPostfix in ['_mask']:
				visible = False
				thisType = 'image'
				minContrast = 0
				maxContrast = 1
				if channelIdx == 1:
					color = 'cyan'
				elif channelIdx == 2:
					color = 'magenta'
			elif thisPostfix in ['_labeled']:
				visible = False
				thisType = 'labeled'

			name = 'ch' + str(channelIdx) + ' ' + str(thisPostfix)

			if thisType == 'image':
				# add image
				myImageLayer = viewer.add_image(rawBlock, scale=commonVoxelSize, colormap=color,
						contrast_limits=(minContrast, maxContrast), opacity=opacity, blending=blending,
						visible=visible, name=name)
			elif thisType == 'labeled':
				# add label
				myLabelLayer = viewer.add_labels(rawBlock, scale=commonVoxelSize,
									opacity=opacity,
									visible=visible, name=name)
		#
		# add grid of stack square
		polygons = getShapeGrid(aicsGridParam) # get list of polygons, one square per stack in ENTIRE grid
		edge_width = 5
		visible = True
		shapeLayer = viewer.add_shapes(polygons, shape_type='polygon', edge_width=edge_width,
                              edge_color='yellow', face_color='black',
                              opacity=opacity, blending=blending,
                              visible=visible, name='Grid')

		#
		# keyboard callbacks
		@viewer.bind_key('Shift-L')
		def myToggleLabelCount(viewer):
			aicsGridParam = viewer.metadata
			aicsGridParam['doCountLabels'] = not aicsGridParam['doCountLabels']
			print("  aicsGridParam['doCountLabels']:", aicsGridParam['doCountLabels'])

		#
		# mouse click callback
		@viewer.mouse_drag_callbacks.append
		def viewerMouseDrag(viewer, event):
			print('=== aicsGridNapari.viewerMouseDrag()')

			#
			# get grid parameters from metadata
			aicsGridParam = viewer.metadata # important
			gridShape = aicsGridParam['gridShape']
			commonShape = aicsGridParam['commonShape'] # of each stack
			commonVoxelSize = aicsGridParam['commonVoxelSize']
			#
			snakeGrid = aicsGridParam['snakeGrid']

			# slice is in um (we are using voxel scale (z,x,y)
			currentSlice = viewer.dims.point[0] # get the slice
			# um to pixel (um / (um/pixel))
			currentSlice = currentSlice / commonVoxelSize[0]
			currentSlice = int(currentSlice)

			xCoord = None
			yCoord = None
			for layer in viewer.layers:
				if layer.selected:
					xCoord = layer.coordinates[0] # um
					yCoord = layer.coordinates[1]
					continue
			if xCoord is None or yCoord is None:
				print('  viewerMouseDrag() please select at least one layer')
				return

			if xCoord<0 or yCoord<0:
				print('  viewerMouseDrag() please click within the grid')
				return


			#
			# find the row/col, and filename

			nCol = gridShape[1] # (rows, cols)

			xCoord = xCoord / commonVoxelSize[1] # um to pixel (um / (um/pixel))
			yCoord = yCoord / commonVoxelSize[2]

			#print('  xCoord (pixel):', xCoord, 'yCoord (pixel):', yCoord)
			xCoord = round(xCoord)
			yCoord = round(yCoord)

			myRow = xCoord // commonShape[1]
			myCol = yCoord // commonShape[2]
			myIdx = myRow * nCol + myCol # this needs to be snaked !!!
			try:
				myIdx = snakeGrid[myRow,myCol]
			except (IndexError) as e:
				#print('exception in aicsGridNapari.viewerMouseDrag()')
				#print('  myRow', myRow, 'myCol:', myCol, snakeGrid.shape, e)
				print('  viewerMouseDrag() please click within the grid')
				return
				#myIdx = None

			print('  Current Slice:', currentSlice)
			print('  xCoord (um):', round(xCoord,2), 'yCoord (um):', round(yCoord,2))
			print('  xCoord (pixel):', xCoord, 'yCoord (pixel):', yCoord)
			print('  Row:', myRow+1, 'Col:', myCol+1, 'File Idx:', myIdx)

			# now get file index from myIdx

			# go through all labeled layers and find (label number, size) that was clicked on
			for layer in viewer.layers:
				if '_labeled' in layer.name:
					try:
						labelVal = layer.data[currentSlice, xCoord, yCoord]
						print('  Shift-L to toggle label count on/off ... can be slow')
						if aicsGridParam['doCountLabels']:
							labelCount = np.count_nonzero(layer.data == labelVal)
						else:
							labelCount = None
						print('  ', layer.name, 'labelVal:', labelVal, 'labelCount:', labelCount)
					except (IndexError) as e:
						print('!!! exception on mouse click:', e)
		#
		print('  Done ... Napari viewer should be open ...')

if __name__ == '__main__':


	masterFilePath = 'aicsBatch/20200717_cell_db.csv'
	path = '/Volumes/ThreeRed/nathan/20200717/aicsAnalysis0'
	path = '/Users/cudmore/Desktop/aicsAnalysis0'
	prefixStr = '20200717__A01_G001_'
	commonShape = (88,740,740)
	commonVoxelSize = (1, 0.3977476, 0.3977476)
	channelList = [1,2]
	gridShape = (11,4)
	finalPostfixList = ['', '_mask', '_labeled']
	#doUseInclude = True
	#doUseFirstLast = True

	# raw data ... WILL NOT BE TRIMMED BY OVERLAP
	'''
	masterFilePath = ''
	path = '/Volumes/ThreeRed/nathan/20200717'
	commonShape = (88,800,800)
	commonVoxelSize = (1, 0.3977476, 0.3977476)
	channelList = [1,2]
	gridShape = (11,4)
	finalPostfixList = [''] # '' is no postfix, e.g. raw tiff like _ch1.tif and _ch2.tif
	'''

	aicsGridParam = OrderedDict()
	aicsGridParam['masterFilePath'] = masterFilePath
	aicsGridParam['path'] = path
	aicsGridParam['prefixStr'] = prefixStr
	aicsGridParam['commonShape'] =  commonShape# shape of each stack in aicsAnalysis (already trimmed)
	aicsGridParam['commonVoxelSize'] = commonVoxelSize
	aicsGridParam['channelList'] = channelList
	aicsGridParam['gridShape'] = gridShape
	aicsGridParam['finalPostfixList'] = finalPostfixList
	aicsGridParam['trimPercent'] = None
	#aicsGridParam['doUseInclude'] = doUseInclude
	#aicsGridParam['doUseFirstLast'] = doUseFirstLast

	aicsGridNapari(aicsGridParam)

	#
	# testing
	if 0:
		tmpChannel = 1
		tmpPostfixStr = '_mask'
		tmpFileList = getFileList(aicsGridParam, tmpChannel, tmpPostfixStr)
		print('tmpFileList:', len(tmpFileList))
		for idx, file in enumerate(tmpFileList):
			print(idx, file)
