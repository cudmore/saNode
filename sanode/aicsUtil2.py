"""
aics utilities that do not require bimpy
"""

import os, sys, math, logging

from collections import OrderedDict
from datetime import datetime

logging.getLogger().setLevel(logging.INFO)

import numpy as np
import pandas as pd

import tifffile

import aicsGridNapari

################################################################################
def rawDataDriver(folderStr, dateStr, gridShape, gDataPath='', smallDict=None):
	"""
	Simplified version to open a raw data viewer

	#folderStr : name of the folder with the raw data
	#dateStr: yyyymmdd in file names, like 20200717__A01_G001_0009_ch2.tif
	"""
	if not gDataPath:
		import aicsDataPath
		gDataPath = aicsDataPath.getDataPath()

	aicsGridParam = mySetDefaultGridParams(gDataPath, folderStr, dateStr, gridShape)
	if aicsGridParam is None:
		print('rawDataDriver() got None aicsGridParam ???')
	else:
		aicsGridNapari.aicsGridNapari(aicsGridParam, smallDict=smallDict)

################################################################################
def myGetDefaultGridParams():
	aicsGridParam = OrderedDict()
	aicsGridParam['dataPath'] = ''
	aicsGridParam['folderStr'] = ''
	aicsGridParam['dateStr'] = ''

	aicsGridParam['path'] = ''
	aicsGridParam['prefixStr'] = ''
	aicsGridParam['commonShape'] =  () # shape of each stack in aicsAnalysis (already trimmed)
	aicsGridParam['commonVoxelSize'] = ()
	aicsGridParam['channelList'] = []
	aicsGridParam['gridShape'] = ()
	aicsGridParam['finalPostfixList'] = []
	aicsGridParam['trimPercent'] = None
	#aicsGridParam['doUseInclude'] = doUseInclude
	#aicsGridParam['doUseFirstLast'] = doUseFirstLast

	return aicsGridParam

################################################################################
def mySetDefaultGridParams(dataPath, folderStr, dateStr, gridShape, dataFolder='raw'):
	"""
	set up a default aicsGRidParam given a folder name

	parameters:
		dataFolder : is from (raw, aicsAnalysis), if aicsAnalysis can be folder name like aicsAnalysis2
	"""

	defaultTrimePercent = 15

	aicsGridParam = myGetDefaultGridParams()

	aicsGridParam['dataPath'] = dataPath
	aicsGridParam['folderStr'] = folderStr
	aicsGridParam['dateStr'] = dateStr

	if not os.path.isdir(dataPath):
		print('ERROR: mySetDefaultGridParams() did not find data path:', dataPath)
		return None

	# path
	if dataFolder == 'raw':
		path = os.path.join(dataPath, folderStr)
	else:
		path = os.path.join(dataPath, folderStr, dataFolder)
	if not os.path.isdir(path):
		print('ERROR: mySetDefaultGridParams() did not find path:', path)
		print('   did you specify "dataPath" properly? It is:', dataPath)
		print('   did you specify "folderStr" properly? It is:', folderStr)
		print('   did you specify "dateStr" properly? It is:', dateStr)
		return None
	aicsGridParam['path'] = path

	if not os.path.isdir(dataPath):
		print('ERROR: mySetDefaultGridParams() did not find date folder:', dataPath)
		return None

	# cell db
	cell_dbFile = folderStr + '_cell_db.csv'
	masterFilePath = os.path.join('aicsBatch', cell_dbFile)
	if os.path.isfile(masterFilePath):
		aicsGridParam['masterFilePath'] = masterFilePath
	else:
		aicsGridParam['masterFilePath'] = ''

	# prefix
	prefixStr = dateStr + '__A01_G001_'
	aicsGridParam['prefixStr'] = prefixStr

	#
	# try loading first _ch1/_ch2 to get shape and voxel
	ch1File = prefixStr + '0001_ch1.tif'
	ch1Path = os.path.join(path, ch1File)
	ch2File = prefixStr + '0001_ch2.tif'
	ch2Path = os.path.join(path, ch2File)
	if os.path.isfile(ch1Path):
		zVoxel, xVoxel, yVoxel, stackShape = readVoxelSize(ch1Path, getShape=True)
		commonShape = stackShape
		commonVoxelSize = (zVoxel, xVoxel, yVoxel)
	elif os.path.isfile(ch2Path):
		zVoxel, xVoxel, yVoxel, stackShape = readVoxelSize(ch2Path, getShape=True)
		commonShape = stackShape
		commonVoxelSize = (zVoxel, xVoxel, yVoxel)
	else:
		print('ERROR: mySetDefaultGridParams() did not find file for ch1/ch2 Tiff')
		print('  ', ch1Path)
		print('  ', ch2Path)
		return None

	aicsGridParam['commonVoxelSize'] = commonVoxelSize

	# if trimming, common shape is AFTER trimming
	#aicsGridParam['commonShape'] =  commonShape
	if dataFolder == 'raw':
		aicsGridParam['trimPercent'] = defaultTrimePercent
		aicsGridParam['commonShape'] = getTrimShape(commonShape, defaultTrimePercent)
	else:
		aicsGridParam['trimPercent'] = None # analysis is already trimmed
		aicsGridParam['commonShape'] = commonShape

	#aicsGridParam['path'] = path

	#aicsGridParam['masterFilePath'] = masterFilePath
	#aicsGridParam['path'] = path
	#aicsGridParam['prefixStr'] = prefixStr
	#aicsGridParam['commonShape'] =  commonShape# shape of each stack in aicsAnalysis (already trimmed)
	#aicsGridParam['commonVoxelSize'] = commonVoxelSize

	aicsGridParam['channelList'] = [1,2] # USER

	if dataFolder == 'raw':
		aicsGridParam['finalPostfixList'] = ['']
	else:
		aicsGridParam['finalPostfixList'] = ['', '_mask', '_labeled']

	aicsGridParam['gridShape'] = gridShape

	'''
	aicsGridParam['gridShape'] = () # USER
	aicsGridParam['finalPostfixList'] = finalPostfixList # USER
	aicsGridParam['trimPercent'] = trimPercent # USER
	#aicsGridParam['doUseInclude'] = doUseInclude
	#aicsGridParam['doUseFirstLast'] = doUseFirstLast
	'''

	aicsGridParam['doUseInclude'] = False # USER
	aicsGridParam['doUseFirstLast'] = False # USER

	return aicsGridParam

