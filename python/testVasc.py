"""
20200803, returning to this, does better than vascDen

20200530
test aics segmentation on vasculature

on 'pip install napari'

	ERROR: aicsimageio 0.6.4 has requirement tifffile==0.15.1, but you'll have tifffile 2020.5.25 which is incompatible.

ERROR: aicsimageio 0.6.4 has requirement tifffile==0.15.1, but you'll have tifffile 2020.5.25 which is incompatible.
ERROR: aicsimageprocessing 0.7.3 has requirement aicsimageio>=3.1.2, but you'll have aicsimageio 0.6.4 which is incompatible.

"""

import sys, time

import numpy as np
import scipy

import tifffile

import napari

import bimpy

from aicssegmentation.core.vessel import filament_3d_wrapper
from aicssegmentation.core.pre_processing_utils import edge_preserving_smoothing_3d, image_smoothing_gaussian_3d

from my_suggest_normalization_param import my_suggest_normalization_param # clone of aics segmentation
from my_intensity_normalization import my_intensity_normalization # clone of aics segmentation

def _printStackParams(name, myStack):
	print('  ', name, myStack.shape, myStack.dtype, 'dtype.char:', myStack.dtype.char,
		'min:', np.min(myStack),
		'max:', np.max(myStack),
		'mean:', np.mean(myStack),
		'std:', np.std(myStack),
		)

def slidingZ(imageStack, upDownSlices=1, verbose=False):
	print('  .slidingZ() upDownSlices:', upDownSlices)

	if verbose: _printStackParams('input', imageStack)

	slidingz = imageStack.copy()
	m = imageStack.shape[0]
	for i in range(m):
		firstSlice = i - upDownSlices
		lastSlice = i + upDownSlices
		if firstSlice < 0:
			firstSlice = 0
		if lastSlice > m-1:
			lastSlice = m-1
		
		slidingz[i,:,:] = np.max(imageStack[firstSlice:lastSlice+1,:,:], axis=0)
		
	if verbose: _printStackParams('output', slidingz)

	return slidingz

def medianFilter(imageStack, kernelSize=(2,2,2), verbose=False):
	"""
	"""
	print('  .myMedianFilter() kernelSize:', kernelSize, '... please wait')
	
	if verbose: _printStackParams('input', imageStack)
		
	startTime = time.time()
	
	result = scipy.ndimage.median_filter(imageStack, size=kernelSize)
	
	if verbose: _printStackParams('output', result)

	stopTime = time.time()
	print('    myMedianFilter took', round(stopTime-startTime,2), 'seconds')
	
	return result

