"""
20201102

plot

	- mean dist from hcn4 to vasc
	- histograms of dist from hcn4 to vasc

	- density of vasc mask (no histograms)

	- mean diameter of slabs
	- histograms of slab diameter
"""

import os

import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt

import bimpy

import aicsMyocyteDistToVasc

def defaultPlotLayout():

	plotForTalk = False

	if plotForTalk:
		plt.style.use('dark_background')

	fontSize = 12
	if plotForTalk:
		fontSize = 14

	mpl.rcParams['figure.figsize'] = [3.0, 4.0]
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

def printStats(dataList):
	theMin = round(np.nanmin(dataList),2)
	theMax = round(np.nanmax(dataList),2)
	theMean = round(np.nanmean(dataList),2)
	theSD = round(np.nanstd(dataList),2)
	theNum = np.count_nonzero(~np.isnan(dataList))
	print(f'  mean:{theMean} sd:{theSD} n:{theNum} min:{theMin} max:{theMax}')

def plotEdgeDiamHist(pathList, minNumberOfSlabs=5):
	"""
	each edge contributes to the hist (not each slab)
	"""

	print('plotEdgeDiamHist():')

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
			print(f'bPyQtPlot.plotEdgeDiamHist() is not plotting {xStat}, it is all np.nan')
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
	for idx, path in enumerate(pathList):
		theDiameters = meanEdgeDiamList[idx] # pixels
		print(f'{idx+1} path:{path}')
		print(f'  x/y/z voxel size:{voxelSizeList[idx]}')
		printStats(theDiameters)

	# set up plot
	defaultPlotLayout()
	fig,axs = plt.subplots(3, 1, figsize=(6,5)) # need constrained_layout=True to see axes titles
	cumFig, cumAxis = plt.subplots(1,1)
	nSlabsFig, nSlabsAxis = plt.subplots(3, 1, figsize=(6,5))

	# plot a number of hist
	bins = [(x+1)*(xVoxel) for x in range(30)]
	#bins = 'auto'

	colorList = ['r', 'g', 'b']

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

		axs[idx].hist(theDiameters, bins=bins, color=color,
						histtype='bar', edgecolor='k', label=label,
						density=True)

		# add a legend
		axs[idx].legend(frameon=False, handlelength=0, handletextpad=-20)
		if idx==2:
			pass
		else:
			axs[idx].set_xticklabels([])
		if idx == 2:
			axs[idx].set_xlabel('Vessel Segment Diameter ($\mu$m)')
		if idx == 1:
			axs[idx].set_ylabel('Probability')
		axs[idx].set_xlim(xAxisMin, xAxisMax) # um

		# plot cumulative
		n, bins, patches = cumAxis.hist(theDiameters, histtype='step',
							bins=bins, color=color, cumulative=True, density=True, linewidth=2)
		cumAxis.set_xlim(xAxisMin, xAxisMax) # um
		cumAxis.set_xlabel('Vessel Segment Diameter ($\mu$m)')
		cumAxis.set_ylabel('Probability')

		# plot nSlabs versus diam
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

def plot_hcn4_dist_hist(pathList):
	"""
	Plot distribution of distance from each hcn4 mask pixel to nearest vasculature

	params:
		path: full path to _ch2.tif

	plot head/mid/tail
	"""

	# set up plot
	defaultPlotLayout()
	fig,axs = plt.subplots(3, 1, figsize=(7,3)) # need constrained_layout=True to see axes titles

	# calculate
	for idx, path in enumerate(pathList):
		# calculate the distance of each hcn4 pixel to nearest vasculature
		thresholdDict, thresholdDistances = aicsMyocyteDistToVasc.aicsMyocyteDistToVasc(path)

		# make a histogram of thresholdDistances (includes nan)

		print('  before removing nan:', thresholdDistances.shape)

		numberOfNonNan = np.count_nonzero(~np.isnan(thresholdDistances))
		print('  numberOfNonNan:', numberOfNonNan)

		# remove nan
		goodDistances = thresholdDistances[~np.isnan(thresholdDistances)]
		print('  after removing nan:', goodDistances.shape)


		numBins = 100
		axs[idx].hist(goodDistances, bins=numBins)

		plt.xlabel('HCN4 distance to vasculature ($\mu$m)')
		plt.ylabel('Count')

	#
	plt.show()

