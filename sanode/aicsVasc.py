"""
20200530
test aics segmentation on vasculature

on 'pip install napari'

	ERROR: aicsimageio 0.6.4 has requirement tifffile==0.15.1, but you'll have tifffile 2020.5.25 which is incompatible.

ERROR: aicsimageio 0.6.4 has requirement tifffile==0.15.1, but you'll have tifffile 2020.5.25 which is incompatible.
ERROR: aicsimageprocessing 0.7.3 has requirement aicsimageio>=3.1.2, but you'll have aicsimageio 0.6.4 which is incompatible.

"""

import os, sys, time, glob, logging

import copy
from collections import OrderedDict
from datetime import datetime

logging.getLogger().setLevel(logging.INFO)

import numpy as np
import scipy

import multiprocessing as mp

import bimpy

import aicsUtil
import aicsUtil2

from aicssegmentation.core.vessel import filament_3d_wrapper
from aicssegmentation.core.pre_processing_utils import edge_preserving_smoothing_3d

from my_suggest_normalization_param import my_suggest_normalization_param # clone of aics segmentation
from my_intensity_normalization import my_intensity_normalization

def vascDenRun(path, trimPercent=15, firstSlice=None, lastSlice=None, saveFolder='aicsAnalysis'):

	"""
		scale_x is set based on the estimated thickness of your target filaments.
		For example, if visually the thickness of the filaments is usually 3~4 pixels,
		then you may want to set scale_x as 1 or something near 1 (like 1.25).
		Multiple scales can be used, if you have filaments of very different thickness.

		cutoff_x is a threshold applied on the actual filter reponse to get the binary result.
		Smaller cutoff_x may yielf more filaments, especially detecting more dim ones and thicker segmentation,
		while larger cutoff_x could be less permisive and yield less filaments and slimmer segmentation.
	"""

	gStartTime = time.time()

	debug = False
	verbose = False

	filename, paramDict, stackDict = \
		aicsUtil.setupAnalysis(path, trimPercent, firstSlice=firstSlice, lastSlice=lastSlice, saveFolder=saveFolder)

	'''
	if stackDict is None or stackDict['raw']['data'] is None:
		# either uInclude is False or we did not find file
		print('=== *** === vascDen.vascDenRun() aborting path:', path)
		return False
	'''

	xVoxel = paramDict['xVoxel']
	yVoxel = paramDict['yVoxel']
	zVoxel = paramDict['zVoxel']

	#
	# parameters
	f3_param = paramDict['f3_param']
	medianKernelSize = paramDict['medianKernelSize']
	removeBelowThisPercent = paramDict['removeBelowThisPercent']
	removeSmallerThan = paramDict['removeSmallerThan']

	#
	# save path
	savePath = paramDict['saveBase']
	tmpFileNoExtension = paramDict['fileNameBase']
	'''
	tmpPath, tmpFile = os.path.split(path)
	tmpFileNoExtension, tmpExtension = tmpFile.split('.')
	savePath = os.path.join(tmpPath, saveFolder)
	if not os.path.isdir(savePath):
		os.mkdir(savePath)
	savePath = os.path.join(savePath, tmpFileNoExtension) # append to this with with _xxx.tif
	'''

	tiffHeader = paramDict['tiffHeader']

	#
	# load
	stackData = stackDict['raw']['data']
	'''
	logging.info('loading path: ' + path)
	#print('loading path:', path)
	#stackData = tifffile.imread(path)
	stackData, tiffHeader = bimpy.util.imread(path)
	print('  .loaded', stackData.shape, myIdx)
	'''

	# abb 2020091 laptop
	# expand stack in z s.t. each slice has 4x copies of *self above and below

	numSlices = stackData.shape[0]

	#
	# save raw to conserve memory
	rawSavePath = savePath + '.tif'
	print('  saving rawSavePath:', rawSavePath)
	#bimpy.util.imsave(rawSavePath, stackData, tifHeader=tiffHeader, overwriteExisting=True)
	#bimpy.util.imsave(rawSavePath, stackData, tifHeader=tiffHeader, overwriteExisting=True)
	bimpy.util.imsave2(rawSavePath, stackData, xVoxel, yVoxel, zVoxel, overwriteExisting=True)

	#_printStackParams('loaded stackData', stackData)

	#
	# sliding z
	# never sure if i should slidingz then median or median then slidingz ???
	#stackData = bimpy.util.morphology.slidingZ(stackData, upDownSlices=1)

	startTime = time.time()
	#medianKernelSize = (3,4,4)
	#medianKernelSize = (2,2,2)
	if verbose: print('  .median filter', path)
	stackData = bimpy.util.morphology.medianFilter(stackData, kernelSize=medianKernelSize)
	stopTime = time.time()
	if verbose: print('    .median filter' , stackData.dtype, 'done in ', round(stopTime-startTime,2), path)

	# give us a guess for our intensity_scaling_param parameters
	#low_ratio, high_ratio = my_suggest_normalization_param(stackData)

	# try per slice
	print('  .per slice my_suggest_normalization_param', path)
	normData = stackData.astype(np.float16)
	#normData = stackData.copy()
	normData[:] = 0
	for i in range(numSlices):
		oneSlice = stackData[i,:,:]
		low_ratio, high_ratio = my_suggest_normalization_param(oneSlice)
		#print(i, low_ratio, high_ratio)
		#low_ratio = 0.2

		#low_ratio -= 0.3
		#high_ratio -= 1

		#if low_ratio < 0:
		#	low_ratio = 0

		#theMin = np.min(oneSlice)
		#theMax = np.max(oneSlice)
		#print('    slice', i, 'min:', theMin, 'max:', theMax, 'snr:', theMax-theMin, 'low_ratio:', low_ratio, 'high_ratio:', high_ratio)

		intensity_scaling_param = [low_ratio, high_ratio]
		#sliceNormData = intensity_normalization(oneSlice, scaling_param=intensity_scaling_param)
		sliceNormData = my_intensity_normalization(oneSlice, scaling_param=intensity_scaling_param)
		normData[i,:,:] = sliceNormData
	if verbose: print('    .per slice my_suggest_normalization_param done', normData.dtype, path)

	#
	# just try to remove noise
	#removeBelowThisPercent = 0.11 # aicsCell uses 0.1, aicsVas uses 0.06
	paramDict['removeBelowThisPercent'] = removeBelowThisPercent
	normData = bimpy.util.morphology.threshold_remove_lower_percent(normData, removeBelowThisPercent=removeBelowThisPercent)

	# smoothing with edge preserving smoothing
	print('  .edge_preserving_smoothing_3d() ... please wait ... normData:', normData.shape, normData.dtype, path)
	try:
		if not debug:
			normData = edge_preserving_smoothing_3d(normData)
		else:
			#normData = normData
			pass
	except (AttributeError) as e:
		print('!!! my exception:', e)
		print('    path:', path)
		raise

	print('  .filament_3d_wrapper() ... please wait ... f3_param:', f3_param)
	startTime = time.time()
	if not debug:
		normData = filament_3d_wrapper(normData, f3_param)
	else:
		#normData = normData
		pass
	normData = normData.astype(np.uint8)
	stopTime = time.time()
	print('    .filament_3d_wrapper() took', round(stopTime-startTime,2), 'seconds', normData.dtype, path)
	#filamentData = filamentData > 0
	#_printStackParams('filamentData', filamentData)

	'''
	iterations = 1
	border_value = 1
	filamentData = scipy.ndimage.morphology.binary_dilation(filamentData, structure=None, border_value=border_value, iterations=iterations)
	filamentData = filamentData.astype(np.uint8)
	'''

	#
	# label
	#removeSmallerThan = 500 #80

	if verbose: print('  .labelling mask and removing small labels <', removeSmallerThan)

	# after this we are done with norm data, maybe delete it?
	labeledStack = bimpy.util.morphology.labelMask(normData) # uint32

	#
	# delete normData from memory
	normData = None

	labeledDataWithout, labeledDataRemoved, labelIdx, labelCount = \
			bimpy.util.morphology.removeSmallLabels2(labeledStack, removeSmallerThan, timeIt=True, verbose=False)

	#
	uniqueOrig, countsOrig = np.unique(labeledStack, return_counts=True)
	origNumLabels = len(uniqueOrig)
	#
	uniqueWithout, countsWithout = np.unique(labeledDataWithout, return_counts=True)
	remainingNumLabels = len(uniqueWithout)
	#
	uniqueRemoved, countsRemoved = np.unique(labeledDataRemoved, return_counts=True)
	removedNumLabels = len(uniqueRemoved)

	print('    origNumLabels:', origNumLabels)
	print('    remainingNumLabels:', remainingNumLabels)
	print('    removedNumLabels:', removedNumLabels)

	myPrettyPrint = np.asarray((uniqueRemoved, countsRemoved)).T
	#print(myPrettyPrint)

	#
	# final mask (directly from remaining labels)
	maskStack = labeledDataWithout > 0
	maskStack = maskStack.astype(np.uint8)

	#
	# save size of each label (plot with tests/testPlotLabels.py)
	'''
	labelSizeArray = np.array(labelCount)
	labelSizePath = os.path.join('/Users/cudmore/Desktop', tmpFileNoExtension + '_labelSizeList')
	np.save(labelSizePath, labelSizeArray)
	'''

	#
	# update cell_db.csv
	#aicsUtil.updateMasterCellDB(masterFilePath, filename, paramDict)

	#
	# save

	'''
	rawSavePath = savePath + '.tif'
	print('  saving rawSavePath:', rawSavePath)
	#bimpy.util.imsave(rawSavePath, stackData, tifHeader=tiffHeader, overwriteExisting=True)
	saveStackData = stackDict['raw']['data']
	bimpy.util.imsave(rawSavePath, saveStackData, tifHeader=tiffHeader, overwriteExisting=True)
	'''

	labeledSavePath = savePath + '_labeled.tif'
	print(f'  saving labeled x/y/z voxel is {xVoxel} {yVoxel} {zVoxel} {labeledSavePath}')
	#bimpy.util.imsave(labeledSavePath, labeledDataWithout, tifHeader=tiffHeader, overwriteExisting=True)
	bimpy.util.imsave2(labeledSavePath, labeledDataWithout, xVoxel, yVoxel, zVoxel, overwriteExisting=True)

	removedLabelsSavePath = savePath + '_labeled_removed.tif'
	print(f'  saving removed labeled x/y/z voxel is {xVoxel} {yVoxel} {zVoxel} {removedLabelsSavePath}')
	#bimpy.util.imsave(removedLabelsSavePath, labeledDataRemoved, tifHeader=tiffHeader, overwriteExisting=True)
	bimpy.util.imsave2(removedLabelsSavePath, labeledDataRemoved, xVoxel, yVoxel, zVoxel, overwriteExisting=True)

	maskSavePath = savePath + '_mask.tif'
	print(f'  saving mask x/y/z voxel is {xVoxel} {yVoxel} {zVoxel} {maskSavePath}')
	# ValueError: ImageJ does not support data type ?
	# maskStack = maskStack.astype(np.bool_)
	#bimpy.util.imsave(maskSavePath, maskStack, tifHeader=tiffHeader, overwriteExisting=True)
	bimpy.util.imsave2(maskSavePath, maskStack, xVoxel, yVoxel, zVoxel, overwriteExisting=True)


	# free memory
	stackData = None
	labeledDataWithout = None
	labeledDataRemoved = None
	maskStack= None

	# done
	gStopTime = time.time()
	tookSeconds = round(gStopTime-gStartTime,2)

	print('  .took', tookSeconds, 'seconds', round(tookSeconds/60,2), 'minutes', 'path:', path)

	return paramDict

