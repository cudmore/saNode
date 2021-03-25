"""
Script to process a folder of folders with ch1/ch2 Tiff files into a visual grid
grid is usually from Olympus FV3000

raw stacks are 640 x 640
trimPercent = 15
gives trimmed size

raw (640,640) after 0.15% trim is (592,592)
"""

import os, sys, math, glob
import numpy as np
import tifffile

import matplotlib.pyplot as plt

def myMakeNumPy(tifDataList, fileIdxMatrix, nRow, nCol, numSlices=None, folderPath=None):
	"""
	make a big numpy aray from list of tif (source can be either 2d max-project or original 3d stacks)

	tifDataList: can be list of 2d or 3d aray
	fileIdxList: gives us the ordering into tifDataList[idx]
	numSlices: (not implemented) some Imaris output folders have different number of slices
			set this to force, otherwise we will use the first folder

	todo: for now this will only work with max project
	"""
	print('myMakeNumPy() making one big tif')
	bigNumPy = None
	commonShape = None
	idx = 0
	for rowIdx in range(nRow):
		for colIdx in range(nCol):
			tifData = tifDataList[idx]

			if tifData is not None:
				if commonShape is None:
					commonShape = tifData.shape # assumind 2d for now
					if len(commonShape) == 2:
						bigRows = commonShape[0] * nRow
						bigCols = commonShape[1] * nCol
						#bigNumPy = np.zeros((bigRows,bigCols), dtype=tifData.dtype)
						bigNumPy = np.zeros((bigRows,bigCols), dtype=np.bool_) # dtype is 32-bit
					elif len(commonShape) == 3:
						bigSlices = commonShape[0]
						bigRows = commonShape[1] * nRow
						bigCols = commonShape[2] * nCol
						#bigNumPy = np.zeros((bigRows,bigCols), dtype=tifData.dtype)
						dtype = tifData.dtype
						print('making 3D bigNumPy with rowIdx:', rowIdx, 'colIdx:', colIdx, 'file num:', fileIdxMatrix[rowIdx][colIdx])
						print('  shape:', (bigSlices,bigRows,bigCols))
						bigNumPy = np.zeros((bigSlices,bigRows,bigCols), dtype=np.bool_) # dtype is 32-bit

				if len(commonShape) == 2:
					startRow = rowIdx * commonShape[0]
					stopRow = startRow + commonShape[0]
					startCol = colIdx * commonShape[1]
					stopCol = startCol + commonShape[1]
				elif len(commonShape) == 3:
					startRow = rowIdx * commonShape[1]
					stopRow = startRow + commonShape[1]
					startCol = colIdx * commonShape[2]
					stopCol = startCol + commonShape[2]
				#print('    startRow:', startRow, 'stopRow:', stopRow)
				#print('    startCol:', startCol, 'stopCol:', stopCol)

				if len(commonShape)==2:
					bigNumPy[startRow:stopRow, startCol:stopCol] = tifData
				elif len(commonShape)==3:
					try:
						# this will only work if common shape is bigger
						# some have fewer slices than others
						startSlice = 0
						bigStopSlice = bigNumPy.shape[0]
						stopSlice = tifData.shape[0]
						if bigStopSlice != stopSlice:
							print('  WARNING: myMakeNumPy() slice mistmatch at rowIdx:', rowIdx, 'colIdx:', colIdx)
							print('    bigNumPy:', bigNumPy.shape, 'tifData:', tifData.shape)
						stopSlice = min(bigStopSlice, stopSlice)
						bigNumPy[startSlice:stopSlice,startRow:stopRow, startCol:stopCol] = tifData
					except(ValueError) as e:
						print('ERROR: myMakeNumPy() rowIdx:', rowIdx, 'colIdx:', colIdx)
						print('  bigNumPy:', bigNumPy.shape, 'tifData:', tifData.shape)
						print('  startSlice:', startSlice, 'stopSlice:', stopSlice)
			# increment idx
			idx += 1
	#
	savePath = 'big.tif'
	if len(commonShape)==2:
		typeStr = '_big_2d.tif'
	elif len(commonShape)==3:
		typeStr = '_big_3d.tif'
	if folderPath is not None:
		folderName = os.path.split(folderPath)[1]
		savePath = os.path.join(folderPath, folderName + typeStr)
	print('saving _big.tif as:', bigNumPy.dtype, 'to:', savePath)
	tifffile.imsave(savePath, bigNumPy)

