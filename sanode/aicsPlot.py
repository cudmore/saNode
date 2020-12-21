"""
20201102

plot

	- mean dist from hcn4 to vasc
	- histograms of dist from hcn4 to vasc

	- density of vasc mask (no histograms)

	- mean diameter of slabs
	- histograms of slab diameter
"""

import os, math, random

import numpy as np
import pandas as pd

import scipy.stats

import matplotlib as mpl
import matplotlib.pyplot as plt
#import seaborn as sns
#sns.set_context("paper") # ('notebook', paper', 'talk', 'poster')

import bimpy

import aicsMyocyteDistToVasc

def defaultPlotLayout(plotForTalk=True):

	if plotForTalk:
		plt.style.use('dark_background')
	else:
		plt.style.use('default')

	fontSize = 12
	if plotForTalk:
		fontSize = 22

	mpl.rcParams['figure.figsize'] = [2.5, 3.0]
	mpl.rcParams['figure.constrained_layout.use'] = True # also applies to plt.subplots(1)
	mpl.rcParams['lines.linewidth'] = 3.0
	mpl.rcParams["lines.markersize"] = 7 # default: 6.0
	mpl.rcParams["lines.marker"] = 'o'
	mpl.rcParams['axes.spines.top'] = False
	mpl.rcParams['axes.spines.right'] = False
	mpl.rcParams['axes.xmargin'] = 0.3 # default: 0.05
	mpl.rcParams['axes.ymargin'] = 0.1 # default: 0.05
	mpl.rcParams['axes.labelsize'] = fontSize # font size of x/y axes labels (not ticks)
	mpl.rcParams['xtick.labelsize']=fontSize
	mpl.rcParams['ytick.labelsize']=fontSize

def printStats(dataList, verbose=True):
	if dataList:
		theMin = round(np.nanmin(dataList),2)
		theMax = round(np.nanmax(dataList),2)
		theMean = round(np.nanmean(dataList),2)
		theSD = round(np.nanstd(dataList),2)
		theNum = np.count_nonzero(~np.isnan(dataList))
		theSEM = round(theSD / math.sqrt(theNum),2)
		theMedian = round(np.nanmedian(dataList),2)
	else:
		theMin = np.nan
		theMax = np.nan
		theMean = np.nan
		theSD = np.nan
		theNum = np.nan
		theSEM = np.nan
		theMedian = np.nan
	if verbose:
		print(f'mean:{theMean:0.2f} sd:{theSD:0.2f} n:{theNum} min:{theMin:0.2f} max:{theMax:0.2f} median:{theMedian:0.2f}')

	return theMean, theSD, theSEM, theMedian, theNum

