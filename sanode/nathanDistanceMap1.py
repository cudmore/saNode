"""
make a distance map from a mask

1) make vasc distance map
2) select hcn4 pixels from the vasc distance map

Note: scipy edt code is crashing on big stacks, to run san4 top
		need to split it into two, run separately, and then merge with postPRocess()
		see _tmpTop and _tmpBottom
"""

import os, sys, time

import numpy as np
import scipy.ndimage

import tifffile

import matplotlib.pyplot as plt
import seaborn as sns

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

	see:
		https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.distance_transform_edt.html
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

def run():
	dataPath = '/media/cudmore/data/heat-map/san4-raw'
	# path to 3d vasc mask
	if 0:
		# san4 top
		vascMaskPath = f'{dataPath}/san4-top/san4-top-cd31/san4-top-cd31_big_3d.tif'
		hcn4MaskPath = f'{dataPath}/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d.tif'
		# run twice on top (edt is crashing when using the whole mosaic)
		# after running both (_tmpTop, _tmpBottom) -->> run postProcess()
		#	to put them back together
		# vascMask and hcn4Mask are shape (104, 7104, 3552)
		# raw (640,640) after 0.15% trim is (592,592)
		# nathans imaris export has first col empty followed by 3x columns of data
		#stackPixelWidth = 592
		#stackPixelWidth = 640

		# 20210322, now trimming 15% from all of left/top/right/bottom
		#			ws previously just trimming the bottom
		#trimming 48 left/top/right/bottom pixels
		#original shape: (104, 640, 640)
		#final shape: (104, 544, 544)
		stackPixelWidth = 544

		startCol = stackPixelWidth
		stopCol = startCol + (3*stackPixelWidth)
		if 0:
			# tmpTop
			trimStr = '_tmpTop'
			startRow = stackPixelWidth
			stopRow = 3500
		if 1:
			# tmpBottom
			trimStr = '_tmpBottom'
			startRow = 3500
			stopRow = -1

	if 1:
		# san4 bottom
		vascMaskPath = f'{dataPath}/san4-bottom/san4-bottom-cd31/san4-bottom-cd31_big_3d.tif'
		hcn4MaskPath = f'{dataPath}/san4-bottom/san4-bottom-hcn4/san4-bottom-hcn4_big_3d.tif'
		trimStr = ''
		#stackPixelWidth = 592
		stackPixelWidth = 544
		startCol = 0
		stopCol = startCol + (4*stackPixelWidth)
		startRow = 0
		#stopRow = 4480
		stopRow = 3806 # our big_3d.tif represents original fv300 grid with lots of missing tiles
						# we only analyzed a subset and exported from Imaris

	xVoxel = 0.4971842
	yVoxel = 0.4971842
	zVoxel = 1

	# load masks
	print('loading original masks:')
	print('  vascMaskPath:', vascMaskPath)
	print('  hcn4MaskPath:', hcn4MaskPath)
	vascMaskData = tifffile.imread(vascMaskPath)
	hcn4MaskData = tifffile.imread(hcn4MaskPath)

	_printStackParams('  vascMaskData:', vascMaskData)
	_printStackParams('  hcn4MaskData:', hcn4MaskData)

	# debug, make it temporarily smaller so we can see what we get fast
	if 1:
		print('DEBUG startRow:', startRow, 'stopRow:', stopRow)
		print('      startCol:', startCol, 'stopCol:', stopCol)
		vascMaskData = vascMaskData[:, startRow:stopRow, startCol:stopCol]
		hcn4MaskData = hcn4MaskData[:, startRow:stopRow, startCol:stopCol]

	_printStackParams('  trimmed vascMaskData:', vascMaskData)
	_printStackParams('  trimmed hcn4MaskData:', hcn4MaskData)

	# edt will have um distance of every pixel to nearest vasculature
	vascEdtData = makeEdt(vascMaskData, xVoxel, yVoxel, zVoxel)

	# this is the most important line
	# take subset of pixels in vasc edt that is in hcn4 mask
	# np.where() return elements chosen from x or y depending on condition.
	#hcn4EdtData = vascEdtData[hcn4MaskData]
	hcn4EdtData = np.where(hcn4MaskData>0, vascEdtData, 0)
	_printStackParams('  hcn4EdtData', hcn4EdtData)

	#mergedData = np.where(np.isnan(mergedData), 0, mergedData)

	# save vasc edt
	vascSavePath, tmpExt = os.path.splitext(vascMaskPath)
	vascSavePath += trimStr + '_edt.tif'
	print('  saving vascSavePath:', vascSavePath)
	tifffile.imsave(vascSavePath, vascEdtData)

	# save hcn4 edt
	hcn4SavePath, tmpExt = os.path.splitext(hcn4MaskPath)
	hcn4SavePath += trimStr + '_edt.tif'
	print('  saving hcn4SavePath:', hcn4SavePath)
	tifffile.imsave(hcn4SavePath, hcn4EdtData)

	# now inspect them in fiji
	# use min/max to set contrast to see edt as image


	# plot for 2d case
	if 0:
		print('plotting ...')
		fig, axs = plt.subplots(1, 2, sharex=False)
		im0 = axs[0].imshow(vaskMaskData)
		#im1 = axs[1].heatmap(edtData, xmin=0, xmax=10)
		im1 = sns.heatmap(vascEdtData, vmin=xVoxel*2, vmax=20, cbar=True, ax=axs[1])
		plt.show()

