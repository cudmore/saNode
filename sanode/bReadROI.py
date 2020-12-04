"""
After drawing line ROI on top of image in Fiji

Load both the .zip and .csv (measure)

we need both .zip and multimeasure

.zip gives us position in image (we can calculate length)
multimeasure .csv gives us group

install
	pip install read-roi
"""

import os, math, json
import numpy as np
import pandas as pd

import tifffile

#import matplotlib.pyplot as plt
#import matplotlib as mpl

#import seaborn as sns

import read_roi # using read_roi.read_roi_zip

import sanode

#import sanode
#import bimpy

'''
def readVoxelSize(path):
	x,y,z,shape = sanode.bTiffFile.readVoxelSize(path, getShape=True)
	return x,y,z,shape
'''
def defaultSeabornLayout(plotForTalk=False):
    if plotForTalk:
        plt.style.use('dark_background')
    else:
        plt.style.use('default')

    fontSize = 10
    if plotForTalk: fontSize = 14

    mpl.rcParams['figure.figsize'] = [4.0, 4.0]
    mpl.rcParams['lines.linewidth'] = 1.0
    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['axes.labelsize'] = fontSize # font size of x/y axes labels (not ticks)
    mpl.rcParams['xtick.labelsize']=fontSize
    mpl.rcParams['ytick.labelsize']=fontSize

def _euclideanDist(x1, y1, x2, y2):
	dx = abs(x2-x1)
	dy = abs(y2-y1)
	dist = math.sqrt(dx**2 + dy**2)
	return dist

def loadRoiFiles(path, sanStr='', origRegions=''):
    """
    path: full path to original .tif
    load MAX_
    load df from Fiji Roi Manager RoiSet.zip
    return df, maxImg
    """
    print('loadRoiFile() path:', path)

    # get voxel size
    x, y, z, shape = sanode.bTiffFile.readVoxelSize(path, getShape=True)
    print('  shape:', shape)
    print('  x/y/z voxel (um/pixel)', x,y,z)
    xyzVoxel = (x,y,z)

    origPath, origTiff = os.path.split(path)

    # load the max
    maxPath = os.path.join(origPath, 'MAX_' + origTiff)
    #maxImg = plt.imread(maxPath)
    maxImg = tifffile.imread(maxPath)

    # load roi .zip
    tmpPath, tmpFile = os.path.split(path)
    zipFilePath = os.path.join(tmpPath, 'RoiSet.zip')
    print('  loading zipFilePath:', zipFilePath)
    df = sanode.bReadROI.loadRoiZip2(zipFilePath, xyzVoxel, sanStr=sanStr, origRegions=origRegions)

    return df, maxImg