def plotEdgeDiamHist(pathList, doPlot=True, minNumberOfSlabs=5):
	"""
	each edge contributes to the hist (not each slab)
	"""

	print('plotEdgeDiamHist():')

	numPath = len(pathList)

	meanEdgeDiamList = [] # mean diameter of each edge
	numSlabList = [] # number of slabs in each edge
	voxelSizeList = []

	xAxisMin = 1e6
	xAxisMax = -1e6

	# build up data to plot
	for idx, path in enumerate(pathList):
		# load the stack
		myStack = bimpy.bStack(path=path, loadImages=False, loadTracing=True)

		# diameter is in pixels, use xVoxel/yVoxel to convert
		xVoxel = myStack.xVoxel # um/pixel
		yVoxel = myStack.yVoxel
		zVoxel = myStack.zVoxel
		voxelSizeList.append([xVoxel, yVoxel, zVoxel])

		slabList = myStack.slabList # bimpy.bVascularTracing

		xData = [x['Diam2']*xVoxel for x in slabList.edgeDictList]
		numSlabs = [x['nSlab'] for x in slabList.edgeDictList]

		# check if all nan and bail
		isAllNaN = np.isnan(xData).all()
		if isAllNaN:
			print(f'!!! !!! !!! bPyQtPlot.plotEdgeDiamHist() is not plotting Diam2, it is all np.nan, path:', path)
			# append
			numSlabList.append([])
			meanEdgeDiamList.append([])
			continue

		# remove nan, order matters
		numSlabs = [numSlabs[tmpIdx] for tmpIdx,x in enumerate(xData) if str(x) != 'nan']
		xData = [x for x in xData if str(x) != 'nan']

		# remove edges with small number of slabs
		if minNumberOfSlabs is not None:
			# remove diameters when the edge has < minNumberOfSlabs
			# order matters
			xData = [xData[tmpIdx] for tmpIdx,x in enumerate(numSlabs) if x > minNumberOfSlabs]
			numSlabs = [x for x in numSlabs if x > minNumberOfSlabs]

		# random sample to make histograms the same n
		if idx==0:
			# random sample a subset of head (to match tail)
			numInHead = len(xData)
			numInTail = 217
			tmpRange = range(numInHead)
			rndIdx = random.sample(tmpRange, numInTail)
			print('taking random sample for idx 0, n=', numInTail)
			xData = [xData[tmpIdx] for tmpIdx in rndIdx]
			numSlabs = [numSlabs[tmpIdx] for tmpIdx in rndIdx]

		# keep track of x-axis
		xMin = np.nanmin(xData)
		xMax = np.nanmax(xData)
		if xMin<xAxisMin: xAxisMin = xMin
		if xMax>xAxisMax: xAxisMax = xMax

		# append
		numSlabList.append(numSlabs)
		meanEdgeDiamList.append(xData)

	#
	# print stats
	print('  minNumberOfSlabs:', minNumberOfSlabs)
	meanList = []
	sdList = []
	nList = []
	medianList = []
	for idx, path in enumerate(pathList):
		print(f'{idx+1} path:{path}')
		print(f'  x/y/z voxel size:{voxelSizeList[idx]}')
		theDiameters = meanEdgeDiamList[idx] # pixels
		theMean, theSD, theSEM, theMedian, theN = printStats(theDiameters)
		meanList.append(theMean)
		sdList.append(theSD)
		medianList.append(theMedian)
		nList.append(theN)

	if doPlot:
		# set up plot
		defaultPlotLayout()
		fig,axs = plt.subplots(numPath, 1, figsize=(4,4)) # need constrained_layout=True to see axes titles
		cumFig, cumAxis = plt.subplots(1,1)
		nSlabsFig, nSlabsAxis = plt.subplots(numPath, 1, figsize=(4,4))

		# plot a number of hist
		bins = [(x+1)*(xVoxel) for x in range(50)]
		#bins = 'auto'

		#colorList = ['r', 'g', 'b', 'm', 'y', 'r', 'g', 'b', 'm', 'y']
		colorList = ['tab:blue', 'tab:orange', '0.5', '0.5', 'r', 'g', 'b']
		# plot
		for idx, path in enumerate(pathList):
			tmpPath, tmpFile = os.path.split(path) # for title/legend
			tmpFile = tmpFile.replace('_ch2.tif', '')
			tmpFile = tmpFile.replace('_', ' ')
			color = colorList[idx]

			theDiameters = meanEdgeDiamList[idx] # pixels
			theNumberOfSlabs = numSlabList[idx] # pixels

			# plot hist
			theMean = round(np.nanmean(theDiameters),2)
			theSD = round(np.nanstd(theDiameters),2)
			theNum = np.count_nonzero(~np.isnan(theDiameters))
			label = f'{tmpFile}\n$\mu$={theMean} $\sigma$={theSD} n={theNum}'
			label = None

			edgeColor = 'k'
			if color == 'k':
				edgeColor = '0.5'
			axs[idx].hist(theDiameters, bins=bins, color=color,
							histtype='bar', edgecolor=edgeColor, label=label,
							density=True)

			# add a legend
			axs[idx].legend(frameon=False, handlelength=0, handletextpad=-20)
			lastIdx = 1 #2 # allows us to plot head/mid/tail or just head/mid
			if idx==lastIdx:
				pass
			else:
				axs[idx].set_xticklabels([])
			if idx == lastIdx:
				axs[idx].set_xlabel('Vessel Segment Diameter ($\mu$m)')
			if idx == 1:
				axs[idx].set_ylabel('Probability')
			axs[idx].set_xlim(xAxisMin, xAxisMax) # um

			print('setting hist y-axis to [0,0.42] for san3')
			axs[idx].set_ylim(0, 0.5) # um

			# plot cumulative
			n, bins, patches = cumAxis.hist(theDiameters, histtype='step',
								bins=bins, color=color, cumulative=True, density=True, linewidth=2)
			cumAxis.set_xlim(xAxisMin, xAxisMax) # um
			cumAxis.set_xlabel('Vessel Segment Diameter ($\mu$m)')
			cumAxis.set_ylabel('Probability')

			# plot nSlabs versus diam
			print(len(nSlabsAxis), idx, len(theDiameters), len(theNumberOfSlabs), color)
			nSlabsAxis[idx].scatter(theDiameters, theNumberOfSlabs, marker='o', color=color)
			if idx==2:
				pass
			else:
				nSlabsAxis[idx].set_xticklabels([])
			if idx == 2:
				nSlabsAxis[idx].set_xlabel('Vessel Segment Diameter ($\mu$m)')
			if idx == 1:
				nSlabsAxis[idx].set_ylabel('Number of Slabs')
			nSlabsAxis[idx].set_xlim(xAxisMin, xAxisMax) # um

		plt.show()
	#
	# end
	return meanList, sdList, medianList, nList, axs, cumAxis

