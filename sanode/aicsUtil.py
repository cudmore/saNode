"""
"""

import os, sys, math, logging

from collections import OrderedDict
from datetime import datetime

logging.getLogger().setLevel(logging.INFO)

import numpy as np
import pandas as pd

import bimpy # only used in setupAnalysis()

"""
raw
labeled (also save by manual edits)
labeled_removed # small labels
labeled_removed_manual # after manual edits, resave _labeled (should be able to revert)
mask
hull
edt
"""

################################################################################
def myGetDefaultParamDict():
	"""
	Using order here to save files with _1_, _2_, _3_, ...
	"""
	paramDict = OrderedDict()
	#paramDict['analysisDate'] = ''
	#paramDict['analysisTime'] = ''
	
	paramDict['path'] = ''
	paramDict['fileNameBase'] = ''
	#paramDict['f3_param'] =[[3, 0.001], [5, 0.001], [7, 0.001]]
	paramDict['f3_param'] =[[5, 0.001], [8, 0.001]]
	paramDict['medianKernelSize'] = (2,2,2)
	paramDict['removeBelowThisPercent'] = 0.09
	paramDict['removeSmallerThan'] = 2200 #2000 #600 #500
	
	return paramDict
	
'''
def myGetDefaultStackDict():
	"""
	Using order here to save files with _1_, _2_, _3_, ...
	"""
	stackDict = OrderedDict()
	stackDict['raw'] = {'type': 'image', 'data': None}
	stackDict['slidingz'] = {'type': 'image', 'data': None}
	stackDict['filtered'] = {'type': 'image', 'data': None}
	stackDict['threshold0'] = {'type': 'image', 'data': None} # added while working on 20200518, remove lower % of image
	stackDict['threshold1'] = {'type': 'image', 'data': None} # image remaining after threshold_sauvola
	stackDict['threshold'] = {'type': 'mask', 'data': None} # added while working on cellDen.py
	stackDict['labeled'] = {'type': 'label', 'data': None}
	stackDict['small_labels'] = {'type': 'label', 'data': None}
	stackDict['finalMask'] = {'type': 'mask', 'data': None}
	stackDict['remainingRaw'] = {'type': 'image', 'data': None}
	stackDict['finalMask_hull'] = {'type': 'mask', 'data': None}
	stackDict['finalMask_edt'] = {'type': 'edt', 'data': None}

	return stackDict
'''
################################################################################
def myGetDefaultStackDict():
	"""
	Using order here to save files with _1_, _2_, _3_, ...
	"""
	stackDict = OrderedDict()
	stackDict['raw'] = {'type': 'image', 'data': None}
	stackDict['slidingz'] = {'type': 'image', 'data': None}
	stackDict['filtered'] = {'type': 'image', 'data': None}
	stackDict['threshold0'] = {'type': 'image', 'data': None} # added while working on 20200518, remove lower % of image
	stackDict['threshold1'] = {'type': 'image', 'data': None} # image remaining after threshold_sauvola
	stackDict['threshold'] = {'type': 'mask', 'data': None} # added while working on cellDen.py
	stackDict['labeled'] = {'type': 'label', 'data': None}
	stackDict['small_labels'] = {'type': 'label', 'data': None}
	stackDict['mask'] = {'type': 'mask', 'data': None}
	stackDict['remainingRaw'] = {'type': 'image', 'data': None}
	stackDict['finalMask_hull'] = {'type': 'mask', 'data': None}
	stackDict['finalMask_edt'] = {'type': 'edt', 'data': None}

	return stackDict
			
################################################################################
def removeChannelFromName(name):
	name = name.replace('_ch1', '')
	name = name.replace('_ch2', '')
	return name	
	