def loadRoiZip2(roiZipPath, xyzVoxel=(1,1,1), sanStr='', origRegions=''):
	"""
	Load a Fiji ROI manager .zip file

	roiZipPath: full path to .zip saved by Fiji ROI manager
	xyzVoxel: required to calculate length(diameter) of line ROI

	REMEMBER, I am using a modified version of read roi, modified to also load 'group'
	"""

	'''
	print('loadRoiZip2()')
	print('  roiZipPath:', roiZipPath)
	print('  xyzVoxel:', xyzVoxel)
	print('  sanStr:', sanStr)
	print('  origRegions:', origRegions)
	'''

	roiList = read_roi.read_roi_zip(roiZipPath) # return collections.OrderedDict
	nList = len(roiList)

	# these lists will be added as columns to df
	group_list = [np.nan] * nList
	zSlice_list = [np.nan] * nList
	x1_list = [np.nan] * nList
	x2_list = [np.nan] * nList
	y1_list = [np.nan] * nList
	y2_list = [np.nan] * nList
	xMid_list = [np.nan] * nList
	yMid_list = [np.nan] * nList
	color_list = ['k'] * nList
	size_list = [10] * nList
	area_list = [10] * nList # for scatterplot, makrer is area, size ** 2
	diam_list = [np.nan] * nList
	for idx, roi in enumerate(roiList):
		# roi is like: ('0056-1250-1420', {'type': 'line', 'x1': 18.16666603088379, 'x2': 84.5, 'y1': 19.16666603088379, 'y2': 0.5, 'draw_offset': False, 'width': 0, 'name': '0056-1250-1420', 'position': 56})
		thisRoi = roiList[roi]
		# this roi is like: {'type': 'line', 'x1': 18.16666603088379, 'x2': 84.5, 'y1': 19.16666603088379, 'y2': 0.5, 'draw_offset': False, 'width': 0, 'name': '0056-1250-1420', 'position': 56}

		# trying to modify source of _read_roi.py package to read 'group'
		# this works !!!
		# requires modified source in Sites/read-roi/read_roi/_read_roi.py
		group = thisRoi['group']
		group_list[idx] = group

		# z
		zSlice = thisRoi['position']
		zSlice_list[idx] = zSlice

		# x/y
		x1 = thisRoi['x1']
		x2 = thisRoi['x2']
		y1 = thisRoi['y1']
		y2 = thisRoi['y2']

		x1_list[idx] = x1
		x2_list[idx] = x2
		y1_list[idx] = y1
		y2_list[idx] = y2

		# x/y mid point
		xMid = min(x1,x2) + abs(x2-x1) / 2
		yMid = min(y1,y2) + abs(y2-y1) / 2

		xMid_list[idx] = xMid
		yMid_list[idx] = yMid

		# make new column with Length as diam
		#diam_list[idx] = df.iloc[idx]['Length']
		distPixels = _euclideanDist(x1, y1, x2, y2)
		distUm = distPixels * xyzVoxel[0]
		diam_list[idx] = distUm

		# color based on group
		'''
		group = df.iloc[idx]['Group'] # np.float64
		group = int(group)
		groupStr = str(group)
		color = colorDict[groupStr]
		color_list[idx] = color
		'''

		# todo calculate lenth(diam) using xVoxel and (x1,y1), (x2,y2)

		# size/area for scatterplot based on length/diam
		'''
		length = df.iloc[idx]['Length'] # np.float64
		size_list[idx] = length
		area_list[idx] = length * 2 #** 2
		'''

	df = pd.DataFrame()
	# I want these as first few columns but need to append actual values at end
	df['sanStr'] = '' # fill in with ('SAN1', 'SAN2', ...)
	df['origRegions'] = '' # fill this in with ('headMid', 'tail', 'headMidTail')
	df['finalRegion'] = '' # fill this in with ('head', 'mid', 'tail')

	df['group'] = group_list
	# group is int64, for plotly to interpret as disrete values (versus continuous) it has to be a string
	df["groupStr"] = df["group"].astype(str)

	df['diameter_um'] = diam_list
	df['length_um'] = diam_list
	df['z'] = zSlice_list
	df['x1'] = x1_list
	df['x2'] = x2_list
	df['y1'] = y1_list
	df['y2'] = y2_list
	df['xMid'] = xMid_list
	df['yMid'] = yMid_list
	#df['color'] = color_list
	#df['size'] = size_list
	#df['area'] = area_list
	df['xVoxel'] = xyzVoxel[0]
	df['yVoxel'] = xyzVoxel[1]
	df['zVoxel'] = xyzVoxel[2]

	df['xMidOffset'] = ''
	df['yMidOffset'] = ''

	# I want these as first few columns but need to append actual values at end
	df['sanStr'] = sanStr # fill in with ('SAN1', 'SAN2', ...)
	df['origRegions'] = origRegions # fill this in with ('headMid', 'tail', 'headMidTail')
	df['finalRegion'] = '' # fill this in with ('head', 'mid', 'tail')

	df = parseBranches(df) #seperate tracing into disjoint/discrete vessel segments

	#
	return df

