"""
20200807
"""

import json

import numpy as np

import bimpy

from my_suggest_normalization_param import my_suggest_normalization_param # clone of aics segmentation
from my_intensity_normalization import my_intensity_normalization

from aicsUtil import setupAnalysis
from aicsUtil import _printStackParams
from aicsOneNapari import aicsOneNapari

################################################################################
def cellDenRun(path, trimPercent=None, verbose=False):
	print('cellDen.myRun() path:', path)

	filename, paramDict, stackDict = \
			setupAnalysis(path, trimPercent = trimPercent, \
			firstSlice=None, lastSlice=None, saveFolder='aicsAnalysis')
	#filename, paramDict, stackDict = setupAnalysis(path, trimPercent, masterFilePath=masterFilePath)

	# debug x/y/z  voxel
	#print('cellDenRun got paramDict:')
	#print(json.dumps(paramDict, indent=4))

	xVoxel = paramDict['xVoxel']
	yVoxel = paramDict['yVoxel']
	zVoxel = paramDict['zVoxel']

	if stackDict['raw']['data'] is None:
		print('=== *** === cellDen.myRun() aborting, got None stack data')
		return None

	# set the algorithm
	paramDict['algorithm'] = 'cellDen'

	# get some local variables
	stackData = stackDict['raw']['data']
	tiffHeader = paramDict['tiffHeader']

	#print('cellDenRun() got tiffHeader:', tiffHeader)

	#saveBase = paramDict['saveBase']
	#saveBase2 = paramDict['saveBase2']
	savePath = paramDict['saveBase']

	numSlices = stackData.shape[0]

	#
	# algorithm
	#

	numSlices = stackData.shape[0]

	currentStack = stackData

	'''
	print('  ', 'running my_suggest_normalization_param() and my_intensity_normalization()')
	#normData = stackData.copy()
	normData = stackData.astype(np.float32)
	for i in range(numSlices):
		oneSlice = currenStack[i,:,:]
		low_ratio, high_ratio = my_suggest_normalization_param(oneSlice)

		#print(i, low_ratio, high_ratio)

		intensity_scaling_param = [low_ratio, high_ratio]
		#sliceNormData = intensity_normalization(oneSlice, scaling_param=intensity_scaling_param)
		sliceNormData = my_intensity_normalization(oneSlice, scaling_param=intensity_scaling_param)
		normData[i,:,:] = sliceNormData
	_printStackParams('normData', normData)

	currentStack = normData
	'''

	#
	# median filter
	'''
	print('  ', 'running medianFilter ...')
	medianKernelSize = (3, 5, 5)
	filteredStack = bimpy.util.morphology.medianFilter(currentStack, kernelSize=medianKernelSize)
	'''

	# gaussian
	# will not accept np.float16
	gaussianKernelSize = (1,1,1)
	paramDict['gaussianKernelSize'] = gaussianKernelSize
	filteredStack = bimpy.util.morphology.gaussianFilter(currentStack, kernelSize=gaussianKernelSize, verbose=False)
	if verbose: _printStackParams('filteredStack', filteredStack)

	stackDict['filtered']['data'] = filteredStack
	#paramDict['medianKernelSize'] = medianKernelSize

	currentStack = filteredStack

	#
	# threshold
	removeBelowThisPercent = 0.1 # vasc channel is 0.06
	paramDict['removeBelowThisPercent'] = removeBelowThisPercent
	thresholdStack = bimpy.util.morphology.threshold_remove_lower_percent(currentStack, removeBelowThisPercent=removeBelowThisPercent)
	paramDict['thresholdAlgorithm'] = 'threshold_remove_lower_percent'
	#paramDict['thresholdScale'] = myScale

	'''
	for i in range(numSlices):
		currentSlice = currentStack[i,:,:]
		print(i, np.min(currentSlice), np.max(currentSlice))
	'''

	#thresholdStack = bimpy.util.morphology.threshold_min(currentStack, min=15)

	# otsu
	# trying otsu because data from 20200518 looks like there are 2 sets of intensities???
	'''
	thresholdStack = bimpy.util.morphology.threshold_otsu(currentStack)
	paramDict['thresholdAlgorithm'] = 'threshold_otsu'
	'''

	# see: https://github.com/AllenInstitute/aics-segmentation/blob/master/lookup_table_demo/playground_st6gal1.ipynb
	'''
	if verbose: print('  ', 'running MO_threshold ...')
	from aicssegmentation.core.MO_threshold import MO
	object_minArea = 200 #1200
	thresholdStack, object_for_debug = MO(currentStack, global_thresh_method='tri', object_minArea=object_minArea, return_object=True)
	_printStackParams('thresholdStack', thresholdStack)
	'''

	currentStack = thresholdStack

	#
	# dilate
	#thresholdStack = bimpy.util.morphology.binary_dilation(currentStack, iterations=2)

	#stackDict['threshold']['data'] = thresholdStack

	finalMask = currentStack

	#
	# fill holes
	finalMask = bimpy.util.morphology.binary_fill_holes(currentStack)
	if verbose: _printStackParams('finalMask', finalMask)

	currentStack = finalMask

	#
	# label and remove smaller than (to remove noise)
	labeledMask = bimpy.util.morphology.labelMask(currentStack)
	removeSmallerThan = 400
	paramDict['removeSmallerThan'] = removeSmallerThan
	labeledMask, returnSmallLabels, labelIndices, labelCounts = \
		bimpy.util.morphology.removeSmallLabels2(labeledMask, removeSmallerThan=removeSmallerThan)

	labeledMask = labeledMask > 0
	labeledMask = labeledMask.astype(np.uint8)

	currentStack = labeledMask
	finalMask = labeledMask

	#
	# erode
	#bimpy.util.morphology.binary_erosion(currentStack, iterations=2)

	#
	# edt
	# edt ? distance from background to hcn4 cells?
	# edt requires (finalMask AND convex hull)

	"""
		need a cross channel edt, something like this

		these_hcn1_pixels = stackDict1['mask']==1 # pixels in hcn1 mask
		_printStackParams('these_hcn1_pixels', these_hcn1_pixels)
		edtFinal = stackDict2['edt'].copy()
		edtFinal[:] = np.nan
		edtFinal[these_hcn1_pixels] = stackDict2['edt'][these_hcn1_pixels]	# grab hcn1 pixels from vascular edt
		stackDict1['edt'] = edtFinal
		_printStackParams('  ch1 edt', edtFinal)
	"""

	#
	# save
	#mySave(saveBase, saveBase2, stackDict, tiffHeader, paramDict)

	#
	# update master cell db
	#updateMasterCellDB(masterFilePath, filename, paramDict)

	# save raw to conserve memory
	rawSavePath = savePath + '.tif'
	print(f'  saving raw x/y/z voxel is {xVoxel} {yVoxel} {zVoxel} {rawSavePath}')
	#bimpy.util.imsave(rawSavePath, stackData, tifHeader=tiffHeader, overwriteExisting=True)
	bimpy.util.imsave2(rawSavePath, stackData, xVoxel, yVoxel, zVoxel, overwriteExisting=True)

	'''
	filteredStack
	filteredSavePath = savePath + '_filtered.tif'
	print('  saving filteredSavePath:', filteredSavePath)
	bimpy.util.imsave(filteredSavePath, filteredStack, tifHeader=tiffHeader, overwriteExisting=True)
	'''

	maskSavePath = savePath + '_mask.tif'
	print(f'  saving mask x/y/z voxel is {xVoxel} {yVoxel} {zVoxel} {maskSavePath}')
	#bimpy.util.imsave(maskSavePath, finalMask, tifHeader=tiffHeader, overwriteExisting=True)
	bimpy.util.imsave2(maskSavePath, finalMask, xVoxel, yVoxel, zVoxel, overwriteExisting=True)

	return paramDict

if __name__ == '__main__':

	path = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0014_ch1.tif'
	path = '/Users/cudmore/data/testing/20200717__A01_G001_0014a_ch1.tif'

	#path = '/home/cudmore/data/nathan/SAN4/SAN4_tail_ch1.tif'
	path = '/media/cudmore/data/san-density/SAN4/SAN4_head_ch1.tif'
	path = '/media/cudmore/data/san-density/SAN4/SAN4_mid_ch1.tif'
	path = '/media/cudmore/data/san-density/SAN4/SAN4_tail_ch1.tif'

	path = '/media/cudmore/data/san-density/SAN3/SAN3_tail/SAN3_tail_ch1.tif'

	# for merged (2 x 2) stacks, don't trim
	#trimPercent = 15
	trimPercent = None

	paramDict = cellDenRun(path, trimPercent)

	'''
	print('paramDict:')
	print(json.dumps(paramDict, indent=4))
	'''

	doNapari = False
	if doNapari:
		aicsOneNapari(path, channels=[1])