def plot2d(data0, data1=None):
	print('plotting ...')
	numCol = 2
	if data1 is None:
		numCol = 1
	fig, axs = plt.subplots(1, numCol, sharex=False)
	if numCol == 1:
		axs = [axs]
	xVoxel = 0.4
	vMax = 30
	im0 = sns.heatmap(data0, vmin=xVoxel, vmax=vMax, cbar=True, ax=axs[0])
	im0.axes.get_xaxis().set_visible(False)
	im0.axes.get_yaxis().set_visible(False)
	axs[0].spines['left'].set_visible(False)
	axs[0].spines['top'].set_visible(False)
	axs[0].spines['right'].set_visible(False)
	axs[0].spines['bottom'].set_visible(False)

	if data1 is not None:
		im1 = sns.heatmap(data1, vmin=xVoxel, vmax=vMax, cbar=True, ax=axs[1])
		im1.axes.get_xaxis().set_visible(False)
		im1.axes.get_yaxis().set_visible(False)
		axs[1].spines['left'].set_visible(False)
		axs[1].spines['top'].set_visible(False)
		axs[1].spines['right'].set_visible(False)
		axs[1].spines['bottom'].set_visible(False)

	#fig.colorbar(pos, ax=ax1)
	#
	plt.show()

def postProcess():
	"""
	load and combine tmpTop/tmpBottom edt
	"""
	dataDir = '/media/cudmore/data/heat-map/san4-raw'
	# san4 top tmpTop
	topHcn4EdtPath = f'{dataDir}/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d_tmpTop_edt.tif'
	print('loading topHcn4EdtPath:', topHcn4EdtPath)
	hcn4EdtData_top = tifffile.imread(topHcn4EdtPath)
	_printStackParams('  hcn4EdtData_top:', hcn4EdtData_top)

	# san4 top tmpBottom
	bottomHcn4EdtPath = f'{dataDir}/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d_tmpBottom_edt.tif'
	print('loading bottomHcn4EdtPath:', bottomHcn4EdtPath)
	hcn4EdtData_bottom = tifffile.imread(bottomHcn4EdtPath)
	_printStackParams('  hcn4EdtData_bottom:', hcn4EdtData_bottom)

	# merge tmpTop and tmpBottom
	print('merging')
	mergedData = np.concatenate((hcn4EdtData_top, hcn4EdtData_bottom), axis=1)
	_printStackParams('  mergedData:', mergedData)

	# convert np.nan to 0 (napari will not show with nan)
	print('converting np.nan to 0')
	mergedData = np.where(np.isnan(mergedData), 0, mergedData)

	if 0:
		# add back in first row and first column, wrt original olympus
		stackPixelWidth = 640
		print('adding back in first row/col stackPixelWidth:', stackPixelWidth)
		slices = mergedData.shape[0]
		#
		tmpNumRows = mergedData.shape[1]
		tmpFirstCol = np.zeros((slices,tmpNumRows,stackPixelWidth))
		print('  adding tmpFirstCol:', tmpFirstCol.shape)
		mergedData = np.concatenate((tmpFirstCol, mergedData), axis=2)
		#
		tmpNumCols = mergedData.shape[2]
		tmpFirstRow = np.zeros((slices,stackPixelWidth,tmpNumCols))
		print('  adding tmpFirstRow:', tmpFirstRow.shape)
		mergedData = np.concatenate((tmpFirstRow, mergedData), axis=1)
		print('  new shape for mergedData:', mergedData.shape, mergedData.dtype)

	if 1:
		print('removing distances > 200')
		mergedData = np.where(mergedData>200, 0, mergedData)

	_printStackParams('  final mergedData:', mergedData)

	# save merged
	savePath = f'{dataDir}/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d_edt.tif'
	print('saving savePath:', savePath)
	tifffile.imsave(savePath, mergedData)

	##
	sys.exit()
	##

	# set 0 to nan
	mergedData = np.where(mergedData==0, np.nan, mergedData)

	# take average intensity projection
	mergedData = np.nanmean(mergedData, axis=0)

	plot2d(mergedData)

if __name__ == '__main__':
	if 1:
		run()

	if 0:
		postProcess()
