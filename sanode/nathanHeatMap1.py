"""
"""

import os
import numpy as np

import tifffile

def makeDensityMap(path, chunkSize):
	"""
	path: (str) full path to a big .tif file
		should be a binary mask (not raw data)
	chunkSize: (int) specifies the width/height in pixels
		for each output pixel in heatmap

	returns:
		tifData
		heatMapOut
	"""
	print('makeDensityMap() path:', path)
	print('  chunkSize:', chunkSize)

	tifData = tifffile.imread(path)
	tifShape = tifData.shape
	print('  tifData.shape:', tifData.shape)

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
			sumPixels = np.sum(chunkData)
			#print('row:', row, 'col:', col, 'sum:', sumPixels)
			if sumPixels > 2**32:
				print('  *** warning: overrun at row:', row, 'col:', col, 'sumPixels:', sumPixels)

			# we need to calculate the % of mask pixels out of total # pixels
			# normalize to number of pixels in 2d/3d chunk
			# here we are not really using pixels in chunk, causes sumPixels to become super small
			if len(tifShape) == 2:
				pixelsInChunk = tifRows * tifCols
				volumeFraction = sumPixels / pixelsInChunk
			elif len(tifShape) == 3:
				pixelsInChunk = tifRows * tifCols * tifSlices
				volumeFraction = sumPixels / pixelsInChunk

			#print('row:', row, 'col:', col, 'pixelsInChunk:', pixelsInChunk, 'volumeFraction:', volumeFraction)

			heatMapOut[row,col] = volumeFraction

	return tifData, heatMapOut

def run():
	dataPath = '/Users/cudmore/data/nathan'
	pathList = []
	if 0:
		# san4 top/bottom cd31
		pathList = [
			f'{dataPath}/san4-top/san4-top-cd31/san4-top-cd31_big_3d.tif',
			f'{dataPath}/san4-bottom/san4-bottom-cd31/san4-bottom-cd31_big_3d.tif'
			]
	if 1:
		# san4 top/bottom hcn4
		pathList = [
			f'{dataPath}/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d.tif',
			f'{dataPath}/san4-bottom/san4-bottom-hcn4/san4-bottom-hcn4_big_3d.tif'
			]

	chunkSize = 320 # 160 # pixels
	tifData = [None] * len(pathList) # from makeDensityMap
	volumeFraction = [None] * len(pathList) # from makeDensityMap
	volumeFractionNorm = [None] * len(pathList) # create this
	for idx, path in enumerate(pathList):
		#print('path:', path)
		tifData[idx], volumeFraction[idx] = makeDensityMap(path, chunkSize)

	# find max across all volumeFraction heatmaps
	theMax = 0
	for idx, vf in enumerate(volumeFraction):
		thisMax = np.max(vf)
		if thisMax > theMax:
			theMax = thisMax

		fileName = os.path.split(pathList[idx])[1]
		print(f'{idx} {fileName} max: {thisMax}')

	# normalize all vf to the same max (theMax)
	for idx, vf in enumerate(volumeFraction):
		volumeFractionNorm[idx] = vf / theMax

	#
	# save both the (original, norm) heat map
	for idx, path in enumerate(pathList):
		tmpPath, tmpExt = os.path.splitext(path)
		#
		savePath = tmpPath + '_cs' + str(chunkSize) + '_heatmap.tif'
		print('  saving heat map as:', savePath)
		tifffile.imwrite(savePath, volumeFraction[idx])
		#
		saveNormPath = tmpPath + '_cs' + str(chunkSize) + '_heatmap_norm.tif'
		print('  saving norm heat map as:', saveNormPath)
		tifffile.imwrite(saveNormPath, volumeFractionNorm[idx])

	#
	# plot
	import matplotlib.pyplot as plt

	n = len(volumeFraction) * 2 # 2 plots for each original (max tif, norm vf)
	fig, axs = plt.subplots(1, n, sharex=False)
	for idx, vfn in enumerate(volumeFractionNorm):
		tif = tifData[idx]
		tifMaxProject = np.max(tif, axis=0)

		colIdx = idx * 2

		im0 = axs[colIdx].imshow(tifMaxProject, vmin=0, vmax=1)
		im0.axes.get_xaxis().set_visible(False)
		im0.axes.get_yaxis().set_visible(False)

		im1 = axs[colIdx+1].imshow(vfn, vmin=0, vmax=1)
		im1.axes.get_xaxis().set_visible(False)
		im1.axes.get_yaxis().set_visible(False)

	#plt.colorbar(im2,fraction=0.046, pad=0.04)

	#
	plt.show()