################################################################################
def updateMasterCellDB(outFilePath, path, paramDict):
	"""
	todo: fix this to just append a row, as is is super complicated
	
	just append a row to a cs, this will somtimes result in csv being out of order
	
	outFilePath: assuming our master file path is _cell_db.csv, this will be _cell_db_out.csv
	"""
	
	print('  .updateMasterCellDB() filename:', filename, 'masterFilePath:', masterFilePath)
	
	tmpPath, tmpFilename = os.path.split(path)
	baseFileName, tmpExt = tmpFilename.split('.')
	
	#
	# load
	df = pd.read_csv(masterFilePath, index_col='index')

	#
	# important
	df.index.name = 'index' 
	
	#
	# check that filename exists
	dfTmp = df.loc[df['uFilename'] == filename]
	if len(dfTmp) == 0:
		# append after baseFilename
		
		# find row with baseFilname
		
		baseFilename = filename.replace('_ch1.tif', '')
		baseFilename = baseFilename.replace('_ch2.tif', '')
		baseFilename = baseFilename.replace('_ch3.tif', '')

		# find the row with basefilename (e.g. without (_ch1.tif, _ch2.tif)
		baseFileRow = df.loc[df['uFilename'] == baseFilename]
		baseFileIndex = baseFileRow.index[0]
		
		#line = pd.DataFrame([[np.nan] * len(df.columns)], columns=df.columns)
		#df2 = pd.concat([df.iloc[:baseFileIndex], line, df.iloc[baseFileIndex:]]).reset_index(drop=True)

		newIdx = baseFileIndex + 0.5
		newRow = pd.DataFrame([[np.nan] * len(df.columns)], index=[newIdx], columns=df.columns)
		newRow['uFilename'] = filename
		df = pd.concat([df, newRow]).sort_index()
		df = df.reset_index(drop=True)
		
		print('  updateMasterCellDB() appending row', newIdx)

		#print('  ERROR: updateMasterCellDB() did not find uFilename:', filename, 'in masterFilePath:', masterFilePath)
		#return
		
	for k,v in paramDict.items():
		if not k in df.columns:
			#print('    *** updateMasterCellDB() is appending column named:', k)
			df[k] = ""
		
		df.loc[df['uFilename'] == filename, k] = str(v)
	
	#
	# resave
	print('    updateMasterCellDB() is saving', masterFilePath)
	df.to_csv(masterFilePath, index_label='index')
	
################################################################################
def getAnalysisPath(masterFilePath):

	if not os.path.isfile(masterFilePath):
		print('  ERROR: getNextFile() did not find masterFilePath:', masterFilePath)
		return None, None

	df = pd.read_csv(masterFilePath, index_col=False) # index_col=False can be used to force pandas to not use the first column as the index
	numRow = df.shape[0]
	
	uAnalysisPath = df['uAnalysisPath'].iloc[0]
	
	return uAnalysisPath
	
################################################################################
def getNextFile(masterFilePath, rowIdx=None, getThis='next'):
	"""
	Search masterFilePath for next file with 'uInclude'
	
	rowIdx: row index to start at, otherwise 0
	getThis: in (next, previous)
	"""
	
	if not os.path.isfile(masterFilePath):
		print('  ERROR: getNextFile() did not find masterFilePath:', masterFilePath)
		return None, None

	df = pd.read_csv(masterFilePath, index_col=False) # index_col=False can be used to force pandas to not use the first column as the index
	numRow = df.shape[0]

	if rowIdx is None:
		rowIdx = -1
	
	if getThis == 'next':
		# increment
		rowIdx += 1
		endRow = numRow
		theRange = range(rowIdx, endRow)
	elif getThis == 'previous':
		#rowIdx -= 1
		endRow = 0
		theRange = reversed(range(endRow, rowIdx))
	
	#print('rowIdx:', rowIdx, 'endRow:', endRow)
	
	theRowIndex = None
	theFile = None
	
	# search from rowIdx+1 to end and look for 'uInclude'
	for i in theRange:
		uFilename = df['uFilename'].iloc[i]
		uInclude = df['uInclude'].iloc[i]
		#print(i, uFilename, uInclude)
		if uInclude == 1:
			#print(i, uFilename, uInclude)
			theRowIndex = i
			theFile = uFilename
			break
			
	return theRowIndex, theFile
	
################################################################################
################################################################################
def pruneStackData(filename, stackData, firstSlice=None, lastSlice=None):
	"""
	prune stack slices by filename (row) and (firstslice, lastslice) specified in .csv file masterFilePath
	
	filename: full file name with _ch and .tif
	"""
	
	numSlices = stackData.shape[0]
	
	if firstSlice is None and lastSlice is None:
		pass
	elif firstSlice > 0 and lastSlice < numSlices - 1:
		#print('  ', 'pruning stackData slices')
		print('  pruneStackData() from stackData', stackData.shape)	
		stackData = stackData[firstSlice:lastSlice+1,:,:] # remember +1 !!!!!
		print('  pruneStackData() pruned stackData', stackData.shape)	

	return stackData
	