##############################################################
def trimStack(stackData, trimPercent, verbose=True):
	""""
	20210322, now trimming left/top/right/bottom
	previously was only trimming bottom/right
	"""
	# from Olympus, usually trimPercent = 15
	trimPixels = math.floor( trimPercent * stackData.shape[1] / 100 ) # ASSUMING STACKS ARE SQUARE
	trimPixels = math.floor(trimPixels / 2)
	if trimPixels > 0:
		if verbose: print('    trimming', trimPixels, 'left/top/right/bottom pixels')
		if verbose: print('    original shape:', stackData.shape)
		thisHeight = stackData.shape[1] - trimPixels
		thisWidth = stackData.shape[2] - trimPixels
		#stackData = stackData[:, 0:thisHeight, 0:thisWidth]
		stackData = stackData[:, trimPixels:thisHeight, trimPixels:thisWidth]
		if verbose: print('    final shape:', stackData.shape)
	else:
		print('    WARNING: trimStack() not trimming lower/right x/y !!!')

	return stackData

def myMakeGrid_ImarisMask(path, prefixStr, channel, nRow, nCol, trimPercent):
	"""
	load output of imaris masks
	load from folders of single plane .tif

	parameters:
		path:
		prefixStr: not used
		channel: (None, 1, 2)
		nRow,nCol: size of the original grid. We assume it is snaked
				giving us folder order like
				[1,2,3,4]
				[8,7,6,5]
				trimPercent: percent of pixels to trim from lower right of each stack
				[...]
		trimPercent: None or percent to trim, Olympus is usually trimPercent = 0.15
	"""
	print(f'myMakeGrid_ImarisMask() loading {nRow*nCol} from nRow:{nRow} x nCol:{nCol} ... please wait ...')
	verbose = True
	postfixStr = '.tif'
	if channel == 1:
		postfixStr = '_ch1.tif'
	elif channel == 2:
		postfixStr = '_ch2.tif'

	# make nRow X nCol grid of integers
	tmpIntegerGrid = np.arange(1,nRow*nCol+1) # Values are generated within the half-open interval [start, stop)
	tmpIntegerGrid = np.reshape(tmpIntegerGrid, (nRow, nCol)) # reshape into nRow X nCol
	# reverse numbers in every other row (to replicate 'snake' image acquisition)
	integerGrid = tmpIntegerGrid.copy()
	integerGrid[1::2] = tmpIntegerGrid[1::2,::-1] # this is obfuscated

	# keep track of per stack slices
	sliceNumGrid = None # todo: add this

	# folder names are 1,2,3, ... 22,23,24
	# some folders are missing
	folderNames = [str(x) for x in integerGrid.ravel()]
	tifDataList = []
	#tifSliceList = []
	tifMaxList = []
	commonShape = None
	numFoldersLoaded = 0
	# folderNames are for numbered folders coming out of imaris
	# each folder number corresponds to original tif/oir number in acquisition grid
	for folderName in folderNames:
		folderPath = os.path.join(path, folderName)
		if os.path.isdir(folderPath):
			# raw data
			if verbose: print('loading raw data from folderPath:', folderPath)
			tmp = glob.glob(folderPath + '/*.tif')
			tmp = sorted(tmp)
			#print(tmp)
			stackData = tifffile.imread(tmp)
			if trimPercent is not None:
				stackData = trimStack(stackData, trimPercent)
			tifDataList.append(stackData)

			print('  ', numFoldersLoaded, 'folderName:', folderName,
					stackData.shape, stackData.dtype, 'min:', np.min(stackData),
					'max:', np.max(stackData))

			# max project
			theMax = np.max(stackData, axis=0)
			tifMaxList.append(theMax)

			# common shape
			if commonShape is None:
				commonShape = stackData.shape
				#print('myMakeGrid() commonShape:', commonShape)

			#
			numFoldersLoaded += 1
		else:
			# todo: This is a bug if we missing files
			#print('  WARNING: Did not find file:', tiffPath)
			#if verbose: print('  Warning: myMakeGrid_ImarisMask() did not find folder:', folderPath)
			tifDataList.append(None)
			tifMaxList.append(None)

	print(f'Loaded {numFoldersLoaded} folders from {nRow}x{nCol} grid with {nRow*nCol} potential folders(tif stacks)')
	#
	# returning folderNames rather than original filesNames
	return tifDataList, tifMaxList, folderNames, integerGrid, sliceNumGrid

