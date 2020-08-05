"""
20200530
test aics segmentation on vasculature

on 'pip install napari'

	ERROR: aicsimageio 0.6.4 has requirement tifffile==0.15.1, but you'll have tifffile 2020.5.25 which is incompatible.

ERROR: aicsimageio 0.6.4 has requirement tifffile==0.15.1, but you'll have tifffile 2020.5.25 which is incompatible.
ERROR: aicsimageprocessing 0.7.3 has requirement aicsimageio>=3.1.2, but you'll have aicsimageio 0.6.4 which is incompatible.

"""

import os, sys, time, glob, logging

from collections import OrderedDict
from datetime import datetime

logging.getLogger().setLevel(logging.INFO)

import numpy as np
import scipy

#import tifffile

import multiprocessing as mp
#import dask
#import dask.array as da

#import napari

import bimpy

from aicssegmentation.core.vessel import filament_3d_wrapper
from aicssegmentation.core.pre_processing_utils import edge_preserving_smoothing_3d, image_smoothing_gaussian_3d

from my_suggest_normalization_param import my_suggest_normalization_param # clone of aics segmentation
from my_intensity_normalization import my_intensity_normalization

def _printStackParams(name, myStack):
	print('  ', name, myStack.shape, myStack.dtype, 'dtype.char:', myStack.dtype.char,
		'min:', np.min(myStack),
		'max:', np.max(myStack),
		'mean:', np.mean(myStack),
		'std:', np.std(myStack),
		)

"""
raw
labeled (also save by manual edits)
labeled_removed # small labels
labeled_removed_manual # after manual edits, resave _labeled (should be able to revert)
mask
hull
edt
"""

def myGetDefaultParamDict():
	"""
	Using order here to save files with _1_, _2_, _3_, ...
	"""
	paramDict = OrderedDict()
	paramDict['analysisDate'] = ''
	paramDict['analysisTime'] = ''
	
	paramDict['f3_param'] =[[3, 0.001], [5, 0.001], [7, 0.001]]
	paramDict['medianKernelSize'] = (2,2,2)
	paramDict['removeSmallerThan'] = 2000 #600 #500
	
	return paramDict
	
