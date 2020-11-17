"""
20201101
use _mask.tif directly to make edt
"""

import os, sys

import numpy as np
import scipy

import tifffile

import bimpy

def _printStackParams(name, myStack):
	#print('  ', name, type(myStack), myStack.shape, myStack.dtype, 'dtype.char:', myStack.dtype.char, 'min:', np.min(myStack), 'max:', np.max(myStack))
	print('  ', name, myStack.shape, 'dtype:', myStack.dtype,
				'dtype.char:', myStack.dtype.char,
		)
	print('  ', 'min:', np.nanmin(myStack),
		'max:', np.nanmax(myStack),
		'mean:', np.nanmean(myStack))

def aicsDistMap(path, maskStart=None, maskStop=None):
	"""
	Make a distance map where each pixel gets a value
	The value is the distance of the pixel to the nearest pixel in the mask

	path: path to either
		*_ch1.tif
		*_ch2.tif
	maskStart: first good slice
	maskStop: last good slice
		From: (maskStart, maskStop) = aicsBlankSlices.getTopBottom(path)

	"""

	print('aicsDistMap() path:', path)

	# convert _ch1.tif to _ch1_mask.tif
	maskPath, tmpExt = os.path.splitext(path)
	maskPath += '_mask.tif'

	# get voxels
	xVoxel, yVoxel, zVoxel = bimpy.util.bTiffFile.readVoxelSize(maskPath)
	print('  x/y/z voxel is:', xVoxel, yVoxel, zVoxel)

	# load the _mask
	maskData = tifffile.imread(maskPath)
	_printStackParams('  0 maskData', maskData)

	# todo: use something like this
	#maskData = aicsBlankSlices.blankOutStack(maskData, maskStart, maskStop, fillValue=False)
	if maskStart is not None:
		print(f'  aicsDistMap() is excluding mask slices 0:{maskStart}')
		maskData[0:maskStart, :, :] = False #np.nan
	if maskStop is not None:
		print(f'  aicsDistMap() is excluding mask slices {maskStop}+1:-1')
		maskData[maskStop+1:-1, :, :] = False #np.nan

	# swap the mask
	# the euclidian distance from each of the "1" points (voxels) to its nearest zero point.
	# computes the distance
	#	from non-zero (i.e. non-background) points to the nearest zero (i.e. background) point.
	maskData = np.logical_not(maskData)
	_printStackParams('  1 maskData', maskData)

	myTimer = bimpy.util.bTimer('  making edt')

	print('  making edt ... please wait ...')

	sampling = (zVoxel, xVoxel, yVoxel)
	edtData = scipy.ndimage.morphology.distance_transform_edt(maskData,
										sampling=sampling) #, return_distances=True)
	_printStackParams('  edtData float64', edtData)

	# convert float64 to float32
	print('  converting float64 to float32 ... will loos some very small decimal precision')
	edtData = edtData.astype(np.float32)
	_printStackParams('  edtData float32', edtData)

	# blank edt based on maskStart/maskStop
	# todo: use something like this
	#edtData = aicsBlankSlices.blankOutStack(edtData, maskStart, maskStop, fillValue=np.nan)
	if maskStart is not None:
		print(f'  aicsDistMap() is excluding edt slices 0:{maskStart}')
		edtData[0:maskStart, :, :] = np.nan
	if maskStop is not None:
		print(f'  aicsDistMap() is excluding edt slices {maskStop}+1:-1')
		edtData[maskStop+1:-1, :, :] = np.nan

	_printStackParams('  edtData final', edtData)

	print('  ', myTimer.elapsed())

	# save doThisChannel edt
	savePath, tmpExt = os.path.splitext(path)
	savePath += '_edt.tif'

	print('  saving savePath:', savePath)
	#tifffile.imsave(savePath, edtData)
	bimpy.util.imsave2(savePath, edtData, xVoxel, yVoxel, zVoxel, overwriteExisting=True)