def myRun(path, saveNumber=1, doNapari=False):

	"""
	
	Parameters:
		saveNumber: save in folder analysis>saveNumber>
		
		scale_x is set based on the estimated thickness of your target filaments.
		For example, if visually the thickness of the filaments is usually 3~4 pixels,
		then you may want to set scale_x as 1 or something near 1 (like 1.25).
		Multiple scales can be used, if you have filaments of very different thickness.
	
		cutoff_x is a threshold applied on the actual filter reponse to get the binary result.
		Smaller cutoff_x may yielf more filaments, especially detecting more dim ones and thicker segmentation,
		while larger cutoff_x could be less permisive and yield less filaments and slimmer segmentation.
	"""
	f3_param=[[1, 0.01]]
	f3_param=[[5, 0.001], [3, 0.001]]
	
	startTimeMaster = time.time()

	#stackData = tifffile.imread(path)
	stackData, tiffHeader = bimpy.util.bTiffFile.imread(path)
	numSlices = stackData.shape[0]
	
	_printStackParams('stackData', stackData)
	xVoxel = tiffHeader['xVoxel']
	yVoxel = tiffHeader['yVoxel']
	zVoxel = tiffHeader['zVoxel']
	print('  xVoxel:', xVoxel, 'yVoxel:', yVoxel, 'zVoxel:', zVoxel)
	
	stackData = slidingZ(stackData, upDownSlices=1)
	
	stackData = medianFilter(stackData)

	# give us a guess for our intensity_scaling_param parameters
	#low_ratio, high_ratio = my_suggest_normalization_param(stackData)

	#
	# try per slice
	print('  per slice my_intensity_normalization')
	normData = stackData.astype(np.float64)
	normData[:] = 0
	for i in range(numSlices):
		oneSlice = stackData[i,:,:]
		low_ratio, high_ratio = my_suggest_normalization_param(oneSlice)
				
		#low_ratio = 0.2
		low_ratio -= 0.2
		high_ratio -= 1
		
		if low_ratio < 0 :
			low_ratio = 0
		
		intensity_scaling_param = [low_ratio, high_ratio]
		sliceNormData = my_intensity_normalization(oneSlice, scaling_param=intensity_scaling_param)
		normData[i,:,:] = sliceNormData
		
		#print('  ', i, 'of', numSlices, 'intensity_normalization() low_ratio:', low_ratio, 'high_ratio:', high_ratio, 'slice min:', np.min(sliceNormData), 'slice max:', np.max(sliceNormData))
	
	_printStackParams('final normData', normData) # this is np.float64

	#sys.exit()
	
	'''
	#intensity_scaling_param = [0.0, 22.5]
	intensity_scaling_param = [low_ratio, high_ratio]
	print('    === intensity_normalization() intensity_scaling_param:', intensity_scaling_param)
	
	# intensity normalization
	print('    === calling intensity_normalization()')
	normData = intensity_normalization(stackData, scaling_param=intensity_scaling_param)
	_printStackParams('normData', normData)
	'''
	
	debug = 0
	
	# smooth data
	if not debug:
		# smoothing with edge preserving smoothing 
		startTime = time.time()
		print('  === calling edge_preserving_smoothing_3d()')
		smoothData = edge_preserving_smoothing_3d(normData)
		_printStackParams('smoothData', smoothData)
		stopTime = time.time()
		print('  edge_preserving_smoothing_3d took', round(stopTime-startTime,2), 'seconds')
	else:
		smoothData = normData
		
	# filament data
	if not debug:
		print('  === calling filament_3d_wrapper() ... SLOW ... f3_param:', f3_param)
		startTime = time.time()
		filamentData = filament_3d_wrapper(smoothData, f3_param)
		#filamentData = filamentData.astype(np.uint8)
		stopTime = time.time()
		print('  filament_3d_wrapper took', round(stopTime-startTime,2), 'seconds')
	else:
		filamentData = smoothData
	_printStackParams('  filamentData', filamentData)
	
	filamentData = filamentData > 0
	filamentData = filamentData.astype(np.uint8)
	filamentData[filamentData>0] = 1
	_printStackParams('  final filamentData', filamentData)
	
	#filamentData2 = slidingZ(filamentData, upDownSlices=1)
	
	#
	# dilate by one
	if 1:
		dilatedData = bimpy.util.morphology.binary_dilation(filamentData, iterations=1)
		_printStackParams('  dilatedData', dilatedData)
	else:
		dilatedData = filamentData
		
	#filledData = bimpy.util.morphology.binary_fill_holes(dilatedData)
	#_printStackParams('  filledData', filledData)
	
	#
	# label stack
	labeledData = bimpy.util.morphology.labelMask(dilatedData)
	labelMin = np.min(labeledData)
	labelMax = np.max(labeledData)
	print('  labeledData min:', labelMin, 'max:', labelMax, 'path:', path)
	
	#
	# remove small labels
	# need to make a list of small labels and then remove with 1 line assignment (otherwise takes ~2 min)
	removeIfSmallerThan = 400 # remove small labels
	print('  removeIfSmallerThan:', removeIfSmallerThan)
	startTime = time.time()
	labelList = []
	smallLabelList = []
	if not debug:
		for i in range(labelMax+1):
			numInLabel = np.count_nonzero(labeledData==i)
			labelList.append(numInLabel)
			if i>1 and numInLabel < removeIfSmallerThan:
				smallLabelList.append(i)
				#print('   label:', i, 'has', numInLabel)
				# remove small labels
				#labeledData[labeledData==i] = 0
			if i==417:
				print('xxx', i, numInLabel)
					
	smallLabelMatrix = np.isin(labeledData, smallLabelList)
	labeledData1 = labeledData.copy()
	labeledData1[smallLabelMatrix] = 0 #remove small labels
	
	numSmall = len(smallLabelList)
	# remove
	
	print('  numSmall labels:', numSmall)
	stopTime = time.time()
	print('  remove small labels took', round(stopTime-startTime,2), 'seconds')
	_printStackParams('  labeledData', labeledData)
	
	#
	# final mask
	finalMask = labeledData.copy()
	finalMask[labeledData>0] = 1
	finalMask = finalMask.astype(np.uint8)
	_printStackParams('  finalMask', finalMask)
	
	#
	# erode by one
	finalMask = bimpy.util.morphology.binary_erosion(finalMask, iterations=1)
	_printStackParams('  finalMask', finalMask)

	#
	# save
	
	# label list (pto plot as a histogram)
	labelSizeArray = np.array(labelList)
	np.save("/Users/cudmore/Desktop/labelSizes", labelSizeArray)
	
	stopTimeMaster = time.time()
	print('  testVas.myRun() took', round(stopTimeMaster-startTimeMaster,2), 'seconds')

	#
	# napari
	if doNapari:
		print('opening in napari')
		scale = (zVoxel, xVoxel, yVoxel)
		with napari.gui_qt():
			viewer = napari.Viewer(title='xxx')
		
			blending = 'additive'
			opacity = 1.0
			
			minContrast = 0
			maxContrast = 180
			myImageLayer = viewer.add_image(stackData, scale=scale, contrast_limits=(minContrast, maxContrast),
								blending=blending, opacity=opacity, colormap='green', visible=True, name='stackData')
		
			'''
			minContrast = 0
			maxContrast = 1
			myImageLayer = viewer.add_image(normData, scale=scale, contrast_limits=(minContrast, maxContrast),
								blending=blending, opacity=opacity, colormap='gray', visible=True, name='normData')
			'''
			
			minContrast = 0
			maxContrast = 1
			myImageLayer = viewer.add_image(filamentData, scale=scale, contrast_limits=(minContrast, maxContrast),
								blending=blending, opacity=opacity, colormap='blue', visible=True, name='filamentData')
		
			minContrast = 0
			maxContrast = 1
			myImageLayer = viewer.add_labels(labeledData, scale=scale,
								blending=blending, opacity=opacity, visible=True, name='labeledData')
		
			minContrast = 0
			maxContrast = 1
			myImageLayer = viewer.add_labels(labeledData1, scale=scale,
								blending=blending, opacity=opacity, visible=True, name='labeledData1')
		
			minContrast = 0
			maxContrast = 1
			myImageLayer = viewer.add_image(finalMask, scale=scale, contrast_limits=(minContrast, maxContrast),
								blending=blending, opacity=opacity, colormap='cyan', visible=True, name='finalMask')
		
			'''
			minContrast = 0
			maxContrast = 1
			myImageLayer = viewer.add_image(filamentData2, scale=scale, contrast_limits=(minContrast, maxContrast),
								opacity=0.6, colormap='red', visible=True, name='filamentData2')
			'''

if __name__ == '__main__':

	startTime = time.time()
	
	path = '/Users/cudmore/box/data/nathan/20200518/analysis2/20200518__A01_G001_0003_ch2_raw.tif'
	
	path = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0014_ch2.tif'
	
	myRun(path, doNapari=True)
	
	stopTime = time.time()
	print('done in', round(stopTime-startTime,2), 'seconds. Single run with path:', path)
	
	
	