def myMakeGrid(path, prefixStr, channel, nRow, nCol):

	if channel == 1:
		postfixStr = '_ch1.tif'
	elif channel == 2:
		postfixStr = '_ch2.tif'

	# make nRow X nCol grid of integers
	tmpIntegerGrid = np.arange(1,nRow*nCol+1) # Values are generated within the half-open interval [start, stop)
	tmpIntegerGrid = np.reshape(tmpIntegerGrid, (nRow, nCol)) # reshape into nRow X nCol
	# reverse numbers in every other row (to replicate 'snake' image acquisition)
	integerGrid = tmpIntegerGrid.copy()
	integerGrid[1::2] = tmpIntegerGrid[1::2,::-1] # this is obfuscated

	# make a list of file names following order of snake pattern in integerGrid
	filenames = [prefixStr + str(x).zfill(4) + postfixStr for x in integerGrid.ravel()]
	# make all file names be full path
	filenames = [os.path.join(path, x) for x in filenames]

	print(f'myMakeGrid() parsing {len(filenames)} files.')

	# check that all files exist, display will fail when loading file that does not exist
	tifDataList = []
	tifMaxList = []
	commonShape = None
	for idx, tiffPath in enumerate(filenames):
		if os.path.isfile(tiffPath):
			# raw data
			stackData = tifffile.imread(tiffPath)
			tifDataList.append(stackData)

			#print(idx, stackData.shape, tiffPath)

			# max project
			theMax = np.max(stackData, axis=0)
			tifMaxList.append(theMax)

			# common shape
			if commonShape is None:
				commonShape = stackData.shape
				print('myMakeGrid() commonShape:', commonShape)

		else:
			# todo: This is a bug if we missing files
			#print('  WARNING: Did not find file:', tiffPath)
			print('myMakeGrid() did not find file:', tiffPath)
			tifDataList.append(None)
			tifMaxList.append(None)

	#
	return tifDataList, tifMaxList, filenames, integerGrid

def plotGrid(folderPath, nRow, nCol, fileNameList, fileIdxList, tifMaxList,
				plotLabels, wSpace, hSpace, verbose=False):
	print('please wait ... folderPath:', folderPath)

	#plotLabels = True # plot the file index in the middle of the image

	# choose a width (in inches) and we will calculate a respective height
	figWidth = 10 #nCol
	figWidth = nCol
	#figHeight = nRow
	heightMult = nRow / nCol
	figHeight = figWidth * heightMult

	print('figWidth:', figWidth, 'figHeight:', figHeight)

	# make (nRow x nCol) subplots
	fig, axs = plt.subplots(nrows=nRow, ncols=nCol,
							sharex=True, sharey=True, figsize=(figWidth,figHeight),
							constrained_layout=True)
	axs = axs.ravel() # flatten all subplots into [0, 1, 2, ...]

	for idx, fileName in enumerate(fileNameList):
		#print('plotGrid():', idx, fileName)

		fileIdx = fileIdxList[idx] # this list is snaked
		plotIdx = fileIdx - 1 # matplotlib is 0 based, our file names are 1 based

		#stackData = tifDataList[plotIdx]
		maxData = tifMaxList[plotIdx]

		# turn off axes labels
		axs[plotIdx].axis('off')

		if maxData is None:
			continue

		#axs[plotIdx].imshow(maxData, cmap=cmap) # looks awefull ???
		axs[plotIdx].imshow(maxData, aspect='equal')


		#print('plotIdx:', plotIdx, 'fileIdx:', fileIdx)

		# put label above image

		# put label in middle of image
		if plotLabels:
			fileIdxLabel = idx + 1 # snakes filename 0001, 0002, 0003, ...
			halfHeight = maxData.shape[0]/2
			halfWidth = maxData.shape[1]/2
			fontsize = 14
			axs[plotIdx].text(halfHeight, halfWidth, '{:d}'.format(fileIdxLabel), ha='center', va='center',
				fontsize=fontsize,
				color='k',
				bbox=dict(boxstyle='round', facecolor='white', edgecolor='0.3'))

	# Pad each stack with some border white space
	plt.subplots_adjust(wspace=wSpace, hspace=hSpace)

	# needed when we are in a script (not in Jupyter)
	plt.show()

	print('done')

