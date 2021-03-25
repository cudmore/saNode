"""
Given a path to a .tif file, usually a heat map,
save a csv with per row statistics for intensity values

Use plotResults() to plot the results
"""

import os
import numpy as np
import pandas as pd
import scipy.stats # needed for sem, numpy does not have it, use nan_policy='omit'
import tifffile

import matplotlib.pyplot as plt

def runRowStats(path, ignore0=True):
	"""
	Given a path to a 2D tif file (usually a heat map)
	Generate statistics on the intensity values in each row

	Parameters:
		path: full path to .tif file with a heat map (or any tif file for that matter)
				Assuming this tif is a 2d image, 3d stacks will not work
		ignore0: if True then convert 0 values to np.nan and ignore them
			this is important for missing values often encoded as 0

	Saves:
		The row statistics as a .csv file in the same folder as 'path'.
		Open this csv with pandas or drag/drop into Excel

	Returns:
		the Pandas DataFrame
		make some plots with plotResults()

	"""
	# load the tif
	if not os.path.isfile(path):
		print('ERROR: runRowStats() did not find the file:', path)
		return
	tifData = tifffile.imread(path)
	m,n = tifData.shape # m is rows, n is columns

	# get the name of the tif
	tifPath, tifFile = os.path.split(path)

	# decide if we want to ignore 0
	if ignore0:
		# set 0 values to np.nan so they will be ignored
		tifData = np.where(tifData==0, np.nan, tifData)

	# print out the heatmap
	if 0:
		print('heat map values are:')
		for i in range(m):
			printOneRow = ''
			for j in range(n):
				printOneRow += str(tifData[i,j]) + '\t'
			print(printOneRow + '\n')

	# make an empty dataframe, this is what we will save as a .csv
	df = pd.DataFrame()

	grandMean = np.nanmean(tifData) # used for oneRow_deltaF_over_f0

	# step through rows in tif and collect stats into Pandas df
	for i in range(m):
		# here we are using np functions like nanmin/npnanmax etc to ignore nan values
		oneRowMin = np.nanmin(tifData[i,:])
		oneRowMax = np.nanmax(tifData[i,:])
		oneRowSum = np.nansum(tifData[i,:])
		oneRowMean = np.nanmean(tifData[i,:])
		oneRowMedian = np.nanmedian(tifData[i,:])
		oneRowStd = np.nanstd(tifData[i,:])
		oneRowSem = scipy.stats.sem(tifData[i,:], nan_policy='omit') # np does not have nansem
		oneRow_deltaF_over_f0 = (oneRowMean-grandMean) / grandMean

		# append values to row i in our output pandas df
		df.loc[i, 'row'] = i
		df.loc[i, 'colCount'] = n # the number of pixels in the row, will be the same for all rows
		df.loc[i, 'min'] = oneRowMin
		df.loc[i, 'max'] = oneRowMax
		df.loc[i, 'sum'] = oneRowSum
		df.loc[i, 'mean'] = oneRowMean
		df.loc[i, 'median'] = oneRowMedian
		df.loc[i, 'std'] = oneRowStd
		df.loc[i, 'sem'] = oneRowSem
		df.loc[i, 'deltaF_over_f0'] = oneRow_deltaF_over_f0
		df.loc[i, 'tifFile'] = tifFile # always useful to keep track of what we were doing analysis from
		df.loc[i, 'tifPath'] = tifPath # always useful to keep track of what we were doing analysis from

	# print the results
	print('results per row ... can copy/paste this into Excel???')
	print(df)

	# save to csv
	savePath = os.path.splitext(path)[0]
	savePath += '_rowStats.csv'
	print('saving csv:', savePath)
	df.to_csv(savePath)

	return df

def plotResults(df, colName='mean', errorBars=None):
	"""
	Plot the results from df created by runRowStats()

	Parameters:
		df: Pandas dataframe returned from runRowStats()
		colName: the name of the column to plot from pandas df
		errorBars: the column name to use for error bars (usually sem)

	Return:
		matplotlib figure that can be saved as pdf or svg
	"""

	# make a figure
	fig, axs = plt.subplots(1, 1)

	# grab x/y data for plot from pandas dataframe
	xData = df['mean']
	yData = df['row']

	axs.plot(xData, yData)

	if errorBars is not None:
		xerr = df[errorBars]
		axs.errorbar(xData, yData, xerr=xerr)

	axs.set_xlabel(colName)

	axs.invert_yaxis()
	#axs.get_yaxis().set_visible(False)
	#axs.get_xaxis().set_visible(False)
	axs.spines['top'].set_visible(False)
	axs.spines['right'].set_visible(False)

	plt.show()

	return fig

if __name__ == '__main__':

	#
	# full path to a heat map .tif file
	#myPath = '/media/cudmore/data/heat-map/san4-raw/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d_cs320_heatmap.tif'

	dataPath = '/media/cudmore/data/heat-map/san4-raw'
	pathList = [
			# top
			f'{dataPath}/san4-top/san4-top-cd31/san4-top-cd31_big_3d_cs272_heatmap_norm.tif',
			f'{dataPath}/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d_cs272_heatmap_norm.tif',
			# bottom
			f'{dataPath}/san4-bottom/san4-bottom-cd31/san4-bottom-cd31_big_3d_cs272_heatmap_norm.tif',
			f'{dataPath}/san4-bottom/san4-bottom-hcn4/san4-bottom-hcn4_big_3d_cs272_heatmap_norm.tif'
			]
	#
	# calculate row stats and save in a .csv file
	for path in pathList:
		df = runRowStats(path)
		print('path:', path)
		fig = plotResults(df, colName='mean', errorBars='sem')
	#
	# optional
	#

	#
	# plot the results
	if 0:
		fig = plotResults(df, colName='mean', errorBars='sem')

	#
	# save the results as (pdf, svg, png)
	if 0:
		saveFileExtension = 'pdf'
		savePath = os.path.splitext(myPath)[0] + '_rowstats.' + saveFileExtension
		print('saving', saveFileExtension, 'figure as:', savePath)
		fig.savefig(savePath, dpi=600)