def plotSlabDiamHist(pathList):
	"""
	plot histogram of all slab diameter
	each slab contrinutes to the hist

	todo: add heuristic to reject slabs that have different intensities on either end
	todo: slab diameter is in pixels -->> need to convert to um !!!!
	"""

	# calculate
	#numSlabList = [] # keep track of number of slabs in each file
	diameterList = [] # each index i is list of all diameters in one file/path
	voxelSizeList = []

	for idx, path in enumerate(pathList):
		# load the stack
		myStack = bimpy.bStack(path=path, loadImages=False, loadTracing=True)

		# diameter is in pixels, use xVoxel/yVoxel to convert
		xVoxel = myStack.xVoxel # um/pixel
		yVoxel = myStack.yVoxel
		zVoxel = myStack.zVoxel
		voxelSizeList.append([xVoxel, yVoxel, zVoxel])

		#xVoxelSizeList.append(xVoxel) # assuming x/y are same

		# grab the slab list (this is a bimpy.bVascularTracing object)
		slabList = myStack.slabList # bimpy.bVascularTracing
		# get a list of all slab diameter
		# todo: check this is what I set when I analyze all diameter
		# units here are pixels
		oneDiameterList = slabList.d2 # check if this is what I fill in when using mp analyze all slabs
		# remove nan
		oneDiameterList = oneDiameterList[~np.isnan(oneDiameterList)]
		# convert pixels to um
		oneDiameterList = oneDiameterList * xVoxel # um
		# append
		diameterList.append(oneDiameterList)

		# number of slabs in each file
		numSlabs = oneDiameterList.size
		#numSlabList.append(numSlabs)

	#
	# print stats
	for idx, path in enumerate(pathList):
		theDiameters = diameterList[idx] # pixels
		print(f'{idx+1} path:{path}')
		print(f'  x/y/z voxel size:{voxelSizeList[idx]}')
		printStats(theDiameters)

	#
	# plot

	# set up plot
	defaultPlotLayout()
	fig,axs = plt.subplots(3, 1, figsize=(6,5)) # need constrained_layout=True to see axes titles
	#cumAxes = 3
	cumFig, cumAxis = plt.subplots(1,1)

	# plot a number of hist
	bins = [(x+1)*(xVoxel) for x in range(30)]
	#bins = 'auto'

	colorList = ['r', 'g', 'b']

	for idx, path in enumerate(pathList):
		tmpPath, tmpFile = os.path.split(path) # for title/legend
		tmpFile = tmpFile.replace('_ch2.tif', '')
		tmpFile = tmpFile.replace('_', ' ')
		color = colorList[idx]

		theDiameters = diameterList[idx] # pixels

		# plot hist
		theMean = round(np.nanmean(theDiameters),2)
		theSD = round(np.nanstd(theDiameters),2)
		theNum = np.count_nonzero(~np.isnan(theDiameters))
		label = f'{tmpFile}\n$\mu$={theMean} $\sigma$={theSD} n={theNum}'

		axs[idx].hist(theDiameters, bins=bins, color=color,
						histtype='bar', edgecolor='k', label=label,
						density=True)

		# add a legend
		#axs[idx].legend(frameon=False, prop={'size': 12})
		axs[idx].legend(frameon=False, handlelength=0, handletextpad=-20)
		# title
		#axs[idx].title.set_text(tmpFile)

		#axs[idx].set_xlabel('Slab Diameter ($\mu$m)')
		if idx==2:
			pass
		else:
			axs[idx].set_xticklabels([])
		if idx == 2:
			axs[idx].set_xlabel('Vessel Diameter ($\mu$m)')
		if idx == 1:
			axs[idx].set_ylabel('Probability')
		axs[idx].set_xlim(1, 14) # um

		# plot cumulative
		n, bins, patches = cumAxis.hist(theDiameters, histtype='step',
							bins=bins, color=color, cumulative=True, density=True, linewidth=2)
		cumAxis.set_xlim(1, 14) # um
		cumAxis.set_xlabel('Vessel Diameter ($\mu$m)')
		cumAxis.set_ylabel('Probability')

	#
	#plt.xlabel('Slab Diameter ($\mu$m)')
	#plt.ylabel('Probability')
	#fig.ylabel('Probability')
	#
	plt.show()

