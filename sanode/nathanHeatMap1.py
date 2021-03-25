"""
"""

import os
import numpy as np

import tifffile

def _printStackParams(name, myStack):
	#print('  ', name, type(myStack), myStack.shape, myStack.dtype, 'dtype.char:', myStack.dtype.char, 'min:', np.min(myStack), 'max:', np.max(myStack))
	print('  .', name, myStack.shape, 'dtype:', myStack.dtype,
				'dtype.char:', myStack.dtype.char,
		)
	print('    ', 'min:', np.nanmin(myStack),
		'max:', np.nanmax(myStack),
		'mean:', np.nanmean(myStack))

def makeDensityMap(path, chunkSize, thisStat='sum', doVolumeFraction=True, ignore0=False):
	"""
	path: (str) full path to a big .tif file
		should be a binary mask (not raw data)
	chunkSize: (int) specifies the width/height in pixels
		for each output pixel in heatmap
	thisStat: ('sum', 'mean')
	ignore0: True for edt, we had to set 'missing values' to 0

	for some reason 'san4-top-hcn4_big_3d_edt.tif' had 6-8 pixels maxed out????
	set anything > 300 um to nan

	returns:
		tifData
		heatMapOut
	"""
	print('makeDensityMap() path:', path)
	print('  chunkSize:', chunkSize)
	print('  thisStat:', thisStat)
	print('  doVolumeFraction:', doVolumeFraction)
	print('  ignore0:', ignore0)

	tifData = tifffile.imread(path)
	tifShape = tifData.shape
	print('  tifData.shape:', tifData.shape)

	if ignore0:
		tifData = np.where(tifData==0, np.nan, tifData)

	# now done in nathanDistanceMap1.py
	#if os.path.split(path)[1] == 'san4-top-hcn4_big_3d_edt.tif':
	#	errorDist = 25
	#	print('*** removing edt distances >', errorDist)
	#	tifData = np.where(tifData>errorDist, np.nan, tifData)

	if len(tifShape) == 2:
		tifRows = tifShape[0]
		tifCols = tifShape[1]
	elif len(tifShape) == 3:
		tifSlices = tifShape[0]
		tifRows = tifShape[1]
		tifCols = tifShape[2]

	# rows/cols to step through (calculate density for each)
	numRows = int(tifRows / chunkSize)
	numCols = int(tifCols / chunkSize)
	print('  heatmap numRows:', numRows, 'numCols:', numCols)

	# make output np array
	heatMapOut = np.zeros((numRows,numCols), dtype=np.float32)

	for row in range(numRows):
		startRow = row * chunkSize
		stopRow = startRow + chunkSize
		for col in range(numCols):
			startCol = col * chunkSize
			stopCol = startCol + chunkSize

			if len(tifShape) == 2:
				chunkData = tifData[startRow:stopRow, startCol:stopCol]
			elif len(tifShape) == 3:
				chunkData = tifData[:, startRow:stopRow, startCol:stopCol]

			# sum pixels in mask within current chunk
			if thisStat == 'sum':
				sumPixels = np.nansum(chunkData)
			elif thisStat == 'mean':
				sumPixels = np.nanmean(chunkData)
			if not doVolumeFraction and sumPixels > 300:
				print('   *** warning: got a BIG distance row:', row, 'col:', col, 'sum:', sumPixels)
			if sumPixels > 2**32:
				print('  *** warning: overrun at row:', row, 'col:', col, 'sumPixels:', sumPixels)

			# we need to calculate the % of mask pixels out of total # pixels
			# normalize to number of pixels in 2d/3d chunk
			# here we are not really using pixels in chunk, causes sumPixels to become super small
			if doVolumeFraction:
				# for binary mask using np.nansum()
				if len(tifShape) == 2:
					pixelsInChunk = tifRows * tifCols
					volumeFraction = sumPixels / pixelsInChunk
				elif len(tifShape) == 3:
					pixelsInChunk = tifRows * tifCols * tifSlices
					volumeFraction = sumPixels / pixelsInChunk
			else:
				# for distance map using np.nanmean()
				volumeFraction = sumPixels
			#print('row:', row, 'col:', col, 'pixelsInChunk:', pixelsInChunk, 'volumeFraction:', volumeFraction)

			heatMapOut[row,col] = volumeFraction

	return tifData, heatMapOut