def old_loadRoiZip(roiSetPath, resultsPath):
	"""
	read both .zip and .csv and merge into one dataframe
	appending columns from zip

	roi zip does not have group, it is in csv

	return pandas dataframe after adding columns to .csv
		df['diam'] = diam_list
		df['x1'] = x1_list
		df['x2'] = x2_list
		df['y1'] = y1_list
		df['y2'] = y2_list
		df['xMid'] = xMid_list
		df['yMid'] = yMid_list
		df['color'] = color_list
		df['size'] = size_list
		df['area'] = area_list
	"""
	roiList = read_roi.read_roi_zip(roiSetPath) # return collections.OrderedDict
	nList = len(roiList)

	df = pd.read_csv(resultsPath)
	ndf = len(df.index)

	if nList != ndf:
		print('error: roiSet and results.csv need to be the same length')
		print(f'  roiSet {nList}, csv {ndf}')
		return None

	colorDict = {
		'0': 'k',
		'1': 'r',
		'11': 'y',
		'2': 'g',
		'3': 'b',
		'4': 'm', #'y'
	}

	# these lists will be added as columns to df
	x1_list = [np.nan] * nList
	x2_list = [np.nan] * nList
	y1_list = [np.nan] * nList
	y2_list = [np.nan] * nList
	xMid_list = [np.nan] * nList
	yMid_list = [np.nan] * nList
	color_list = ['k'] * nList
	size_list = [10] * nList
	area_list = [10] * nList # for scatterplot, makrer is area, size ** 2
	diam_list = [np.nan] * nList
	for idx, roi in enumerate(roiList):
		# roi is like: ('0056-1250-1420', {'type': 'line', 'x1': 18.16666603088379, 'x2': 84.5, 'y1': 19.16666603088379, 'y2': 0.5, 'draw_offset': False, 'width': 0, 'name': '0056-1250-1420', 'position': 56})
		thisRoi = roiList[roi]
		# this roi is like: {'type': 'line', 'x1': 18.16666603088379, 'x2': 84.5, 'y1': 19.16666603088379, 'y2': 0.5, 'draw_offset': False, 'width': 0, 'name': '0056-1250-1420', 'position': 56}

		# trying to modify source of _read_roi.py package to read 'group'
		# this works !!!
		# requires modified source in Sites/read-roi/read_roi/_read_roi.py
		group = thisRoi['group']
		#print(idx, type(group), group)

		# x/y
		x1 = thisRoi['x1']
		x2 = thisRoi['x2']
		y1 = thisRoi['y1']
		y2 = thisRoi['y2']

		x1_list[idx] = x1
		x2_list[idx] = x2
		y1_list[idx] = y1
		x2_list[idx] = y2

		# x/y mid point
		xMid = min(x1,x2) + abs(x2-x1) / 2
		yMid = min(y1,y2) + abs(y2-y1) / 2

		xMid_list[idx] = xMid
		yMid_list[idx] = yMid

		# make new column with Length as diam
		diam_list[idx] = df.iloc[idx]['Length']

		# color based on group
		group = df.iloc[idx]['Group'] # np.float64
		group = int(group)
		groupStr = str(group)
		color = colorDict[groupStr]
		color_list[idx] = color

		# size/area for scatterplot based on length/diam
		length = df.iloc[idx]['Length'] # np.float64
		size_list[idx] = length
		area_list[idx] = length * 2 #** 2

	df['diam'] = diam_list
	df['x1'] = x1_list
	df['x2'] = x2_list
	df['y1'] = y1_list
	df['y2'] = y2_list
	df['xMid'] = xMid_list
	df['yMid'] = yMid_list
	df['color'] = color_list
	df['size'] = size_list
	df['area'] = area_list
	#
	return df