################################################################################
def readVoxelSize(path, getShape=False, verbose=False):
	"""
	is also in bimpy.util

	here i am return (z, x, y)
	"""

	with tifffile.TiffFile(path) as tif:
		xVoxel = 1
		yVoxel = 1
		zVoxel = 1

		try:
			tag = tif.pages[0].tags['XResolution']
			if tag.value[0]>0 and tag.value[1]>0:
				xVoxel = tag.value[1] / tag.value[0]
			else:
				print('   bStackHeader.loadHeader() error, got zero tag value?')
			if verbose: print('   bStackHeader.loadStack() xVoxel from TIFF XResolutions:', xVoxel)
		except (KeyError) as e:
			print('warning: bStackHeader.loadHeader() did not find XResolution')

		try:
			tag = tif.pages[0].tags['YResolution']
			if tag.value[0]>0 and tag.value[1]>0:
				yVoxel = tag.value[1] / tag.value[0]
			else:
				print('   bStackHeader.loadHeader() error, got zero tag value?')
			if verbose: print('   bStackHeader.loadStack() yVoxel from TIFF YResolutions:', yVoxel)
		except (KeyError) as e:
			print('warning: bStackHeader.loadHeader() did not find YResolution')

		# HOLY CRAP, FOUND IT QUICK
		imagej_metadata = tif.imagej_metadata
		if imagej_metadata is not None:
			try:
				#print('    imagej_metadata["spacing"]:', imagej_metadata['spacing'], type(imagej_metadata['spacing']))
				zVoxel = imagej_metadata['spacing']
				if verbose: print('    zVoxel from imagej_metadata["spacing"]:', imagej_metadata['spacing'])
			except (KeyError) as e:
				if verbose: print('warning: bStackHeader.loadHeader() did not find spacing')

		'''
		tag = tif.pages[0].tags['ResolutionUnit']
		print('ResolutionUnit:', tag.value)
		'''

		numImages = len(tif.pages)

		tag = tif.pages[0].tags['ImageWidth']
		xPixels = tag.value

		tag = tif.pages[0].tags['ImageLength']
		yPixels = tag.value

		myShape = (numImages, xPixels, yPixels)

		if getShape:
			return zVoxel, xVoxel, yVoxel, (myShape)
		else:
			return zVoxel, xVoxel, yVoxel