def plot_hcn4_dist_hist(pathList, doPlot=True, verbose=True, keepAboveDist=0.2):
	"""
	Plot distribution of distance from each hcn4 mask pixel to nearest vasculature

	params:
		path: full path to _ch2.tif
		keepAboveDist: um distances to keep are > keepAboveDist
	plot head/mid/tail
	"""

	xAxisMin = 1e6
	#xAxisMax = -1e6
	xAxisMax = 1e6 # confusing

	goodDistancesList = []

	# make a df and save as .csv
	df = pd.DataFrame(columns=['SAN', 'headMidTail', 'hcn4DistToVasc'])

	# calculate
	for idx, path in enumerate(pathList):
		# figure out SAN and headMidTail
		tmpPath, tmpFile = os.path.split(path)
		# SAN2_head_ch2.tif
		tmpFile, tmpExt = os.path.splitext(tmpFile)
		# SAN2_head_ch2
		sanName, headMidTail, channel = tmpFile.split('_')

		# calculate the distance of each hcn4 pixel to nearest vasculature
		thresholdDict, thresholdDistances = aicsMyocyteDistToVasc.aicsMyocyteDistToVasc(path)

		# make a histogram of thresholdDistances (includes nan)

		#print('  before removing nan:', thresholdDistances.shape)

		numberOfNonNan = np.count_nonzero(~np.isnan(thresholdDistances))
		#print('  numberOfNonNan:', numberOfNonNan)

		# remove nan
		goodDistances = thresholdDistances[~np.isnan(thresholdDistances)]
		#print('  after removing nan:', goodDistances.shape)

		if keepAboveDist is not None:
			goodDistances = goodDistances[goodDistances>keepAboveDist]

		# 20201106, this is wierd but will allow me to take
		# avg cum hist across 1/2/3/4 in superioer/mid/inferior
		keepBelowDistances = 24
		if keepBelowDistances is not None:
			goodDistances = goodDistances[goodDistances<keepBelowDistances]

		# keep track of x-axis
		xMin = np.nanmin(goodDistances)
		xMax = np.nanmax(goodDistances)
		if xMin<xAxisMin: xAxisMin = xMin
		#if xMax>xAxisMax: xAxisMax = xMax # max should be smalled xMax???
		if xMax<xAxisMax: xAxisMax = xMax # max should be smalled xMax???

		# append
		goodDistancesList.append(goodDistances)

		#
		# make a dataframe
		nOrig = goodDistances.size
		# random select a subset
		nSample = 1000000
		goodDistances2 = np.random.choice(goodDistances, nSample, replace=False)
		n = goodDistances2.size
		print(f'  making df with {n} rows from original {nOrig}')

		tmp_df = pd.DataFrame()
		tmp_df['SAN'] = [sanName] * n
		tmp_df['headMidTail'] = [headMidTail] * n
		tmp_df['hcn4DistToVasc'] = goodDistances2

		df = df.append(tmp_df, ignore_index = True)

	#
	# save dataframe df
	dfFilePath = 'hcn4Dist.csv'
	print('  saving dfFilePath:', dfFilePath, '... please wait')
	df.to_csv(dfFilePath)

	# stats
	if 1:
		for tmpList in goodDistancesList:
			printStats(tmpList, verbose=verbose)

		# Tests whether the distributions of two independent samples are equal or not.
		# Observations in each sample are independent and identically distributed (iid).
		# Observations in each sample can be ranked.
		#
		# 0 - 1
		'''
		stat, p01 = scipy.stats.mannwhitneyu(stat0, stat1)
		# 1 - 2
		stat, p12 = scipy.stats.mannwhitneyu(stat1, stat2)
		# 0 - 2
		'''
		# this works
		if 0:
			stat, p02 = scipy.stats.mannwhitneyu(stat0, stat2)
			print('mannwhitneyu p02:', p02)
		#print(f'  p01:{p01}, p12:{p12}, p02:{p02}')
		#
		'''
		# The Wilcoxon signed-rank test tests the null hypothesis that two related paired samples come from the same distribution.
		# 0 - 1
		stat, p01 = scipy.stats.wilcoxon(stat0, stat1)
		# 1 - 2
		stat, p12 = scipy.stats.wilcoxon(stat1, stat2)
		# 0 - 2
		print('wilcoxon')
		stat, p02 = scipy.stats.wilcoxon(stat0, stat2)
		print(f'  p01:{p01}, p12:{p12}, p02:{p02}')
		'''

	#
	# plot
	if doPlot:
		# set up plot
		defaultPlotLayout()
		fig,axs = plt.subplots(3, 1, figsize=(7,5)) # need constrained_layout=True to see axes titles
		cumFig, cumAxis = plt.subplots(1,1, figsize=(4,4))

		colorList = ['r', 'g', 'b']

		# plot
		for idx, path in enumerate(pathList):
			tmpPath, tmpFile = os.path.split(path) # for title/legend
			tmpFile = tmpFile.replace('_ch2.tif', '')
			tmpFile = tmpFile.replace('_', ' ')
			color = colorList[idx]

			goodDistances = goodDistancesList[idx]

			# plot hist
			theMin = np.nanmin(goodDistances)
			theMax = np.nanmax(goodDistances)
			theMean = round(np.nanmean(goodDistances),2)
			theSD = round(np.nanstd(goodDistances),2)
			theNum = np.count_nonzero(~np.isnan(goodDistances))
			label = f'{tmpFile}\n$\mu$={theMean:.2f} $\sigma$={theSD:.2f} n={theNum}'

			# had to turn off edgecolor='k' because some were showing up as black (e.g. 'k')
			bins = 200 #'auto'
			axs[idx].hist(goodDistances, bins=bins, color=color,
							#histtype='bar', edgecolor='k', label=label,
							histtype='bar', label=label,
							density=True,
							log=True)

			#axs[idx].set_xlim(xAxisMin, xAxisMax) # um
			axs[idx].set_xlim(0, xAxisMax) # um

			axs[idx].legend(frameon=False, handlelength=0, handletextpad=-20)
			if idx==2:
				pass
			else:
				pass
				#axs[idx].set_xticklabels([])
			if idx == 2:
				axs[idx].set_xlabel('HCN4 distance to vasculature ($\mu$m)')
			if idx == 1:
				axs[idx].set_ylabel('Probability')

			# plot cumulative
			#hist,bins = np.histogram(goodDistances,bins=bins)
			if idx==0:
				color = 'k'
			elif idx==1:
				color = '0.5' # gray
			n, bins, patches = cumAxis.hist(goodDistances, bins=bins,
						histtype='step', color=color, linewidth=2,
						cumulative=True, density=True,
						range=[theMin,theMax])
			#cumAxis.set_xlim(xAxisMin, xAxisMax) # um
			cumAxis.set_xlim(0, xAxisMax) # um
			cumAxis.set_xlabel('HCN4 distance to vasculature ($\mu$m)')
			cumAxis.set_ylabel('Probability')

	#
	plt.show()

	return goodDistancesList

