"""
make a distance map from a mask
"""

import os, sys, time

import numpy as np
import scipy.ndimage

import tifffile

def _printStackParams(name, myStack):
	#print('  ', name, type(myStack), myStack.shape, myStack.dtype, 'dtype.char:', myStack.dtype.char, 'min:', np.min(myStack), 'max:', np.max(myStack))
	print('  .', name, myStack.shape, 'dtype:', myStack.dtype,
				'dtype.char:', myStack.dtype.char,
		)
	print('    ', 'min:', np.nanmin(myStack),
		'max:', np.nanmax(myStack),
		'mean:', np.nanmean(myStack))

def makeEdt(maskData, xVoxel, yVoxel, zVoxel):
	"""
	make a euclidean distance transform (map) from a mask
	"""
	_printStackParams('  maskData', maskData)

	# swap the mask
	# the euclidian distance from each of the "1" points (voxels) to
	# its nearest zero point.
	# computes the distance
	#	from non-zero (i.e. non-background) points to
	#	the nearest zero (i.e. background) point.
	maskData = np.logical_not(maskData)
	_printStackParams('  swapped maskData', maskData)

	if len(maskData.shape)==2:
		sampling = (xVoxel, yVoxel)
	elif len(maskData.shape)==3:
		sampling = (zVoxel, xVoxel, yVoxel)

	print('  .taking edt of mask', maskData.shape, '... please wait ...')
	edtData = scipy.ndimage.morphology.distance_transform_edt(maskData,
										sampling=sampling) #, return_distances=True)
	_printStackParams('  edtData float64', edtData)

	# convert float64 to float32
	print('  converting float64 to float32 ... will loose some very small decimal precision')
	edtData = edtData.astype(np.float32)
	_printStackParams('  edtData float32', edtData)

	return edtData

if __name__ == '__main__':
	#vascPath = '/Users/cudmore/data/nathan/Thresholded-Vessels-Tifs/Thresholded-Vessels-Tifs_big_2d.tif'
	# path to 3d vasc mask
	if 1:
		# san4 upper
		vascMaskPath = '/Users/cudmore/data/nathan/san4-top/san4-top-cd31/san4-top-cd31_big_3d.tif'
		hcn4MaskPath = '/Users/cudmore/data/nathan/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d.tif'
	xVoxel = 0.4971842
	yVoxel = 0.4971842
	zVoxel = 1

	# load masks
	print('loading original masks:')
	print('  vascMaskPath:', vascMaskPath)
	print('  hcn4MaskPath:', hcn4MaskPath)
	vascMaskData = tifffile.imread(vascMaskPath)
	hcn4MaskData = tifffile.imread(hcn4MaskPath)

	# debug, make it temporarily smaller so we can see what we get fast
	if 1:
		startPixel = 640
		stopPixel = startPixel + 3*startPixel
		print('DEBUG startPixel:', startPixel, 'stopPixel:', stopPixel)
		vascMaskData = vascMaskData[:, startPixel:-1, startPixel:stopPixel]
		hcn4MaskData = hcn4MaskData[:, startPixel:-1, startPixel:stopPixel]

	# edt will have um distance of every pixel to nearest vasculature
	vascEdtData = makeEdt(vascMaskData, xVoxel, yVoxel, zVoxel)

	# this is the most important line
	# take subset of pixels in vasc edt that is in hcn4 mask
	# np.where() return elements chosen from x or y depending on condition.
	#hcn4EdtData = vascEdtData[hcn4MaskData]
	hcn4EdtData = np.where(hcn4MaskData>0, vascEdtData, np.nan)
	_printStackParams('  hcn4EdtData', hcn4EdtData)

	# save vasc edt
	vascSavePath, tmpExt = os.path.splitext(vascMaskPath)
	vascSavePath += '_edt.tif'
	print('  saving vascSavePath:', vascSavePath)
	tifffile.imsave(vascSavePath, vascEdtData)

	# save hcn4 edt
	hcn4SavePath, tmpExt = os.path.splitext(hcn4MaskPath)
	hcn4SavePath += '_edt.tif'
	print('  saving hcn4SavePath:', hcn4SavePath)
	tifffile.imsave(hcn4SavePath, hcn4EdtData)

	# not inspect them in fiji
	# use min/max to set contrast to see edt as image

	# plot for 2d case
	if 0:
		import matplotlib.pyplot as plt
		import seaborn as sns
		print('plotting ...')
		fig, axs = plt.subplots(1, 2, sharex=False)
		im0 = axs[0].imshow(vaskMaskData)
		#im1 = axs[1].heatmap(edtData, xmin=0, xmax=10)
		im1 = sns.heatmap(vascEdtData, vmin=xVoxel*2, vmax=20, cbar=True, ax=axs[1])
		plt.show()
