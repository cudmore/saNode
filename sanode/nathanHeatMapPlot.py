
import os
import pandas as pd
import numpy as np
import scipy.stats # for sem
import tifffile
import matplotlib.pyplot as plt


def myPlot():
	# plot heat maps from tif

	titleStr = ''
	#dataPath = '/Users/cudmore/data/nathan'
	# created mar15
	dataPath = '/media/cudmore/data/heat-map/san4-raw'
	# created mar20 -- broken
	#dataPath = '/media/cudmore/data/heat-map/san4-raw'

	# vers==320 for mar15, ==296 for mar20
	#vers = 320
	#vers = 296
	# now trimming 15% of left/top/right/bottom
	vers = int(544/2)
	if 1:
		titleStr = 'san4 cd31 mask'
		san4Top = f'{dataPath}/san4-top/san4-top-cd31/san4-top-cd31_big_3d_cs{vers}_heatmap_norm.tif'
		san4Bottom = f'{dataPath}/san4-bottom/san4-bottom-cd31/san4-bottom-cd31_big_3d_cs{vers}_heatmap_norm.tif'
		doVolumeFraction = True
	if 0:
		titleStr = 'san4 hcn4 mask'
		san4Top = f'{dataPath}/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d_cs{vers}_heatmap_norm.tif'
		san4Bottom = f'{dataPath}/san4-bottom/san4-bottom-hcn4/san4-bottom-hcn4_big_3d_cs{vers}_heatmap_norm.tif'
		doVolumeFraction = True

	if 0:
		# hcn4 dist to vasc
		titleStr = 'san4 hcn4 dist to vasc'
		san4Top = f'{dataPath}/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d_edt_cs{vers}_heatmap.tif'
		san4Bottom = f'{dataPath}/san4-bottom/san4-bottom-hcn4/san4-bottom-hcn4_big_3d_edt_cs{vers}_heatmap.tif'
		doVolumeFraction = False

	print('loading san4Top:', san4Top)
	topTif = tifffile.imread(san4Top)
	print('loading san4Bottom:', san4Bottom)
	bottomTif = tifffile.imread(san4Bottom)

	# mask out 0 values so they are displayed as transparent (white)
	#topTif = np.ma.masked_where(topTif == 0, topTif)
	#bottomTif = np.ma.masked_where(bottomTif == 0, bottomTif)
	topTif = np.where(topTif==0, np.nan, topTif)
	bottomTif = np.where(bottomTif==0, np.nan, bottomTif)

	fig, axs = plt.subplots(1, 3, sharey=True)
	fig.suptitle(titleStr)

	cmap = 'inferno' #'Greens' # 'inferno'

	if doVolumeFraction:
		# for plotting masks
		vmin = 0.000
		vmax = 1
	else:
		# for plotting edt
		if 1 and 'san4-top-hcn4_big_3d_edt' in san4Top:
			topTif[2,4] = np.nan # bright spot appeared 20210322 after trimming 15% of l/t/r/b
			topTif[3,4] = np.nan # bright spot appeared 20210322 after trimming 15% of l/t/r/b
			topTif[5,5] = np.nan # bright spot appeared 20210322 after trimming 15% of l/t/r/b
			topTif[9,0] = np.nan
			topTif[14,1] = np.nan
			topTif[20,2] = np.nan
		#
		topTifMax = np.nanmax(topTif)
		bottomTifMax = np.nanmax(bottomTif)
		vmin = 0
		vmax = max(topTifMax, bottomTifMax)

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
	densityLineTop = np.zeros(m1) * np.nan
	densityLineTop_sem = np.zeros(m1) * np.nan
	topMean = np.nanmean(topTif)
	for i in range(m1):
		# top
		#print('row:', i, topTif[i,:])
		oneRowMax = np.nanmax(topTif[i,:])
		oneRowSum = np.nansum(topTif[i,:])
		oneRowMean = np.nanmean(topTif[i,:])
		oneRowSem = scipy.stats.sem(topTif[i,:], nan_policy='omit') # np does not have nansem
		oneRowMedian = np.nanmedian(topTif[i,:])
		oneRowDf = (oneRowMean-topMean) / topMean
		if doVolumeFraction:
			densityLineTop[i] = oneRowMean
			densityLineTop_sem[i] = oneRowSem
		else:
			# edt for hcn4 dist to vasc
			densityLineTop[i] = oneRowMean
			densityLineTop_sem[i] = oneRowSem
		print(f'\t{i}\t{oneRowMax}\t{oneRowMean}')
	#
	m2,n = bottomTif.shape
	print('bottom m2:', m2)
	yDensityLineBottom = range(m1+m2)
	densityLineBottom = np.zeros(m1+m2) * np.nan
	densityLineBottom_sem = np.zeros(m1+m2) * np.nan
	bottomMean = np.mean(bottomTif)
	for i in range(m2):
		# bottom
		oneRowMax = np.nanmax(bottomTif[i,:])
		oneRowSum = np.nansum(bottomTif[i,:])
		oneRowMean = np.nanmean(bottomTif[i,:])
		oneRowSem = scipy.stats.sem(bottomTif[i,:], nan_policy='omit') # np does not have nansem
		oneRowMedian = np.nanmedian(bottomTif[i,:])
		oneRowDf = (oneRowMean-topMean) / topMean #USING TOP MEAN
		if doVolumeFraction:
			#print('row:', m1+i, 'oneRowMax:', oneRowMax)
			densityLineBottom[m1+i] = oneRowMean
			densityLineBottom_sem[m1+i] = oneRowSem
		else:
			# edt for hcn4 dist to vasc
			#print('row:', m1+i, 'oneRowMax:', oneRowMean)
			densityLineBottom[m1+i] = oneRowMean
			densityLineBottom_sem[m1+i] = oneRowSem
		print(f'\t{m1+i}\t{oneRowMax}\t{oneRowMean}')

	#
	#top
	axs[1].scatter(densityLineTop, yDensityLineTop,
					vmin=vmin,
					vmax=vmax,
					c=densityLineTop, cmap=cmap)
	axs[1].errorbar(densityLineTop, yDensityLineTop, xerr=densityLineTop_sem, yerr=None,
					ecolor='k', fmt='none')
	#bottom
	axs[1].scatter(densityLineBottom, yDensityLineBottom,
					vmin=vmin,
					vmax=vmax,
					c=densityLineBottom, cmap=cmap)
	axs[1].errorbar(densityLineBottom, yDensityLineBottom, xerr=densityLineBottom_sem, yerr=None,
					ecolor='k', fmt='none')
	#axs[1].set_xscale('log')
	#axs[1].set_ylim(0, m1+m2+1)
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
	myPlot()