def myRun(path, paramDict, myIdx=0, saveFolder='analysisAics'):

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

	f3_param = paramDict['f3_param']
	medianKernelSize = paramDict['medianKernelSize']
	removeSmallerThan = paramDict['removeSmallerThan']
	
	# save path
	tmpPath, tmpFile = os.path.split(path)
	tmpFileNoExtension, tmpExtension = tmpFile.split('.')
	savePath = os.path.join(tmpPath, saveFolder)
	if not os.path.isdir(savePath):
		os.mkdir(savePath)
	savePath = os.path.join(savePath, tmpFileNoExtension) # append to this with with _xxx.tif 
	
	#print('savePath:', savePath)
	
	#f3_param=[[1, 0.01]]
	#f3_param=[[5, 0.001], [3, 0.001]]
	#f3_param=[[3, 0.001], [5, 0.001], [7, 0.001]] # 8 is no good
	
	logging.info('loading path: ' + path)
	#print('loading path:', path)
	#stackData = tifffile.imread(path)
	stackData, tifHeader = bimpy.util.imread(path)
	print('  .loaded', stackData.shape, myIdx)
	
	numSlices = stackData.shape[0]
	#_printStackParams('loaded stackData', stackData)
	
	# never sure if i should slidingz then median or median then slidingz ???
	stackData = bimpy.util.morphology.slidingZ(stackData, upDownSlices=1)

	startTime = time.time()
	#medianKernelSize = (3,4,4)
	#medianKernelSize = (2,2,2)
	print('  .median filter', myIdx)
	stackData = bimpy.util.morphology.medianFilter(stackData, kernelSize=medianKernelSize)
	stopTime = time.time()
	print('    .median filter' , stackData.dtype, 'done in ', round(stopTime-startTime,2), myIdx)
		
	# give us a guess for our intensity_scaling_param parameters
	#low_ratio, high_ratio = my_suggest_normalization_param(stackData)

	# try per slice
	print('  .per slice my_suggest_normalization_param', myIdx)
	normData = stackData.astype(np.float16)
	#normData = stackData.copy()
	normData[:] = 0
	for i in range(numSlices):
		oneSlice = stackData[i,:,:]
		low_ratio, high_ratio = my_suggest_normalization_param(oneSlice)
		#print(i, low_ratio, high_ratio)
		#low_ratio = 0.2
		
		'''
		low_ratio -= 0.3
		high_ratio -= 1
		
		if low_ratio < 0:
			low_ratio = 0
		'''
		
		theMin = np.min(oneSlice)
		theMax = np.max(oneSlice)
		#print('    slice', i, 'min:', theMin, 'max:', theMax, 'snr:', theMax-theMin, 'low_ratio:', low_ratio, 'high_ratio:', high_ratio)

		intensity_scaling_param = [low_ratio, high_ratio]
		#sliceNormData = intensity_normalization(oneSlice, scaling_param=intensity_scaling_param)
		sliceNormData = my_intensity_normalization(oneSlice, scaling_param=intensity_scaling_param)
		normData[i,:,:] = sliceNormData
	print('    .per slice my_suggest_normalization_param done', normData.dtype, myIdx)
			
	# smoothing with edge preserving smoothing 
	print('  .edge_preserving_smoothing_3d() normData:', normData.shape, normData.dtype, myIdx)
	try:
		smoothData = edge_preserving_smoothing_3d(normData)
	except (AttributeError) as e:
		print('!!! my exception:', e)
		print('    path:', path)
		raise
	
	#_printStackParams('smoothData', smoothData)

	print('  .filament_3d_wrapper() f3_param:', f3_param)
	startTime = time.time()
	filamentData = filament_3d_wrapper(smoothData, f3_param)
	filamentData = filamentData.astype(np.uint8)
	stopTime = time.time()
	print('    .filament_3d_wrapper() took', round(stopTime-startTime,2), 'seconds', filamentData.dtype, myIdx)
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

	print('  .labelling mask and removing small labels <', removeSmallerThan)

	labeledStack = bimpy.util.morphology.labelMask(filamentData) # uint32
	
	'''
	labeledStack, removedLabelStack, labelSizeList = bimpy.util.morphology.removeSmallLabels(labeledStack, removeSmallerThan=removeSmallerThan)	
	'''
	
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
	labelSizeArray = np.array(labelCount)
	labelSizePath = os.path.join('/Users/cudmore/Desktop', tmpFileNoExtension + '_labelSizeList')
	np.save(labelSizePath, labelSizeArray)
	
	#
	# save
	rawSavePath = savePath + '.tif'
	print('  saving rawSavePath:', rawSavePath)
	bimpy.util.imsave(rawSavePath, stackData, tifHeader=tifHeader, overwriteExisting=True)
	
	labeledSavePath = savePath + '_labeled.tif'
	print('  saving labeledSavePath:', labeledSavePath)
	bimpy.util.imsave(labeledSavePath, labeledDataWithout, tifHeader=tifHeader, overwriteExisting=True)
	
	removedLabelsSavePath = savePath + '_labeled_removed.tif'
	print('  saving labeledSavePath:', labeledSavePath)
	bimpy.util.imsave(removedLabelsSavePath, labeledDataRemoved, tifHeader=tifHeader, overwriteExisting=True)
	
	maskSavePath = savePath + '_mask.tif'
	print('  saving maskSavePath:', maskSavePath)
	bimpy.util.imsave(maskSavePath, maskStack, tifHeader=tifHeader, overwriteExisting=True)
	
		
	gStopTime = time.time()
	tookSeconds = round(gStopTime-gStartTime,2)
	
	print('  .took', tookSeconds, 'seconds', tookSeconds/60, 'minutes', 'path:', path)
	return tookSeconds, path

def myLoad(path):
	#print('myLoad() path:', path)
	stackData = tifffile.imread(path)
	#print('    loaded', stackData.shape, path)
	return stackData
	

if __name__ == '__main__':

	# run one file
	if 1:
		path = '/Users/cudmore/box/data/nathan/20200518/20200518__A01_G001_0003_ch2.tif'
		
		path = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0014_ch2.tif'
		
		paramDict = myGetDefaultParamDict()
		
		myRun(path, paramDict=paramDict)
	
	# run batch
	if 0:
		path = '/Users/cudmore/box/data/nathan/20200518/20200518__A01_G001_*_ch2.tif'
		filenames = glob.glob(path)
		print('proccessing', len(filenames), 'files')
 		
		startTime = time.time()
		
		cpuCount = mp.cpu_count()
		cpuCount -= 2
		pool = mp.Pool(processes=cpuCount)
		results = [pool.apply_async(myRun, args=(file,myIdx+1)) for myIdx, file in enumerate(filenames)]
		for idx, result in enumerate(results):
			#print(result.get())
			result.get()
        			
		stopTime = time.time()
		print('finished in', round(stopTime-startTime,2), 'seconds')