def plotMaskDensity(channel=2, csvFile=None, plotMean=True):
	"""
	plot the percent of a mask occupying a valume

	use to plot both hcn4 (ch1) and vasc (chan2)
	there is no mean here, this is an absolute count per stack
	"""

	defaultPlotLayout()
	#sns.set_context("paper") # ('notebook', paper', 'talk', 'poster')

	# load csv into pd dataframe
	if csvFile is None:
		csvFile = f'../Density-Result-ch{channel}.csv'
	df = pd.read_csv(csvFile)
	#print(df)

	sanList = ['SAN1', 'SAN2', 'SAN3', 'SAN4']
	sanMarkers = ['o', '^', 's', 'd']
	regionList = ['head', 'mid', 'tail']
	regionList = ['head', 'tail']
	hmtListLabel = ['Superior', 'Inferior']

	# column to pull plot values form
	statCol = 'vMaskPercent'

	#regionListData = [] # not working
	#regionListData = [[]] * len(regionList) # too complicated
	superiorList = []
	inferiorList = []
	dataList = []
	for sanIdx, sanStr in enumerate(sanList):
		# & has higher precident than ==
		#oneList = df[ (df['SAN']==sanStr) ]['mean'].tolist()
		oneSeries = df[ (df['SAN']==sanStr) & df['headMidTail'].isin(regionList) ][statCol]
		oneList = oneSeries.tolist()
		dataList.append(oneList)
		superiorList.append(oneList[0])
		inferiorList.append(oneList[1])
		# this is getting complicated, loosing track
		# THIS IS NOT WORKING !!!!!!!!!!!!!!
		'''
		for regionIdx, region in enumerate(regionList):
			# todo: this needs to be 2d list
			regionListData[regionIdx].append(oneList[regionIdx])
		'''
		print('  ', sanStr, oneList)

	print('  superiorList:', superiorList)
	print('  inferiorList:', inferiorList)
	#print(regionListData)

	#colorChars = ['r', 'g', 'b', 'y'] # one color for each of SAN1, SAN2, ...
	colorChars = ["0.8", "0.8", "0.8", "0.8"] # one color for each of SAN1, SAN2, ...

	fig,ax = plt.subplots(1, figsize=(6,6)) # need constrained_layout=True to see axes titles
	for idx, data in enumerate(dataList):
		colorChar = colorChars[idx]
		marker = sanMarkers[idx]
		#ax.plot(regionList, data, colorChar)
		ax.plot(data, color=colorChar,
				linewidth=3, markersize=6, marker=marker)

	# set x-axis tick marks to region as a category
	# how do I do this with ax. instead of global plt. ?
	# does not work
	#ax.set_xticklabels(regionList)
	plt.xticks([0,1], hmtListLabel)
	#ax.set_xticks(regionList)

	if plotMean:
		# this is for (Superior, inferior)
		if 1:
			sMean, sSD, sSEM, sMedian, sN = printStats(superiorList, verbose=False)
			iMean, iSD, iSEM, iMedian, iN = printStats(inferiorList, verbose=False)
			xMeanPlot = [-0.1, 1.1]
			ax.errorbar(xMeanPlot, [sMean, iMean], yerr=[sSEM, iSEM],
						linewidth=4, markersize=8, marker='s')

		# v2 this follows regions
		# THIS IS NOT WORKING !!!!!!!!!!!!!!
		if 0:
			xRegionPlot = []
			yRegionMean = []
			yRegionSEM = []
			#for thisRegionData in regionListData:
			for sanIdx, sanStr in enumerate(sanList):
				for regionIdx, region in enumerate(regionList):
					thisRegionData = regionListData[sanIdx]
					print('san:', sanStr, 'region:', region, 'thisRegionData:', thisRegionData)
					regionMean, regionSD, regionSEM, regionMedian, regionN = \
										printStats(thisRegionData, verbose=False)
					xRegionPlot.append(regionIdx - 0.1)
					yRegionMean.append(regionMean)
					yRegionSEM.append(regionSEM)
			ax.errorbar(xRegionPlot, yRegionMean, yerr=yRegionSEM,
						color='0.4', linewidth=3, markersize=8, marker='s')

	plt.xlabel('')
	if channel==1:
		yLabelStr = 'HCN4\nPercent of Volume'
	elif channel==2:
		yLabelStr = 'Vasculature\nPercent of Volume'
	plt.ylabel(f'{yLabelStr} ($\mu$m^3)')

	# set the number of ticks
	numOnXAxis = len(regionList)
	plt.locator_params(axis='x', nbins=numOnXAxis)

	#
	plt.show()

	# each list is for san1/2/3/4
	return superiorList, inferiorList, ax