"""
def oldMain():
	maxPath = '/media/cudmore/data/san-density/SAN4/tracing/san4_max.tif'
	maxImg = plt.imread(maxPath)
	'''
	#plt.imshow(maxImg, cmap=plt.cm.reds)
	plt.imshow(maxImg)
	'''

	roiSetPath = '/media/cudmore/data/san-density/SAN4/tracing/RoiSet.zip'
	resultsPath = '/media/cudmore/data/san-density/SAN4/tracing/Results.csv'
	numRows = 7104 # original image size
	numCols = 3552
	df = loadRoiZip(roiSetPath, resultsPath)

	desc = df.groupby('Group')['Length'].describe()
	print(desc)

	defaultSeabornLayout(plotForTalk=False)

	if 1:
		# violin plot of Length for each group
		fig, ax = plt.subplots(1)
		#sns.pointplot(ax=ax, x='Group', y='Length', data=df) # this gives us mean
		palette=['r','g','b','m', 'y']
		sns.violinplot(ax=ax, x='Group', y='diam', palette=palette, data=df)
		# this should but does not work
		#sns.violinplot(ax=ax, y=df['Group'], x=df['diam'], palette=palette)
		ax.set_ylabel('Vessel Diameter ($\mu$m)')
		ax.set_xlabel('Branch Order')

	if 0:
		# histogram of Length for each group
		fig, ax = plt.subplots(1)
		binwidth = 1 # um

		#sns.histplot(ax=ax, x='diam', hue='Group', binwidth=binwidth, data=df)

		palette=['r','g','b','m', 'y'] # 'y' is for my strange 11 'in between' artery
		sns.histplot(ax=ax, x='diam', hue='Group', binwidth=binwidth, palette=palette, data=df)

		ax.set_xlabel('Vessel Diameter ($\mu$m)')
		ax.set_ylabel('Count')

	if 1:
		# scatter plot of spatial position, diameter (marker size), and group (color)
		fig, ax = plt.subplots(1)
		# s specifies, The marker size in points**2. Default is rcParams['lines.markersize'] ** 2.
		ax.imshow(maxImg, cmap='gray') # 'Reds'

		x = df['xMid'].tolist()
		y = df['yMid'].tolist()
		size = df['size'].tolist()
		#size = df['area'].tolist()
		color = df['color'].tolist()
		ax.scatter(x,y, s=size, c=color)
		ax.set_ylim(numRows, 0) #reversed
		ax.set_xlim(0, numCols)
		ax.axis('off')

	if 1:
		#
		# plot Group 1 length/diam as function of y
		fig, ax = plt.subplots(1)
		# s specifies, The marker size in points**2. Default is rcParams['lines.markersize'] ** 2.
		theseGroups = [1, 11]
		diamGroupOne = df[ df['Group'].isin(theseGroups) ]['diam'].tolist()
		yMidGroupOne = df[ df['Group'].isin(theseGroups) ]['yMid'].tolist()
		color = df[ df['Group'].isin(theseGroups) ]['color'].tolist()

		ax.scatter(diamGroupOne, yMidGroupOne, c=color) #, s=sizeList, c=colorList)
		ax.set_ylim(numRows, 0) #reversed
		ax.get_yaxis().set_visible(False)
		ax.set_xlabel('Arterial Diameter ($\mu$m)')

	#
	# todo: split group 2/3/4 based on y-position (superior/inferior)
	# for group 2 (first branch), plot hist of diameter in superior and inferior
	# plot diam hist for superior and inferior

	# seperate groups 1/2/3/4 green/blue/magenta in superior/inferior

	if 1:
		doViolin = False
		ySup = [1000, 3000]
		yInf = [5000, 8000]
		# plot diam of group 2 (first branches)
		theseGroups = [1, 2, 3, 4]
		palette=['r','g','b','m'] # 'y' is for my strange 11 'in between' artery
		binwidth = 1 # um
		xAxisRange = [2, 45] # share between sup/inf

		axs = [np.nan] * 2

		# superior
		sup_df = df [ (df['yMid']>ySup[0]) & (df['yMid']<ySup[1])]
		sup_df = sup_df[ sup_df['Group'].isin(theseGroups) ]

		desc = sup_df.groupby('Group')['Length'].describe()
		print('\nSuperior')
		print(desc)

		fig, ax = plt.subplots(1,1)
		axs[0] = ax

		if doViolin:
			sns.violinplot(ax=axs[0], x='Group', y='diam', palette=palette, data=sup_df)
			axs[0].set_ylim(xAxisRange) # share between sup/inf
		else:
			sns.histplot(ax=axs[0], x='diam', hue='Group', palette=palette, binwidth=binwidth, data=sup_df)
			axs[0].set_xlim(xAxisRange) # share between sup/inf
		axs[0].set_title('Superior')


		# inferior
		theseGroups = [1, 2, 3, 4, 11] # 11 is after primary branched into 2
		palette=['r','g','b', 'm', 'y'] # 'y' is for my strange 11 'in between' artery

		inf_df = df [ (df['yMid']>yInf[0]) & (df['yMid']<yInf[1])]
		inf_df = inf_df[ inf_df['Group'].isin(theseGroups) ]

		desc = inf_df.groupby('Group')['Length'].describe()
		print('Inferior')
		print(desc)

		fig, ax = plt.subplots(1,1)
		axs[1] = ax

		if doViolin:
			sns.violinplot(ax=axs[1], x='Group', y='diam', palette=palette, data=inf_df)
			axs[1].set_ylim(xAxisRange) # share between sup/inf
		else:
			sns.histplot(ax=axs[1], x='diam', hue='Group', palette=palette, binwidth=binwidth, data=inf_df)
			axs[1].set_xlim(xAxisRange) # share between sup/inf
		axs[1].set_title('Inferior')

	#
	plt.show()
"""