################################################################################
def parseMasterFile(masterFilePath, filePath, dfMasterFile=None):
	"""
	filePath: full RAW file name with _ch and .tif
	"""
	if dfMasterFile is not None:
		df = dfMasterFile
	else:
		if not os.path.isfile(masterFilePath):
			print('  ERROR: parseMasterFile() did not find masterFilePath:', masterFilePath)
			return None, None, None, None
		df = pd.read_csv(masterFilePath)

	tmpPath, tmpFilename = os.path.split(filePath)
	filename, ext = tmpFilename.split('.')

	#print('    parseMasterFile() loading .csv to get (uInclude, uFirstslice, uLastslice) for uFilename:', filename, 'from masterFilePath:', masterFilePath)

	#df = pd.read_csv(masterFilePath)

	uInclude = None # changed from True on 20200813
	firstSlice = None
	lastSlice = None

	baseFilename = filename.replace('_ch1', '')
	baseFilename = baseFilename.replace('_ch2', '')
	baseFilename = baseFilename.replace('_ch3', '')

	if df is not None:
		df2 = df.loc[df['uFilename'] == baseFilename, 'uFirstSlice']
		if df2.shape[0] == 0:
			print('  ERROR: parseMasterFile() did not find dfMasterCellDB uFilename:', baseFilename, 'in master file')
		else:
			thisLineDF = df[df['uFilename'] == baseFilename]

			# is it in uInclude
			tmpInclude = df.loc[df['uFilename'] == baseFilename, 'uInclude'].iloc[0]
			if pd.notnull(tmpInclude):
				uInclude = int(tmpInclude)
				#print('    read uFilename:', baseFilename, 'uInclude:', uInclude)
			else:
				#print('    ERROR: did not find "uInclude" for uFilename:', baseFilename)
				uInclude = False

			# firstslice
			tmpFirstSlice = df.loc[df['uFilename'] == baseFilename, 'uFirstSlice'].iloc[0]
			if pd.notnull(tmpFirstSlice):
				firstSlice = int(tmpFirstSlice)
				#print('    read uFilename:', baseFilename, 'uFirstSlice:', firstSlice)
			else:
				#print('    WARNING: did not find "uFirstSlice" for uFilename:', baseFilename)
				pass
			# lastslice
			tmpLastSlice = df.loc[df['uFilename'] == baseFilename, 'uLastSlice'].iloc[0]
			if pd.notnull(tmpLastSlice):
				lastSlice = int(tmpLastSlice)
				#print('    read uFilename:', baseFilename, 'uLastSlice:', lastSlice)
			else:
				#print('    WARNING: did not find "uLastSlice" for uFilename:', baseFilename)
				pass

			# uVascThreshold

	else:
		print('ERROR: pruneStackData() did not read df from masterFilePath:', masterFilePath)

	return baseFilename, uInclude, firstSlice, lastSlice

##############################################################
def trimStack(stackData, trimPercent, verbose=False):
	trimPixels = math.floor( trimPercent * stackData.shape[1] / 100 ) # ASSUMING STACKS ARE SQUARE
	trimPixels = math.floor(trimPixels / 2)
	if trimPixels > 0:
		if verbose: print('    trimming', trimPixels, 'lower/right pixels')
		if verbose: print('    original shape:', stackData.shape)
		thisHeight = stackData.shape[1] - trimPixels
		thisWidth = stackData.shape[2] - trimPixels
		stackData = stackData[:, 0:thisHeight, 0:thisWidth]
		if verbose: print('    final shape:', stackData.shape)
	else:
		print('    WARNING: trimStack() not trimming lower/right x/y !!!')

	return stackData

##############################################################
def getTrimShape(stackShape, trimPercent):
	trimPixels = math.floor( trimPercent * stackShape[1] / 100 ) # ASSUMING STACKS ARE SQUARE
	trimPixels = math.floor(trimPixels / 2)

	trimSlices = stackShape[0] # not changing slices
	trimHeight = stackShape[1] - trimPixels
	trimWidth = stackShape[2] - trimPixels

	return (trimSlices, trimHeight, trimWidth)
