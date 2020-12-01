
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
import tifffile

path = '/media/cudmore/data/20201111/1.tif'

stackData = tifffile.imread(path)

print('median filter, please wait ...')
#stackData = scipy.ndimage.median_filter(stackData, size=(1,2,2))

slices, rows, cols = stackData.shape

xMinMax = np.arange(start=1, stop=slices+1)

fig, ax = plt.subplots(1)

sliceDiffList = [np.nan] * slices
for slice in range(slices):
	if slice == 0:
		continue
	prevSlice = stackData[slice-1,:,:]
	thisSlice = stackData[slice,:,:]
	sliceDiff = thisSlice - prevSlice
	sliceDiff = np.sum(sliceDiff)
	sliceDiffList[slice] = sliceDiff

meanDiff = np.nanmean(sliceDiffList)

sliceDiffList -= meanDiff # center around 0
sliceDiffList = [abs(diff) for diff in sliceDiffList]

sdDiff = np.nanstd(sliceDiffList)
plusOneSd =  sdDiff
plusTwoSd =  sdDiff * 2

# detect beats
firstBadList = []
lastBadList = []
startSlice = 5 # skip the first few slices
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
			if sliceDiffList[j] > plusTwoSd:
				outlierCount += 1
			if sliceDiffList[j] < plusOneSd:
				lastBadSlice = j-1
				break
		if lastBadSlice is None:
			print('error finding return to mean from currentSlice:', currentSlice)
		elif outlierCount < 1:
			print('there was a blip at currentSlice:', currentSlice)
		else:
			firstBadList.append(firstBadSlice)
			lastBadList.append(lastBadSlice)
			# change loop
			currentSlice = jump2-1

	#
	currentSlice += 1

# construct a new 'good' stack and save
newStack = [slice for slice in ]

ax.plot(xMinMax, sliceDiffList, '-o', c='k')
ax.axhline(0, c='r')
ax.axhline(plusOneSd, linestyle='--', c='r')
ax.axhline(plusTwoSd, linestyle='--', c='r')

yPlot = [sliceDiffList[slice] for slice in firstBadList]
xPlot = [slice+1 for slice in firstBadList]
ax.plot(xPlot, yPlot, 'o', c='r')

yPlot = [sliceDiffList[slice] for slice in lastBadList]
xPlot = [slice+1 for slice in lastBadList]
ax.plot(xPlot, yPlot, 'o', c='g')

#
plt.show()