def _euclideanDist(x1, y1, x2, y2):
	dx = abs(x2-x1)
	dy = abs(y2-y1)
	dist = math.sqrt(dx**2 + dy**2)
	return dist

def parseBranches(roiDf):
	"""
	Extract individual vessel segments

	For example, for group 2 (1st order branch)
	step through each line ROI and see how far it is from previous xMid/yMid
	if it is FAR away then assume *this is the start of a new group 2 tracing
	"""

	roiDf['masterVesselIdx'] = ''

	masterVesselIdx = 0 # number each line ROI into a unique vessel segment

	groupList = roiDf['group'].unique()
	#print(groupList)
	for group in groupList:
		oneGroupDf = roiDf[ roiDf['group']==group ]
		numInGroup = len(oneGroupDf.index)
		#print('\ngroup:', group, 'numInGroup (number of line ROI):', numInGroup)
		'''
		with pd.option_context('display.max_rows', None):
			print(oneGroupDf)
		'''
		dfStartIdx = None # idx into master df to keep track of start/stop of individual vessels
		dfStopIdx = None  # these are asssigned when we encounter big gaps between line ROI xMid/yMid
		myIdx = 0 # count line roi within each group
		for dfIdx, oneRow in oneGroupDf.iterrows():
			#print(dfIdx)
			group = oneRow['group']
			xVoxel = oneRow['xVoxel'] # um/pixel
			yVoxel = oneRow['yVoxel'] # um/pixel
			xMid = oneRow['xMid'] # pixel
			yMid = oneRow['yMid']
			xMid_um = xMid * xVoxel
			yMid_um = yMid * yVoxel

			if dfStartIdx is None:
				# start a new vessel segment, the first index in a group is always the start
				dfStartIdx = dfIdx
			if myIdx == 0:
				pass
			elif dfIdx-dfIdx_prev > 1:
				# disjoint master df index within a group
				# start new segment
				dfStopIdx = dfIdx_prev
				'''
				print('  * disjoint master df index within group ... finish current segment')
				print('    dfStartIdx:', dfStartIdx)
				print('    dfStopIdx:', dfStopIdx)
				'''
			else:
				dist_um = _euclideanDist(xMid_um, yMid_um, xMid_um_prev, yMid_um_prev)
				if dist_um > 50:
					'''
					print('  * found big gap ... finish current segment')
					print('    dfStartIdx:', dfStartIdx)
					print('    dfStopIdx:', dfStopIdx)
					'''
					dfStopIdx = dfIdx_prev

			if dfStartIdx is not None and dfStopIdx is not None:
				# we just finished a single vessel segment
				'''
				print('      *** Finished vesssel ')
				print('           at dfIdx', dfIdx)
				print('           group', group)
				print('           masterVesselIdx', masterVesselIdx)
				print('           from dfStartIdx', dfStartIdx)
				print('           to dfStopIdx', dfStopIdx)
				'''

				# assign rows in df to masterVesselIDx
				# SUPER IMPORTANT, NEED TO have df['colName'] FIRST
				#roiDf['masterVesselIdx'].iloc[dfStartIdx:dfStopIdx+1] = masterVesselIdx
				roiDf.loc[dfStartIdx:dfStopIdx, ('masterVesselIdx')] = masterVesselIdx

				#print(roiDf.loc[dfStartIdx:dfStopIdx])

				dfStartIdx = dfIdx # on reset, start a new segment
				dfStopIdx = None
				#print('           starting new vessel dfStartIdx:', dfStartIdx)
				masterVesselIdx += 1

			#
			dfIdx_prev = dfIdx
			xMid_um_prev = xMid_um
			yMid_um_prev = yMid_um
			myIdx += 1

		#
		# after we are done iterating through the group, if we started a vessel with dfStartIdx
		# but did not finish with dfStopIdx, then finish it here
		if dfStartIdx is not None and dfStopIdx is None:
			# we started a vessel segment but did not finish it, finish it here
			# using dfIdx_prev is error prone !!!
			dfStopIdx = oneGroupDf.index[-1] # last row
			'''
			print('    === AFTER loop, cleaning up vessel segment')
			#print('           group', group)
			print('      masterVesselIdx:', masterVesselIdx)
			print('      dfStartIdx:', dfStartIdx)
			print('      dfStopIdx:', dfStopIdx)
			'''
			
			# assign rows in df to masterVesselIdx
			# SUPER IMPORTANT, NEED TO have df['colName'] FIRST
			#roiDf['masterVesselIdx'].iloc[dfStartIdx:dfStopIdx+1] = masterVesselIdx
			roiDf.loc[dfStartIdx:dfStopIdx, ('masterVesselIdx')] = masterVesselIdx

			dfStartIdx = None
			dfStopIdx = None
			masterVesselIdx += 1


	#
	return roiDf