def plotMeanDist(csvFile = '../hcn4-Distance-Result.csv', statCol='mean'):
	"""
	plot mean dist of hcn4 to nearest vasculature

	params:
		statCol: ('mean', 'median')

	todo:	add sd/se to .csv file
			add a histogram plot
	"""

	defaultPlotLayout()

	# csvFile is generated in aicsMyocyteDistToVasc.py
	# it spans all of (san1 .. san2) and (head, mid,tail)

	# load csv into pd dataframe
	#csvFile = '../hcn4-Distance-Result.csv'
	df = pd.read_csv(csvFile)

	sanList = ['SAN1', 'SAN2', 'SAN3', 'SAN4']
	sanMarkers = ['o', '^', 's', 'd']
	hmtList = ['head', 'mid', 'tail']
	hmtList = ['head', 'tail']
	hmtListLabel = ['Superior', 'Inferior']

	# column to pull plot values form
	#statCol = 'mean'
	dataList = []
	superiorList = []
	inferiorList = []
	for sanStr in sanList:
		# & has higher precident than ==
		#oneList = df[ (df['SAN']==sanStr) ]['mean'].tolist()
		oneList = df[ (df['SAN']==sanStr) & df['headMidTail'].isin(hmtList) ][statCol].tolist()
		dataList.append(oneList)
		superiorList.append(oneList[0])
		inferiorList.append(oneList[1])
		print(sanStr, oneList)

	colorChars = ['r', 'g', 'b', 'y'] # one color for each of SAN1, SAN2, ...
	colorChars = ['k', 'k', 'k', 'k'] # one color for each of SAN1, SAN2, ...
	colorChars = ["0.8", "0.8", "0.8", "0.8"] # one color for each of SAN1, SAN2, ...

	fig,ax = plt.subplots(1, figsize=(6,6)) # need constrained_layout=True to see axes titles
	for idx, data in enumerate(dataList):
		colorChar = colorChars[idx]
		marker = sanMarkers[idx]
		#ax.plot(hmtList, data, colorChar)
		ax.plot(data, color=colorChar,
			linewidth=3, markersize=6, marker=marker)

	# set x-axis tick marks to region as a category
	# how do I do this with ax. instead of global plt. ?
	# does not work
	#ax.set_xticklabels(regionList)
	plt.xticks([0,1], hmtListLabel)

	plotMean = True
	if plotMean:
		# this is for (Superior, inferior)
		if 1:
			sMean, sSD, sSEM, sMedian, sN = printStats(superiorList, verbose=False)
			iMean, iSD, iSEM, iMedian, iN = printStats(inferiorList, verbose=False)
			xMeanPlot = [-0.1, 1.1]
			ax.errorbar(xMeanPlot, [sMean, iMean], yerr=[sSEM, iSEM],
						linewidth=4, markersize=8, marker='s')

	yLabel = statCol[0].upper() + statCol[1:]
	plt.xlabel('')
	plt.ylabel(f'{yLabel} HCN4 Distance\nto Vasculature ($\mu$m)')

	# set the number of ticks
	numOnXAxis = len(hmtList)
	plt.locator_params(axis='x', nbins=numOnXAxis)

	#
	plt.show()

	return superiorList, inferiorList, ax