if __name__ == '__main__':

	myTimer = bimpy.util.bTimer('aicsVas()')

	# run one file
	if 1:
		"""
		path = '/Users/cudmore/box/data/nathan/20200518/20200518__A01_G001_0003_ch2.tif'
		path = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0014_ch2.tif'
		path = '/Users/cudmore/Box/data/20200717/20200717__A01_G001_0014_ch2.tif'

		# after expanding with each slice with iteself above and below
		path = '/Users/cudmore/Box/data/20200717/20200717__A01_G001_0014a_ch2.tif'
		path = '/Users/cudmore/data/testing/20200717__A01_G001_0014_ch2.tif'

		# z padded stack (each slice is replicated above/below)
		path = '/Users/cudmore/data/testing/20200717__A01_G001_0014a_ch2.tif'

		masterFilePath = 'aicsBatch/20200717_cell_db.csv'
		#outFilePath = 'aicsBatch/20200717_cell_db_out.csv'
		"""

		trimPercent = 15

		# 20200924, this is a subset of entire grid (not a single stack)
		# i don't want a trim percent here???
		#path = '/home/cudmore/data/nathan/20200814_SAN3_BOTTOM_tail/20200814_SAN3_BOTTOM_tail_ch2.tif'

		##
		##
		# this is output of something like sanode/nathan_20200901.py
		#path = '/home/cudmore/data/nathan/SAN4/SAN4_head_ch2.tif'
		#path = '/home/cudmore/data/nathan/SAN4/SAN4_mid_ch2.tif'
		path = '/home/cudmore/data/nathan/SAN4/SAN4_tail_ch2.tif'

		path = '/media/cudmore/data/san-density/SAN3/SAN3_tail/SAN3_tail_ch2.tif'

		trimPercent = None # for the small subset, we don't trim it

		saveFolder = 'aicsAnalysis'

		uFirstSlice = None
		uLastSlice = None
		#baseFilename, uInclude, uFirstSlice, uLastSlice = aicsUtil2.parseMasterFile(masterFilePath, path)
		#print('uFirstSlice:', uFirstSlice, 'uLastSlice:', uLastSlice)
		#if uInclude:
		if 1:
			paramDict = vascDenRun(path, trimPercent=trimPercent, firstSlice=uFirstSlice, lastSlice=uLastSlice, saveFolder=saveFolder)
			#
			# todo: rewrite updateMasterCellDB
			#aicsUtil.updateMasterCellDB(outFilePath, path, paramDict)

	# run batch
	if 0:

		masterFilePath = 'aicsBatch/20200717_cell_db.csv'
		path = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_*_ch2.tif'

		filenames = glob.glob(path)
		print('proccessing', len(filenames), 'files')

		trimPercent = 15
		saveFolder = 'aicsAnalysis'

		cpuCount = mp.cpu_count()
		print('cpuCount:', cpuCount)
		cpuCount = 3 #aics code is taking up to > 7 GB per stack , can't run in parallel with only 32 GB !!!
		pool = mp.Pool(processes=cpuCount)

		#results = [pool.apply_async(vascDenRun, args=(file,myIdx+1)) for myIdx, file in enumerate(filenames)]

		#
		# build async pool
		numFilesToAnalyze = 0
		results = []
		for filePath in filenames:
			# file is full file path

			baseFilename, uInclude, uFirstSlice, uLastSlice = aicsUtil.parseMasterFile(masterFilePath, filePath)

			if uInclude:
				# path, trimPercent=trimPercent, firstSlice=uFirstSlice, lastSlice=uLastSlice, saveFolder=saveFolder
				args = [filePath, trimPercent, uFirstSlice, uLastSlice, saveFolder]
				oneResult = pool.apply_async(vascDenRun, args=args)
				results.append(oneResult)

				numFilesToAnalyze += 1

		#
		# run
		for idx, result in enumerate(results):
			print('=== running file', idx+1, 'of', numFilesToAnalyze)
			oneParamDict = result.get()
			print('\nDONE with idx:', idx, 'paramDict:', oneParamDict)
	#
	print(myTimer.elapsed())