if __name__ == '__main__':
	import aicsBlankSlices

	path = '/media/cudmore/data/san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch1.tif'
	path = '/media/cudmore/data/san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch2.tif'
	
	path = '/media/cudmore/data/san-density/SAN1/SAN1_tail/aicsAnalysis/SAN1_tail_ch2.tif'

	(maskStart, maskStop) = aicsBlankSlices.getTopBottom(path)

	# we require start/stop
	if maskStart is None or maskStop is None:
		print('  error: aicsDistMap.__main__ did not get start/stop for path', path)
	else:
		aicsDistMap(path, maskStart, maskStop)

	##
	##
	sys.exit()
	##
	##

	path = '/media/cudmore/data/san-density/SAN3/SAN3_tail/aicsAnalysis/SAN3_tail_ch2.tif'
	maskStartStop = (17, 41)
	doThisChannel = 1

	'''
	# load the stack
	myStack = bimpy.bStack(path=path, loadImages=True, loadTracing=False)

	# get the mask
	maskData = myStack.getStack('mask', doThisChannel)
	#maskData = maskData.astype(np.uint8)
	_printStackParams('1 maskData', maskData)
	tifffile.imsave('/home/cudmore/Desktop/mask1.tif', maskData)
	'''

	maskPath = '/media/cudmore/data/san-density/SAN3/SAN3_tail/aicsAnalysis/SAN3_tail_ch1_mask.tif'
	maskData = tifffile.imread(maskPath)
	_printStackParams('0 maskData', maskData)
	tifffile.imsave('/home/cudmore/Desktop/mask1.tif', maskData)

	# blank out upper/lower mask
	maskData[0:maskStartStop[0], :, :] = False #np.nan
	maskData[maskStartStop[1]:-1, :, :] = False #np.nan
	_printStackParams('2 maskData', maskData)
	tifffile.imsave('/home/cudmore/Desktop/mask2.tif', maskData)

	# the euclidian distance from each of the "1" points (voxels) to its nearest zero point.
	# computes the distance
	#	from non-zero (i.e. non-background) points to the nearest zero (i.e. background) point.
	# swap mask
	# original 1 is in mask, 0 is background
	# new 1 is in background, 0 is in mask
	if 1:
		maskData = np.logical_not(maskData)
	if 0:
		maskData[maskData==1] = 10
		maskData[maskData==0] = 1
		maskData[maskData==10] = 0
	_printStackParams('3 maskData', maskData)
	tifffile.imsave('/home/cudmore/Desktop/mask3.tif', maskData)

	#print('  maskData:', maskData.shape)

	# generate edt
	myTimer = bimpy.util.bTimer('making edt')
	#scale = (1, 0.1, 0.1)
	sampling = (1, 0.1, 0.1)
	# edtData is float32
	'''
	edtData = bimpy.util.morphology.euclidean_distance_transform( maskData,
							hullMask = None,
							scale=(1,1,1))
	'''
	# edtData is np.float64
	edtData = scipy.ndimage.morphology.distance_transform_edt(maskData,
										sampling=sampling) #, return_distances=True)
	# debug
	#edtData = np.zeros(maskData.shape, dtype=np.float32)

	# blank out edt value above/below good portion to analyze
	edtData[0:maskStartStop[0], :, :] = np.nan #np.nan
	edtData[maskStartStop[1]:-1, :, :] = np.nan #np.nan
	_printStackParams('edtData', edtData)
	tifffile.imsave('/home/cudmore/Desktop/edt.tif', edtData)
	print(myTimer.elapsed())

	# convert edt to 8-bit (assuming no distances > 255
	'''
	edtMax = np.nanmax(edtData)
	if edtMax < 255:
		print(f'  converting edt to 8-bit, edtMax:{edtMax}')
		edtData = edtData.astype(np.uint8)
	else:
		print(f'  did not convert edt to 8-bit, edtMax:{edtMax}')
	'''

	# convert float64 to float32
	edtData = edtData.astype(np.float32)

	 # save doThisChannel edt
	savePath, tmpExt = os.path.splitext(path)
	# remove _ch1 _ch2
	savePath = savePath.replace('_ch1', '')
	savePath = savePath.replace('_ch2', '')
	# append the channel we just created the edt for
	savePath += f'_ch{doThisChannel}'

	savePath += '_edt.tif'
	print('  saving savePath:', savePath)
	tifffile.imsave(savePath, edtData)
