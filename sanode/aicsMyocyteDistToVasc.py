"""
20201102

Calculate distance of each pixel in hcn4 mask (_ch1_mask.tif)
to nearest vessel using vasc edt (_ch2_edt.tif)

_edt.tif has values in um

_mask.py is made in (aicsCell.py and aicsVasc.py)
_edt.tif is made in aicsDistMap.py

We will start with the mean/sd/se

But really want to look at histograms to be sure we do not include
tons of small/large distance outliers
"""

import math, json

import numpy as np

import tifffile

import aicsBlankSlices

def _printStackParams(name, myStack):
	#print('  ', name, type(myStack), myStack.shape, myStack.dtype, 'dtype.char:', myStack.dtype.char, 'min:', np.min(myStack), 'max:', np.max(myStack))
	print('  ', name, myStack.shape, 'dtype:', myStack.dtype,
				'dtype.char:', myStack.dtype.char,
		)
	print('  ', 'min:', np.nanmin(myStack),
		'max:', np.nanmax(myStack),
		'mean:', np.nanmean(myStack))

def aicsMyocyteDistToVasc(path, verbose=False):
	"""
	params:
		path: full path to _ch2.tif
	returns:
		thresholdDict, thresholdDistances
	"""

	print('=== aicsMyocyteDistToVasc()', path)

	# shared by all _ch1/_ch2 stacks
	(maskStart, maskStop) = aicsBlankSlices.getTopBottom(path)

	# hcn4 mask
	ch1MaskPath = path.replace('_ch2.tif', '')
	ch1MaskPath += '_ch1_mask.tif'
	maskData = tifffile.imread(ch1MaskPath)
	maskData = maskData.astype(np.bool) # maskData is coming in as 0/1 but dtyle np.uint8
	# blank out upper/lower slices
	maskData = aicsBlankSlices.blankOutStack(maskData, maskStart, maskStop, fillValue=False)
	if verbose: _printStackParams('  hcn4 mask after blanking', maskData)

	# vascular edt
	ch2EdtPath = path.replace('_ch2.tif', '_ch2_edt.tif')
	edtData = tifffile.imread(ch2EdtPath)
	# blank out upper/lower slices
	edtData = aicsBlankSlices.blankOutStack(edtData, maskStart, maskStop, fillValue=np.nan)
	if verbose: _printStackParams('  vasc edt after blanking', edtData)

	# for every pixel in hcn4 mask, get its distance from vascular edt
	# assuming maskData is dtype bool
	# goodDistance looses it shape
	# todo: if hcn4 mask pixel falls into vasc edt pixel of 0 dist then ignore
	#	more generally, ignore all vasc edt distance < 0.1 (or similar)

	goodDistances = edtData[maskData]

	if verbose: _printStackParams('  goodDistances', goodDistances)

	# reject hcn4 pixels that fall really close to vasculature
	minVascDistance = 0.2
	thresholdDistances = np.where(edtData[maskData] < minVascDistance, np.nan, edtData[maskData])
	if verbose: _printStackParams('  thresholdDistances', thresholdDistances)

	numberOfPixels = thresholdDistances.size
	numberOfNonNan = np.count_nonzero(~np.isnan(thresholdDistances))

	#
	# return a dict, make multiple columsn with head/mid/tail
	hmtStr = ''
	if '_head_' in path:
		hmtStr = 'head'
	elif '_mid_' in path:
		hmtStr = 'mid'
	elif '_tail_' in path:
		hmtStr = 'tail'

	sanStr = ''
	if 'SAN1' in path:
		sanStr = 'SAN1'
	elif 'SAN2' in path:
		sanStr = 'SAN2'
	elif 'SAN3' in path:
		sanStr = 'SAN3'
	elif 'SAN4' in path:
		sanStr = 'SAN4'

	thresholdDict = {} #getDefaultDict() #{}
	thresholdDict['path'] = path
	thresholdDict['SAN'] = sanStr
	thresholdDict['headMidTail'] = hmtStr
	'''
	thresholdDict[hmtStr + '_' + 'numPixels'] = numberOfPixels # total number of pixels in mask
	thresholdDict[hmtStr + '_' + 'numberOfNonNan'] = numberOfNonNan # these contribute to the mean/sd
	thresholdDict[hmtStr + '_' + 'min'] = float(np.nanmin(thresholdDistances))
	thresholdDict[hmtStr + '_' + 'max'] = float(np.nanmax(thresholdDistances))
	thresholdDict[hmtStr + '_' + 'mean'] = float(np.nanmean(thresholdDistances))
	'''
	thresholdDict['numPixels'] = numberOfPixels # total number of pixels in mask
	thresholdDict['numberOfNonNan'] = numberOfNonNan # these contribute to the mean/sd (e.g. n)
	thresholdDict['min'] = float(np.nanmin(thresholdDistances))
	thresholdDict['max'] = float(np.nanmax(thresholdDistances))
	thresholdDict['mean'] = float(np.nanmean(thresholdDistances))
	thresholdDict['std'] = float(np.nanstd(thresholdDistances))
	sem = float(np.nanstd(thresholdDistances)) / math.sqrt(numberOfNonNan)
	thresholdDict['sem'] = sem

	# can't create a pd dataframe with a key as a list?
	#thresholdDict['rawDist'] = thresholdDistances.tolist()

	# todo: make simple jupyter notebook to plot this distribution
	return thresholdDict, thresholdDistances