################################################################################
################################################################################
def setupAnalysis(path, trimPercent = 15, firstSlice=None, lastSlice=None, saveFolder='aicsAnalysis'):
	"""
	path: path to single raw _ch1/_ch2 stack
	trimPercent: percent of image that is overlapping in FV300 tiling
	saveFolder: allows us to save results in different folders
	masterFilePath: must be specified, see analysis/xxx.csv
	"""
	
	print('  setupAnalysis() path:', path)
	
	folderpath, filename = os.path.split(path)
	filenamenoextension, tmpExt = filename.split('.')
	
	savePath = os.path.join(folderpath, saveFolder)
	saveBase = os.path.join(savePath, filenamenoextension)

	# make output folder
	if not os.path.isdir(savePath):
		os.mkdir(savePath)

	channel = None
	if filename.endswith('_ch1.tif'):
		channel = 1
	elif filename.endswith('_ch2.tif'):
		channel = 2
	elif filename.endswith('_ch3.tif'):
		channel = 3
	
	#print('  savePath:', savePath)
	print('    channel:', channel, 'saveBase:', saveBase) # append _labeled.tif to this
		
	#
	# make a dictionary of dictionaries to hold (type, data) for each step
	stackDict = myGetDefaultStackDict()
	
	#
	# save (stack pixels, pruned stack pixels, analysis parameters, number of original labels)
	paramDict = myGetDefaultParamDict()
	
	paramDict['analysisDate'] = datetime.today().strftime('%Y%m%d')
	paramDict['analysisTime'] = datetime.now().strftime('%H:%M:%S')
	
	paramDict['channel'] = channel

	paramDict['fileNameBase'] = filenamenoextension
	
	#
	# load
	print('    setupAnalysis() loading stack:', path)
	stackData, tiffHeader = bimpy.util.bTiffFile.imread(path)
	paramDict['tiffHeader'] = tiffHeader
	_printStackParams('  stackData', stackData)
	
	paramDict['zVoxel'] = tiffHeader['zVoxel']
	paramDict['xVoxel'] = tiffHeader['xVoxel']
	paramDict['yVoxel'] = tiffHeader['yVoxel']

	paramDict['zOrigPixel'] = stackData.shape[0]
	paramDict['xOrigPixel'] = stackData.shape[1] # rows
	paramDict['yOrigPixel'] = stackData.shape[2]
		
	#
	# trim
	trimPixels = math.floor( trimPercent * stackData.shape[1] / 100 ) # ASSUMING STACKS ARE SQUARE
	trimPixels = math.floor(trimPixels / 2)
	if trimPixels > 0:
		print('    trimming', trimPixels, 'lower/right pixels')
		_printStackParams('from', stackData)
		thisHeight = stackData.shape[1] - trimPixels
		thisWidth = stackData.shape[2] - trimPixels
		stackData = stackData[:, 0:thisHeight, 0:thisWidth]
		_printStackParams('to', stackData)
	else:
		print('    WARNING: not trimming lower/right x/y !!!')
		
	#
	# keep slices
	# will return None when user has not specified first/last
	stackData = pruneStackData(filename, stackData, firstSlice=firstSlice, lastSlice=lastSlice) # can be None
	stackDict['raw']['data'] = stackData
	
	paramDict['firstSlice'] = firstSlice
	paramDict['lastSlice'] = lastSlice

	if stackData is not None:
		paramDict['zFinalPixel'] = stackData.shape[0]
		paramDict['xFinalPixel'] = stackData.shape[1] # rows
		paramDict['yFinalPixel'] = stackData.shape[2]

	paramDict['saveBase'] = saveBase

	return filename, paramDict, stackDict

################################################################################
def _printStackParams(name, myStack):
	print('  ', name, myStack.shape, myStack.dtype, 'dtype.char:', myStack.dtype.char,
		'min:', np.min(myStack),
		'max:', np.max(myStack),
		'mean:', np.mean(myStack),
		'std:', np.std(myStack),
		)

if __name__ == '__main__':
	
	path = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0003_ch2.tif'
	trimPercent = 15
	masterFilePath = 'aicsBatch/20200717_cell_db.csv'
	
	uFIle, uInclude, uFirstSlice, uLastSlice = parseMasterFile(masterFilePath, path)
	
	filename, paramDict, stackDict = \
		setupAnalysis(path, trimPercent = 15, firstSlice=uFirstSlice, lastSlice=uLastSlice)
	
	print('filename:', filename)
	print('paramDict:', paramDict)
	#print('stackDict:', stackDict)
	
	#filename = '20200717__A01_G001_0003'
	updateMasterCellDB(masterFilePath, filename, paramDict)
	
	