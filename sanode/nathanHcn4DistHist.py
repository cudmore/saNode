
import numpy as np
import pandas as pd
import tifffile
import matplotlib.pyplot as plt
import seaborn as sns

"""
[[ 1  2  3  4  5  6]
 [12 11 10  9  8  7]
 [13 14 15 16 17 18]
 [24 23 22 21 20 19]
 [25 26 27 28 29 30]
 [36 35 34 33 32 31]
 [37 38 39 40 41 42]
 [48 47 46 45 44 43]
 [49 50 51 52 53 54]
 [60 59 58 57 56 55]
 [61 62 63 64 65 66]
 [72 71 70 69 68 67]]

all stacks are 640x640

stackXY = 640

top mosaic is (12,6)
top superior stacks are: 10,11,14,15

1 ,2 ,3 ,4 ,5 ,6
12,11,10,9 ,8 ,7
13,14,15,16,17,18

supStartRow = stackXY
supStopRow = supStartRow + stackXY
supStartCol = stackXY
supStopCol = supStartCol + stackXY

bottom mosaic is (14,6)
bottom inferior stacks are 34,35,38,39

1 ,2 ,3 ,4 ,5 , 6
12,11,10,9 , 8, 7
13,14,15,16,17,18
24,23,22,21,20,19
25,26,27,28,29,30
36,35,34,33,32,31
37,38,39,40,41,42

infStartRow = stackXY * 5
infStopRow = infStartRow + stackXY
infStartCol = stackXY * 2
infStopCol = infStartCol + stackXY

"""

def _printStackParams(name, myStack):
	#print('  ', name, type(myStack), myStack.shape, myStack.dtype, 'dtype.char:', myStack.dtype.char, 'min:', np.min(myStack), 'max:', np.max(myStack))
	print('  .', name, myStack.shape, 'dtype:', myStack.dtype,
				'dtype.char:', myStack.dtype.char,
		)
	print('    ', 'min:', np.nanmin(myStack),
		'max:', np.nanmax(myStack),
		'mean:', np.nanmean(myStack),
		'non-nan pixel count:', np.count_nonzero(~np.isnan(myStack))
		)

def run():
	# this is the original, mar15, no trimming
	topHcn4Edt = '/media/cudmore/data/heat-map/san4-raw/san4-top/san4-top-hcn4/san4-top-hcn4_big_3d_edt.tif'
	bottomHcn4Edt = '/media/cudmore/data/heat-map/san4-raw/san4-bottom/san4-bottom-hcn4/san4-bottom-hcn4_big_3d_edt.tif'

	print('loading:', topHcn4Edt)
	topEdtData = tifffile.imread(topHcn4Edt)
	print('loading:', bottomHcn4Edt)
	bottomEdtData = tifffile.imread(bottomHcn4Edt)

	# set all 0 dist to nan (just in case)
	print('  set all 0 to nan')
	topEdtData = np.where(topEdtData==0, np.nan, topEdtData)
	bottomEdtData = np.where(bottomEdtData==0, np.nan, bottomEdtData)

	# set all 0 dist to nan (just in case)
	maxDist = 23 # um
	print('  set all distances >', maxDist, 'to nan')
	topEdtData = np.where(topEdtData>maxDist, np.nan, topEdtData)
	bottomEdtData = np.where(bottomEdtData>maxDist, np.nan, bottomEdtData)

	# remove all dist > long threshold

	#
	# need to select superior/inferior rows/cols from original google docs spreedsheet

	#_printStackParams('topEdtData', topEdtData)
	#_printStackParams('bottomEdtData', bottomEdtData)

	#
	# subsample to grab identified sup/inf from google spreadsheet
	stackXY = 640

	# 20210322, now trimming 15% from all of left/top/right/bottom
	#			ws previously just trimming the bottom
	#trimming 48 left/top/right/bottom pixels
	#original shape: (104, 640, 640)
	#final shape: (104, 544, 544)
	stackXY = 544

	# superior
	supStartRow = stackXY
	supStopRow = supStartRow + stackXY
	supStartCol = stackXY
	supStopCol = supStartCol + stackXY
	print('supStartRow:', supStartRow, 'supStopRow:', supStopRow)
	print('supStartCol:', supStartCol, 'supStopCol:', supStopCol)
	topEdtData = topEdtData[:, supStartRow:supStopRow, supStartCol:supStopCol]
	# inferior
	infStartRow = stackXY * 5
	infStopRow = infStartRow + stackXY
	infStartCol = stackXY * 2
	infStopCol = infStartCol + stackXY
	print('infStartRow:', infStartRow, 'infStopRow:', infStopRow)
	print('infStartCol:', infStartCol, 'infStopCol:', infStopCol)
	bottomEdtData = bottomEdtData[:, infStartRow:infStopRow, infStartCol:infStopCol]

	# debug plot, trying to figure out how to subsample to match google doc superior/inferior
	# in san4 folder, top, I started rows at 640 and then went 640*3
	# in san4 folder, bottom, I started rows at 0 and then went 640*3
	if 0:
		tmpTopMaxProject = np.nanmax(topEdtData, axis=0)
		tmpBottomMaxProject = np.nanmax(bottomEdtData, axis=0)
		fig, axs = plt.subplots(1, 2, sharey=False)
		axs[0].imshow(tmpTopMaxProject)
		axs[1].imshow(tmpBottomMaxProject)
		plt.show()
		sys.exit()

	# number of random samples to chose (upper pixel count is like 119,249,269 and lower like 19,416,724)
	nSample = 100000 #100000 #500000
	print('   flatten')
	topEdtData_flat = np.ravel(topEdtData)
	bottomEdtData_flat = np.ravel(bottomEdtData)
	print(f'  random sample of {nSample} distances')
	topEdtData = np.random.choice(topEdtData_flat, nSample, replace=False)
	bottomEdtData = np.random.choice(bottomEdtData_flat, nSample, replace=False)
	#_printStackParams('after random sample topEdtData', topEdtData)
	#_printStackParams('after random sample bottomEdtData', bottomEdtData)

	'''
	df = pd.DataFrame(columns=['SAN', 'headMidTail', 'hcn4DistToVasc'])

	dfTop = pd.DataFrame()
	dfTop['SAN'] = ['san4'] * nSample
	dfTop['headMidTail'] = ['superior'] * nSample
	dfTop['hcn4DistToVasc'] = topEdtData

	dfBottom = pd.DataFrame()
	dfBottom['SAN'] = ['san4'] * nSample
	dfBottom['headMidTail'] = ['inferior'] * nSample
	dfBottom['hcn4DistToVasc'] = bottomEdtData

	df = dfTop.append(dfBottom, ignore_index = True)

	# save as csv
	print(df)
	'''

	# once save, called plotHcn4Dist_FromCsv()

	if 1:
		print('   plot')
		fig, axs = plt.subplots(1, 1, sharey=False)
		axs= [axs]
		bins = 500
		axs[0].hist(topEdtData, bins=bins, cumulative=True, density=True, histtype='step', color='r')
		axs[0].hist(bottomEdtData, bins=bins, cumulative=True, density=True, histtype='step', color='k')

		axs[0].set_xlabel('HCN4 Distance To Vasculature (um)')
		axs[0].set_ylabel('Probability')

		axs[0].spines['top'].set_visible(False)
		axs[0].spines['right'].set_visible(False)

		# maxDist
		axs[0].set_xlim(0, maxDist-1)

		plt.show()

if __name__ == '__main__':
	run()