def _run():
	"""
	20210321 this was for loading original stack .tif files
	replaced by fromImarisMask to load from folders of .tif
	"""
	# either this
	if 0:
		folderPath = '/Users/cudmore/box/data/nathan/20200518'
		prefixStr = '20200518__A01_G001_'
		nRow = 8
		nCol = 6

	# or this
	if 0:
		folderPath = '/Users/cudmore/box/data/nathan/20200519'
		prefixStr = '20200519__A01_G001_'
		nRow = 17
		nCol = 7

	if 0:
		folderPath = '/home/cudmore/data/nathan/20200720'
		prefixStr = '20200720__A01_G001_'
		nRow = 8 #12
		nCol = 6 #4

	if 0:
		folderPath = '/home/cudmore/data/nathan/20200901_SAN4_TOP'
		prefixStr = '20200901__A01_G001_'
		nRow = 12
		nCol = 6

	if 0:
		folderPath = '/home/cudmore/data/nathan/20200914_SAN4_BOTTOM'
		prefixStr = '20200914__A01_G001_'
		nRow = 14
		nCol = 6


	# specify the channel
	channel = 1
	#channel = 2 # does not look so good for CD-31 because of endocardium

	# myMakeGrid is defined above
	tifDataList, tifMaxList, fileNameList, fileIdxMatrix = myMakeGrid(folderPath, prefixStr, channel, nRow, nCol)

	print('fileIdxMatrix:')
	print(fileIdxMatrix)

	fileIdxList = fileIdxMatrix.ravel() # flatten 2d to 1d, we still need to know (nRow, nCol)

	print('done with myMakeGrid()')
	print(f'plotting {len(fileNameList)} files')
	#
	# plot
	plotLabels = True
	#wSpace = 0.02 # a little white space between stacks
	#hSpace = 0.02
	wSpace = -0.1 # to remove border
	hSpace = -0.1
	plotGrid(folderPath, nRow, nCol, fileNameList, fileIdxList, tifMaxList, plotLabels, wSpace, hSpace)

def fromImarisMask(folderPath, nRow, nCol, trimPercent=None):
	"""
	take a folder of oir numbered folders and make a big tif grid

	parameters:
		folderPath: full path to folder (usually numbered) that contains a long list of single image .tif
		nRow/nCol: number of .tif files acquired on Olympus Fv3000
		trimPercent: Usually 15 %, can be None for no trimming

	# folder of numbered folders for one channel
	# downloaded from box
	"""

	prefixStr = None
	channel = 1

	#
	# myMakeGrid is defined above
	#trimPercent = 15
	#trimPercent = None
	print('fromImarisMask() folderPath:', folderPath)
	tifDataList, tifMaxList, fileNameList, fileIdxMatrix, sliceNumMatrix= myMakeGrid_ImarisMask(
										folderPath, prefixStr, channel, nRow, nCol, trimPercent)

	print('fileIdxMatrix:')
	print(fileIdxMatrix)
	print('sliceNumMatrix:')
	print(sliceNumMatrix)

	fileIdxList = fileIdxMatrix.ravel() # flatten 2d to 1d, we still need to know (nRow, nCol)

	print('done with myMakeGrid()')
	print(f'plotting {len(fileNameList)} files')
	#
	# plot
	if 0:
		plotLabels = False
		#wSpace = 0.02 # a little white space between stacks
		#hSpace = 0.02
		wSpace = -0.1 # to remove border
		hSpace = -0.1
		plotGrid(folderPath, nRow, nCol, fileNameList, fileIdxList, tifMaxList, plotLabels, wSpace, hSpace)

	# make big numpy matrix (can be 2d or 3d) and then save
	# save it into original folder
	# save max-project to .tif
	myMakeNumPy(tifMaxList, fileIdxMatrix, nRow, nCol, folderPath=folderPath)
	# save 3d to .tif
	myMakeNumPy(tifDataList, fileIdxMatrix, nRow, nCol, folderPath=folderPath)

if __name__ == '__main__':

	#dataPath = '/media/cudmore/data/heat-map/san4-raw'
	dataPath = '/media/cudmore/data/heat-map/san4-raw'

	trimPercent = 15

	#
	#san4 upper/top
	if 1:
		# vessels
		folderPath = f'{dataPath}/san4-top/san4-top-cd31'
		# hcn4
		#folderPath = f'{dataPath}/san4-top/san4-top-hcn4'
		prefixStr = None # files are in numbered folder #'20200914__A01_G001_' # 20200901__A01_G001_0011_ECSubtract_Z000.tif
		nRow = 12
		nCol = 6
		# specify the channel
		channel = 1
		#channel = 2 # does not look so good for CD-31 because of endocardium

	#san4 lower/bottom
	if 0:
		# vessels slices=86
		#folderPath = f'{dataPath}/san4-bottom/san4-bottom-cd31'
		# hcn4
		folderPath = f'{dataPath}/san4-bottom/san4-bottom-hcn4'
		prefixStr = None # files are in numbered folder #'20200914__A01_G001_' # 20200901__A01_G001_0011_ECSubtract_Z000.tif
		nRow = 14
		nCol = 6
		# specify the channel
		channel = 1
		#channel = 2 # does not look so good for CD-31 because of endocardium

	#
	fromImarisMask(folderPath, nRow, nCol, trimPercent)