if __name__ == '__main__':
	if 0:
		path = '/media/cudmore/data/san-density/SAN4/tracing/head/SAN4_head_BIG__ch2.zip'
		roi_df = loadRoiZip2(path, xyzVoxel=(1,1,1), sanStr='xSanStr', origRegions='xOrigRegion')
		print(roi_df.head())

	path = '/media/cudmore/data/san-density/SAN4/tracing/head/SAN4_head_BIG__ch2.tif'
	roi_df, maxImg = loadRoiFiles(path, sanStr='xSanStr', origRegions='xOrigRegion')
	roi_df = parseBranches(roi_df)

	'''
	with pd.option_context('display.max_rows', None):
		print(roi_df[ ['group', 'masterVesselIdx'] ])
	'''

	desc = roi_df.groupby('group')['masterVesselIdx'].describe()
	print(desc)

	groupList = roi_df['group'].unique()
	print(groupList)
	for group in groupList:
		oneGroupDf = roi_df[ roi_df['group']==group ]
		numInGroup = len(oneGroupDf.index)
		print('\ngroup:', group, 'numInGroup (number of line ROI):', numInGroup)

		print('summary of diameter_um for each masterVesselIdx')
		desc = oneGroupDf.groupby('masterVesselIdx')['diameter_um'].describe()
		print(desc)
		meanList = oneGroupDf.groupby('masterVesselIdx')['diameter_um'].mean().tolist()
		print(meanList)
