"""
given a stack, reove 'bad' slices and save anew stack with good slices

bad slices are slices that change by more than thresholdfrom previous
"""

import os, sys
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
import tifffile

def bRemoveBeating(path, doSave=True, doPlot=True):

	#
	# create save path for both (raw, median)
	# make new folder and file from path
	tmpSavePath, tmpSaveFile = os.path.split(path)
	tmpSaveFile = os.path.splitext(tmpSaveFile)[0]
	saveFile = tmpSaveFile + '.tif'
	saveMedianFile = tmpSaveFile + '_median.tif'
	savePath = os.path.join(tmpSavePath, 'removeMotion')
	if not os.path.isdir(savePath):
		print('making output folder:', savePath)
		os.mkdir(savePath)
	rawPath = os.path.join(savePath, saveFile)
	medianPath = os.path.join(savePath, saveMedianFile)

	print('rawPath:', rawPath)
	print('medianPath:', medianPath)

	loadedMedian = False
	if os.path.isfile(medianPath):
		# just load the median
		print('loading medianPath:', medianPath)
		stackData = tifffile.imread(medianPath)
		loadedMedian = True
	else:
		print('loading path:', path)
		stackData = tifffile.imread(path)

	print('  ', stackData.shape)

	if not loadedMedian:
		print('median filter, please wait ...')
		stackData = scipy.ndimage.median_filter(stackData, size=(1,2,2))
		print('saving medianPath:', medianPath)
		tifffile.imsave(medianPath, stackData)

	slices, rows, cols = stackData.shape

	#
	# v2 is calculating difference of each frame j from one reference frame i
	referenceFrame = 4 # (frame 5 in Fiji)
	referenceFrame = 444 # (frame 445 in Fiji)
	referenceFrame = 0 # (frame 1 in Fiji)
	referenceSlice = stackData[referenceFrame,:,:]
	sliceDiffList = [np.nan] * slices
	#debugSlices = slices
	debugSlices = 10
	for slice in range(debugSlices):
		if slice == 0:
			continue
		if slice == referenceFrame:
			continue
		#prevSlice = stackData[slice-1,:,:]
		thisSlice = stackData[slice,:,:]
		sliceDiff = thisSlice - referenceSlice
		sliceDiff = np.sum(sliceDiff)
		sliceDiffList[slice] = sliceDiff

	'''
	print('calculating between slice difference')
	sliceDiffList = [np.nan] * slices
	for slice in range(slices):
		if slice == 0:
			continue
		prevSlice = stackData[slice-1,:,:]
		thisSlice = stackData[slice,:,:]
		sliceDiff = thisSlice - prevSlice
		sliceDiff = np.sum(sliceDiff)
		sliceDiffList[slice] = sliceDiff
	'''

	meanDiff = np.nanmean(sliceDiffList)

	sliceDiffList -= meanDiff # center around 0
	sliceDiffList = [abs(diff) for diff in sliceDiffList]

	sdDiff = np.nanstd(sliceDiffList)
	plusOneSd =  sdDiff
	plusTwoSd =  sdDiff * 2

	# detect beats
	'''
	firstBadList = []
	lastBadList = []
	badList = []
	startSlice = 1 # skip the first few slices
	currentSlice = startSlice
	for slice in np.arange(start=startSlice, stop=slices):
		try:
			currDiff = sliceDiffList[currentSlice]
		except (IndexError) as e:
			break
		if currDiff > plusTwoSd:
			jump1 = currentSlice + 4 # jump beyond intermediate zero crossing
			jump2 = jump1 + 5 # go past end of beat
			# look ahead for return to mean
			firstBadSlice = currentSlice
			lastBadSlice = None
			outlierCount = 0 # keep track of outliers and reject if there are too few
			for j in np.arange(start=jump1, stop=jump2):
				if j > len(sliceDiffList):
					print('jumped past end')
					continue
				if sliceDiffList[j] > plusTwoSd:
					outlierCount += 1
				if sliceDiffList[j] < plusOneSd:
					lastBadSlice = j-1
					break
			if lastBadSlice is None:
				print('  error: finding return to mean from currentSlice:', currentSlice)
			elif outlierCount < 1:
				print('  warning: there was a blip at currentSlice:', currentSlice, '-->> keeping')
			else:
				firstBadList.append(firstBadSlice)
				lastBadList.append(lastBadSlice)
				badList += list(range(firstBadSlice,lastBadSlice+1))
				# change loop
				currentSlice = jump2-1

		#
		currentSlice += 1

	numBad = len(badList)
	numOut = slices - numBad

	print('slices:', slices, 'numBad:', numBad, 'numOut:', numOut)
	print(badList)
	'''

	if doSave:
		#
		# construct a new 'good' stack and save
		outStack = np.zeros((numOut, rows, cols), dtype=np.uint8)
		outSlice = 0
		for slice in np.arange(0,slices):
			if slice not in badList:
				outStack[outSlice,:,:] = stackData[slice,:,:]
				outSlice += 1

		#
		# save new stack after removing bad
		print('saving rawPath:', rawPath)
		tifffile.imsave(rawPath, outStack)

	#
	# plot
	if doPlot:
		# plot from one so we can compare to fiji display of stack
		# in general, slice 1 itself has no diff. Diff = (slice i) - (slice i-1)
		xMinMax = np.arange(start=1, stop=slices+1)

		fig, ax = plt.subplots(1)

		ax.plot(xMinMax, sliceDiffList, '-o', c='k')
		ax.axhline(0, c='r')
		ax.axhline(plusOneSd, linestyle='--', c='r')
		ax.axhline(plusTwoSd, linestyle='--', c='r')

		'''
		yPlot = [sliceDiffList[slice] for slice in firstBadList]
		xPlot = [slice+1 for slice in firstBadList]
		ax.plot(xPlot, yPlot, 'o', c='r')

		yPlot = [sliceDiffList[slice] for slice in lastBadList]
		xPlot = [slice+1 for slice in lastBadList]
		ax.plot(xPlot, yPlot, 'o', c='g')
		'''

		plt.show()

if __name__ == '__main__':

	path = '/media/cudmore/data/20201111/1.tif'

	path = '/media/cudmore/data/20201124/1.tif'
	path = '/media/cudmore/data/20201124/1_cropped.tif'
	#path = '/media/cudmore/data/20201124/9.tif'

	bRemoveBeating(path, doSave=False, doPlot=True)