if __name__ == '__main__':

	# this works, plot the mean dist of hcn4 pixels to nearest vasulature
	if 0:
		plotMeanDist()

	# plot the density of a ch1/ch2 mask in % um^3
	if 0:
		channel = 2
		plotMaskDensity(channel)

	if 0:
		# SAN2 is well behaved with one distribution
		# showing larger distances in tail versus shorter in head
		# san 2
		pathList = [
			'/media/cudmore/data/san-density/SAN2/SAN2_head/aicsAnalysis/SAN2_head_ch2.tif',
			'/media/cudmore/data/san-density/SAN2/SAN2_mid/aicsAnalysis/SAN2_mid_ch2.tif',
			'/media/cudmore/data/san-density/SAN2/SAN2_tail/aicsAnalysis/SAN2_tail_ch2.tif',
		]
		# this has bimodal distribution ???
		# san 3
		'''
		pathList = [
			'/media/cudmore/data/san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch2.tif',
			'/media/cudmore/data/san-density/SAN3/SAN3_mid/aicsAnalysis/SAN3_mid_ch2.tif',
			'/media/cudmore/data/san-density/SAN3/SAN3_tail/aicsAnalysis/SAN3_tail_ch2.tif',
		]
		'''
		# this has bimodal distribution ???
		# san 4
		'''
		pathList = [
			'/media/cudmore/data/san-density/SAN4/SAN4_head/aicsAnalysis/SAN4_head_ch2.tif',
			'/media/cudmore/data/san-density/SAN4/SAN4_mid/aicsAnalysis/SAN4_mid_ch2.tif',
			'/media/cudmore/data/san-density/SAN4/SAN4_tail/aicsAnalysis/SAN4_tail_ch2.tif',
		]
		'''

		'''
		for path in pathList:
			plot_hcn4_dist_hist(path)
		'''

		plot_hcn4_dist_hist(pathList)

	if 1:
		pathList = []

		# SAN2
		pathList += [
					'/media/cudmore/data/san-density/SAN2/SAN2_head/aicsAnalysis/SAN2_head_ch2.tif',
					'/media/cudmore/data/san-density/SAN2/SAN2_mid/aicsAnalysis/SAN2_mid_ch2.tif',
					'/media/cudmore/data/san-density/SAN2/SAN2_tail/aicsAnalysis/SAN2_tail_ch2.tif',
					]
		# SAN3
		'''
		pathList += [
					'/media/cudmore/data/san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch2.tif',
					'/media/cudmore/data/san-density/SAN3/SAN3_mid/aicsAnalysis/SAN3_mid_ch2.tif',
					'/media/cudmore/data/san-density/SAN3/SAN3_tail/aicsAnalysis/SAN3_tail_ch2.tif',
					]
		'''
		# SAN4
		'''
		pathList += [
			'/media/cudmore/data/san-density/SAN4/SAN4_head/aicsAnalysis/SAN4_head_ch2.tif',
			'/media/cudmore/data/san-density/SAN4/SAN4_mid/aicsAnalysis/SAN4_mid_ch2.tif',
			'/media/cudmore/data/san-density/SAN4/SAN4_tail/aicsAnalysis/SAN4_tail_ch2.tif',
		]
		'''
		tmpPathList = []
		tmpPathList += [
		    '/media/cudmore/data/san-density/SAN1/SAN1_head/aicsAnalysis/SAN1_head_ch2.tif',
		    #'/media/cudmore/data/san-density/SAN1/SAN1_mid/aicsAnalysis/SAN1_mid_ch2.tif',
		    '/media/cudmore/data/san-density/SAN1/SAN1_tail/aicsAnalysis/SAN1_tail_ch2.tif',
		    ]
		tmpPathList += [
		    '/media/cudmore/data/san-density/SAN2/SAN2_head/aicsAnalysis/SAN2_head_ch2.tif',
		    #'/media/cudmore/data/san-density/SAN2/SAN2_mid/aicsAnalysis/SAN2_mid_ch2.tif',
		    '/media/cudmore/data/san-density/SAN2/SAN2_tail/aicsAnalysis/SAN2_tail_ch2.tif',
		    ]
		# SAN3
		tmpPathList += [
		    '/media/cudmore/data/san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch2.tif',
		    #'/media/cudmore/data/san-density/SAN3/SAN3_mid/aicsAnalysis/SAN3_mid_ch2.tif',
		    '/media/cudmore/data/san-density/SAN3/SAN3_tail/aicsAnalysis/SAN3_tail_ch2.tif',
		    ]
		# SAN4
		tmpPathList += [
		    '/media/cudmore/data/san-density/SAN4/SAN4_head/aicsAnalysis/SAN4_head_ch2.tif',
		    #'/media/cudmore/data/san-density/SAN4/SAN4_mid/aicsAnalysis/SAN4_mid_ch2.tif',
		    '/media/cudmore/data/san-density/SAN4/SAN4_tail/aicsAnalysis/SAN4_tail_ch2.tif',
		    ]
		pathList = tmpPathList

		# all slabs contribute
		if 0:
			plotSlabDiamHist(pathList)
		# plot mDiam of each edge
		if 1:
			plotEdgeDiamHist(pathList)
		if 0:
			plot_hcn4_dist_hist(pathList)
