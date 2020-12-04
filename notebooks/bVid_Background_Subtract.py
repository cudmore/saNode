import os
import numpy as np
import tifffile
import matplotlib.pyplot as plt

inPath = '/media/cudmore/data/20201124/1_cropped.tif'
outPath = '/media/cudmore/data/20201124/1_cropped_bs.tif'

stackData = tifffile.imread(inPath)

slices, rows, cols = stackData.shape

newStack = np.zeros(stackData.shape, dtype=np.uint8)
meanList = [np.nan] * slices

for slice in range(slices):
	theSlice = stackData[slice,:,:]

	theMin = np.nanmin(theSlice)
	theMax = np.nanmax(theSlice)
	theMean = np.nanmean(theSlice)
	#print('slice:', slice, 'theMean:', theMean, theMin, theMax)

	meanList[slice] = theMean

	newSlice = theSlice - theMean
	newSlice[newSlice<0] = 0

	newStack[slice,:,:] = newSlice

tifffile.imsave(outPath, newStack)

plt.plot(meanList)
plt.show()