'''
def getDefaultDict():
	"""
	all returned dicts need same keys so they line up in saved .csv
	"""
	hmtList = ['head', 'mid', 'tail']
	retDict = {}
	retDict['path'] = ''
	retDict['SAN'] = ''
	retDict['headMidTail'] = ''
	for hmtStr in hmtList:
		retDict[hmtStr + '_' + 'numPixels'] = '' # total number of pixels in mask
		retDict[hmtStr + '_' + 'numberOfNonNan'] = '' # these contribute to the mean/sd
		retDict[hmtStr + '_' + 'min'] = ''
		retDict[hmtStr + '_' + 'max'] = ''
		retDict[hmtStr + '_' + 'mean'] = ''
	return retDict
'''

if __name__ == '__main__':

	# do one
	if 0:
		path = '/media/cudmore/data/san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch2.tif'
		aicsMyocyteDistToVasc(path)

	# do batch
	if 1:
		# san1
		pathList = [
			'/media/cudmore/data/san-density/SAN1/SAN1_head/aicsAnalysis/SAN1_head_ch2.tif',
			'/media/cudmore/data/san-density/SAN1/SAN1_mid/aicsAnalysis/SAN1_mid_ch2.tif',
			#'/media/cudmore/data/san-density/SAN1/SAN1_tail/aicsAnalysis/SAN1_tail_ch2.tif',
		]
		# san2
		pathList += [
			'/media/cudmore/data/san-density/SAN2/SAN2_head/aicsAnalysis/SAN2_head_ch2.tif',
			'/media/cudmore/data/san-density/SAN2/SAN2_mid/aicsAnalysis/SAN2_mid_ch2.tif',
			'/media/cudmore/data/san-density/SAN2/SAN2_tail/aicsAnalysis/SAN2_tail_ch2.tif',
		]
		# san3
		pathList += [
			'/media/cudmore/data/san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch2.tif',
			'/media/cudmore/data/san-density/SAN3/SAN3_mid/aicsAnalysis/SAN3_mid_ch2.tif',
			'/media/cudmore/data/san-density/SAN3/SAN3_tail/aicsAnalysis/SAN3_tail_ch2.tif',
		]
		# san4
		pathList += [
			'/media/cudmore/data/san-density/SAN4/SAN4_head/aicsAnalysis/SAN4_head_ch2.tif',
			'/media/cudmore/data/san-density/SAN4/SAN4_mid/aicsAnalysis/SAN4_mid_ch2.tif',
			'/media/cudmore/data/san-density/SAN4/SAN4_tail/aicsAnalysis/SAN4_tail_ch2.tif',
		]

		import pandas as pd

		for pandasIdx, path in enumerate(pathList):
			thresholdDict, thresholdDistances = aicsMyocyteDistToVasc(path)

			#print(json.dumps(thresholdDict, indent=2))

			# save to csv with pandas
			csvPath = '/home/cudmore/Sites/saNode/hcn4-Distance-Result.csv'
			df = pd.DataFrame(thresholdDict, index=[pandasIdx])
			#doHeader = True #pandasIdx==0
			df.to_csv(csvPath, header=pandasIdx==0, mode='a')