def myPlot():
	# plot heat maps from tif

	if 0:
		titleStr = 'cd31'
		san4Top = '/Users/cudmore/data/nathan/san4-top/san4-top-cd31/san4-top-cd31_big_3d_cs320_heatmap_norm.tif'
		san4Bottom = '/Users/cudmore/data/nathan/san4-bottom/san4-bottom-cd31/san4-bottom-cd31_big_3d_cs320_heatmap_norm.tif'

	if 1:
		titleStr = 'hcn4'
		san4Top = '/Users/cudmore/data/nathan/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d_cs320_heatmap_norm.tif'
		san4Bottom = '/Users/cudmore/data/nathan/san4-bottom/san4-bottom-hcn4/san4-bottom-hcn4_big_3d_cs320_heatmap_norm.tif'

	topTif = tifffile.imread(san4Top)
	bottomTif = tifffile.imread(san4Bottom)

	# mask out 0 values so they are displayed as transparent (white)
	topTif = np.ma.masked_where(topTif == 0, topTif)
	bottomTif = np.ma.masked_where(bottomTif == 0, bottomTif)

	import matplotlib.pyplot as plt
	fig, axs = plt.subplots(1, 3, sharey=True)
	fig.suptitle(titleStr)

	cmap = 'inferno' #'Greens' # 'inferno'
	vmin = 0.000
	vmax = 1

	#fig, axs = plt.subplots(1, 2, sharex=False)
	im0 = axs[0].imshow(topTif, vmin=vmin, vmax=vmax, cmap=cmap)
	#im0.set_clim([vmin, vmax])
	im0.axes.get_xaxis().set_visible(False)
	im0.axes.get_yaxis().set_visible(False)
	axs[0].spines['left'].set_visible(False)
	axs[0].spines['top'].set_visible(False)
	axs[0].spines['right'].set_visible(False)
	axs[0].spines['bottom'].set_visible(False)

	im1 = axs[2].imshow(bottomTif, vmin=vmin, vmax=vmax, cmap=cmap)
	im1.axes.get_xaxis().set_visible(False)
	im1.axes.get_yaxis().set_visible(False)
	axs[2].spines['left'].set_visible(False)
	axs[2].spines['top'].set_visible(False)
	axs[2].spines['right'].set_visible(False)
	axs[2].spines['bottom'].set_visible(False)

	#
	# make 1d of each row going from top to bottom
	m1,n = topTif.shape
	print('top m1:', m1)
	yDensityLineTop = range(m1)
	densityLineTop = np.zeros(m1)
	topMean = np.mean(topTif)
	for i in range(m1):
		# top
		oneRowMax = np.max(topTif[i,:])
		oneRowSum = np.sum(topTif[i,:])
		oneRowMean = np.mean(topTif[i,:])
		oneRowMean = (oneRowMean-topMean) / topMean
		densityLineTop[i] = oneRowMax
	m2,n = bottomTif.shape
	print('bottom m2:', m2)
	yDensityLineBottom = range(m1+m2)
	densityLineBottom = np.zeros(m1+m2) * np.nan
	bottomMean = np.mean(bottomTif)
	for i in range(m2):
		# bottom
		oneRowMax = np.max(bottomTif[i,:])
		oneRowSum = np.sum(bottomTif[i,:])
		oneRowMean = np.mean(bottomTif[i,:])
		oneRowMean = (oneRowMean-topMean) / topMean #USING TOP MEAN
		densityLineBottom[m1+i] = oneRowMax
	#
	#axs = [axs]
	axs[1].scatter(densityLineTop, yDensityLineTop,
					vmin=vmin,
					vmax=vmax,
					c=densityLineTop, cmap=cmap)
	axs[1].scatter(densityLineBottom, yDensityLineBottom,
					vmin=vmin,
					vmax=vmax,
					c=densityLineBottom, cmap=cmap)
	#axs[1].invert_yaxis()
	axs[1].get_yaxis().set_visible(False)
	axs[1].spines['left'].set_visible(False)
	axs[1].spines['top'].set_visible(False)
	axs[1].spines['right'].set_visible(False)

	cax = fig.add_axes([0.9, 0.5, 0.03, 0.38]) # [x, y, w, h]
	#plt.colorbar(im0,fraction=0.046, pad=0.04, cax=axs[2])
	plt.colorbar(im0,cax=cax)

	plt.show()

if __name__ == '__main__':
	#run()
	myPlot()