def plotMaskDensity(channel=2, csvFile=None):
	"""
	plot the percent of a mask occupying a valume

	use to plot both hcn4 (ch1) and vasc (chan2)
	there is no mean here, this is an absolute count per stack
	"""

	defaultPlotLayout()

	# load csv into pd dataframe
	if csvFile is None:
		csvFile = f'../Density-Result-ch{channel}.csv'
	df = pd.read_csv(csvFile)

	sanList = ['SAN1', 'SAN2', 'SAN3', 'SAN4']
	hmtList = ['head', 'mid', 'tail']
	hmtList = ['head', 'tail']

	# column to pull plot values form
	statCol = 'vMaskPercent'

	dataList = []
	for sanStr in sanList:
		# & has higher precident than ==
		#oneList = df[ (df['SAN']==sanStr) ]['mean'].tolist()
		oneList = df[ (df['SAN']==sanStr) & df['headMidTail'].isin(hmtList) ][statCol].tolist()
		dataList.append(oneList)
		print(sanStr, oneList)

	colorChars = ['r', 'g', 'b', 'y'] # one color for each of SAN1, SAN2, ...

	fig,ax = plt.subplots(1) # need constrained_layout=True to see axes titles
	for idx, data in enumerate(dataList):
		colorChar = colorChars[idx]
		#ax.plot(hmtList, data, colorChar)
		ax.plot(data,
				color=colorChar)

	plt.xlabel('')
	if channel==1:
		yLabelStr = 'HCN4\nPercent of Volume'
	elif channel==2:
		yLabelStr = 'Vasculature\nPercent of Volume'
	plt.ylabel(f'{yLabelStr} ($\mu$m^3)')

	# set the number of ticks
	numOnXAxis = len(hmtList)
	plt.locator_params(axis='x', nbins=numOnXAxis)

	#
	#plt.show()

def plotMeanDist(csvFile = '../hcn4-Distance-Result.csv'):
	"""
	plot mean dist of hcn4 to nearest vasculature

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
	hmtList = ['head', 'mid', 'tail']
	hmtList = ['head', 'tail']

	# column to pull plot values form
	statCol = 'mean'
	dataList = []
	for sanStr in sanList:
		# & has higher precident than ==
		#oneList = df[ (df['SAN']==sanStr) ]['mean'].tolist()
		oneList = df[ (df['SAN']==sanStr) & df['headMidTail'].isin(hmtList) ][statCol].tolist()
		dataList.append(oneList)
		print(sanStr, oneList)

	colorChars = ['r', 'g', 'b', 'y'] # one color for each of SAN1, SAN2, ...

	fig,ax = plt.subplots(1) # need constrained_layout=True to see axes titles
	for idx, data in enumerate(dataList):
		colorChar = colorChars[idx]
		#ax.plot(hmtList, data, colorChar)
		ax.plot(data, color=colorChar)

	plt.xlabel('')
	plt.ylabel('Mean Distance from HCN4 pixels\nto vasculature ($\mu$m)')

	# set the number of ticks
	numOnXAxis = len(hmtList)
	plt.locator_params(axis='x', nbins=numOnXAxis)

	#
	plt.show()

if __name__ == '__main__':

	# this works, plot the mean dist of hcn4 pixels to nearest vasulature
	if 0:
		plotMeanDist()

	# plot the density of a ch1/ch2 mask in % um^3
	if 0:
		channel = 1
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

		# all slabs contribute
		if 0:
			plotSlabDiamHist(pathList)
		# plot mDiam of each edge
		if 1:
			plotEdgeDiamHist(pathList)