def run_volume_fraction():
	"""
    original shape: (86, 640, 640)
    final shape: (86, 544, 544)

	IGNORE: raw (640,640) after 0.15% trim is (592,592)
	"""
	#dataPath = '/Users/cudmore/data/nathan'
	dataPath = '/media/cudmore/data/heat-map/san4-raw'
	pathList = []
	if 0:
		# san4 top/bottom cd31
		pathList = [
			f'{dataPath}/san4-top/san4-top-cd31/san4-top-cd31_big_3d.tif',
			f'{dataPath}/san4-bottom/san4-bottom-cd31/san4-bottom-cd31_big_3d.tif'
			]
		thisStat = 'sum'
		doVolumeFraction = True
		ignore0 = False
	if 0:
		# san4 top/bottom hcn4
		pathList = [
			f'{dataPath}/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d.tif',
			f'{dataPath}/san4-bottom/san4-bottom-hcn4/san4-bottom-hcn4_big_3d.tif'
			]
		thisStat = 'sum'
		doVolumeFraction = True
		ignore0 = False

	if 1:
		# hcn4 dist map
		# REQUIRES nathanDistanceMap1.py OUTPUT !!!!!
		# REMEMBER TO IGNORE DISTANCE == 0
		titleStr = 'san4 hcn4 dist to vasc'
		pathList = [
			f'{dataPath}/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d_edt.tif',
			f'{dataPath}/san4-bottom/san4-bottom-hcn4/san4-bottom-hcn4_big_3d_edt.tif'
			]
		thisStat = 'mean'
		doVolumeFraction = False
		ignore0 = True

	# raw (640,640) after 0.15% trim is (592,592)
	#chunkSize = 296
	# not trimmed
	#chunkSize = 320 # 160 # pixels
	# new trimming 15% from left/top/right/bottom
	#	original shape: (86, 640, 640)
    #	final shape: (86, 544, 544)
	chunkSize = int(544/2)

	print('run_volume_fraction()')
	print('pathList:', pathList)
	print('  thisStat:', thisStat)
	print('  doVolumeFraction:', doVolumeFraction)
	print('  chunkSize:', chunkSize)

	tifData = [None] * len(pathList) # from makeDensityMap
	volumeFraction = [None] * len(pathList) # from makeDensityMap
	volumeFractionNorm = [None] * len(pathList) # create this
	for idx, path in enumerate(pathList):
		#print('path:', path)
		tifData[idx], volumeFraction[idx] = makeDensityMap(path, chunkSize,
									thisStat=thisStat, doVolumeFraction=doVolumeFraction, ignore0=ignore0)
		#_printStackParams(f'{idx}  tifData', tifData[idx])
		#_printStackParams(f'{idx}  volumeFraction', volumeFraction[idx])

	# find max across all volumeFraction heatmaps
	theMax = 0
	for idx, vf in enumerate(volumeFraction):
		thisMax = np.nanmax(vf)
		if thisMax > theMax:
			theMax = thisMax

		fileName = os.path.split(pathList[idx])[1]
		print(f'{idx} {fileName} max: {thisMax}')
		_printStackParams('  ', vf)

	# normalize all vf to the same max (theMax)
	for idx, vf in enumerate(volumeFraction):
		fileName = os.path.split(pathList[idx])[1]
		print(f'{idx} {fileName} normalize to {theMax}')
		_printStackParams('  before vf', vf)
		volumeFractionNorm[idx] = vf / theMax
		_printStackParams('  after volumeFractionNorm', volumeFractionNorm[idx])

	#
	# save both the (original, norm) heat map
	for idx, path in enumerate(pathList):
		tmpPath, tmpExt = os.path.splitext(path)
		#
		savePath = tmpPath + '_cs' + str(chunkSize) + '_heatmap.tif'
		print('  saving heat map as:', savePath)
		_printStackParams('  vf', volumeFraction[idx])
		tifffile.imwrite(savePath, volumeFraction[idx])
		#
		saveNormPath = tmpPath + '_cs' + str(chunkSize) + '_heatmap_norm.tif'
		print('  saving norm heat map as:', saveNormPath)
		_printStackParams('  vf', volumeFractionNorm[idx])
		tifffile.imwrite(saveNormPath, volumeFractionNorm[idx])

		#
		# print raw heat map
		mTmp, nTmp = volumeFraction[idx].shape
		for i in range(mTmp):
			rowStr = ''
			for j in range(nTmp):
				rowStr += str(volumeFraction[idx][i,j]) + '\t'
			print(rowStr + '\n')

	#
	# plot
	import matplotlib.pyplot as plt

	print('plotting ...')
	cmap = 'inferno' #'Greens' # 'inferno'
	numPerIdx = 3
	n = len(volumeFraction) * numPerIdx # 2 plots for each original (max tif, norm vf)
	fig, axs = plt.subplots(1, n, sharex=False)
	for idx, vfn in enumerate(volumeFractionNorm):
		vf = volumeFraction[idx]
		tif = tifData[idx]
		tifMaxProject = np.nanmax(tif, axis=0)

		colIdx = idx * numPerIdx

		# was for mask
		#im0 = axs[colIdx].imshow(tifMaxProject, vmin=0, vmax=1)
		im0 = axs[colIdx].imshow(tifMaxProject, cmap=cmap)
		im0.axes.get_xaxis().set_visible(False)
		im0.axes.get_yaxis().set_visible(False)
		axs[colIdx].title.set_text('tifMaxProject')

		im1 = axs[colIdx+1].imshow(vf, vmin=0, vmax=theMax, cmap=cmap) # for edt, this has actual um distances
		im1.axes.get_xaxis().set_visible(False)
		im1.axes.get_yaxis().set_visible(False)
		axs[colIdx+1].title.set_text('vf')

		im2 = axs[colIdx+2].imshow(vfn, vmin=0, vmax=1, cmap=cmap)
		im2.axes.get_xaxis().set_visible(False)
		im2.axes.get_yaxis().set_visible(False)
		axs[colIdx+2].title.set_text('vfn')

	#plt.colorbar(im2,fraction=0.046, pad=0.04)

	#
	plt.show()


if __name__ == '__main__':
	run_volume_fraction()
	# to plot output, use nathanHeatMapPlot.py
	#myPlot()
