"""
20201102

take a mask _mask.tif and good first/last slice and calculate a density

uses
	_ch1_mask.tif
	_ch2_mask.tif

"""

import os, json
import tifffile
import numpy as np

import bimpy
import aicsBlankSlices

def _printStackParams(name, myStack):
	#print('  ', name, type(myStack), myStack.shape, myStack.dtype, 'dtype.char:', myStack.dtype.char, 'min:', np.min(myStack), 'max:', np.max(myStack))
	print('  ', name, myStack.shape, 'dtype:', myStack.dtype,
				'dtype.char:', myStack.dtype.char,
		)
	print('  ', 'min:', np.nanmin(myStack),
		'max:', np.nanmax(myStack),
		'mean:', np.nanmean(myStack))

# todo: this works for both hcn4 and vasc channels
def aicsMaskDen(path, verbose=False):

	if verbose: print('=== aicsMaskDen()', path)

	# get the first/last good slices
	(maskStart, maskStop) = aicsBlankSlices.getTopBottom(path)
	if verbose: print('  maskStart:', maskStart, 'maskStop:', maskStop)

	if maskStart is None or maskStop is None:
		print('  ERROR: aicsMaskDen.aicsMaskDen got None maskStart/maskStop for path:', path)
		return None

	maskPath, tmpExt = os.path.splitext(path)
	maskPath += '_mask.tif'

	# load voxel x/y/z
	xVoxel, yVoxel, zVoxel = bimpy.util.bTiffFile.readVoxelSize(maskPath)
	pixelVolume = xVoxel * yVoxel * zVoxel
	if verbose: print('  x/y/z voxel is:', xVoxel, yVoxel, zVoxel)

	# load the _mask
	maskData = tifffile.imread(maskPath)
	if verbose: _printStackParams('  0 maskData', maskData)

	# blank bad slices on top/bottom
	maskData = aicsBlankSlices.blankOutStack(maskData, maskStart, maskStop, fillValue=False)
	'''
	if maskStart is not None:
		if verbose: print(f'  aicsMaskDen() is excluding mask slices 0:{maskStart}')
		maskData[0:maskStart, :, :] = False #np.nan
	if maskStop is not None:
		if verbose: print(f'  aicsMaskDen() is excluding mask slices {maskStop}+1:-1')
		maskData[maskStop+1:-1, :, :] = False #np.nan
	'''

	#
	# count all pixels in trimmed volume (exluding slices above maskStart and below maskStop)
	(slices, m, n) = maskData.shape
	numGoodSlices = maskStop-maskStart+1
	totalNumPixels =  numGoodSlices * m * n

	# count all pixels in mask
	numPixelsInMask = np.count_nonzero(maskData)

	# ratio of (pixels in mask) / (total number of pixels)
	maskRatio = numPixelsInMask / totalNumPixels
	maskPercent = numPixelsInMask / totalNumPixels * 100

	# mask as a volume using um^3 pixelVolume
	totalVolume = totalNumPixels * pixelVolume # um^3 volume we analyzed
	vPixelsInMask = numPixelsInMask * pixelVolume
	vMaskRatio = vPixelsInMask / totalVolume
	vMaskPercent = vPixelsInMask / totalVolume * 100

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

	retDict = {}
	retDict['path'] = path
	retDict['SAN'] = sanStr
	retDict['headMidTail'] = hmtStr
	retDict['zPixels'] = maskData.shape[0]
	retDict['xPixels'] = maskData.shape[1]
	retDict['yPixels'] = maskData.shape[2]
	#retDict['xyzVoxel'] = (xVoxel, yVoxel, zVoxel)
	retDict['zVoxel'] = zVoxel
	retDict['xVoxel'] = xVoxel
	retDict['yVoxel'] = yVoxel
	retDict['maskStart'] = maskStart
	retDict['maskStop'] = maskStop

	retDict['numGoodSlices'] = numGoodSlices
	retDict['totalNumPixels'] = totalNumPixels
	retDict['numPixelsInMask'] = numPixelsInMask
	retDict['maskRatio'] = maskRatio
	retDict['maskPercent'] = maskPercent
	# volumes
	retDict['totalVolume'] = totalVolume
	retDict['vPixelsInMask'] = vPixelsInMask
	retDict['vMaskRatio'] = vMaskRatio
	retDict['vMaskPercent'] = vMaskPercent

	if verbose: print(json.dumps(retDict, indent=4))

	return retDict

if __name__ == '__main__':

	# do one
	if 0:
		dataPath = '/media/cudmore/data1/'
		path = f'{dataPath}san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch2.tif'
		aicsMaskDen(path)

	# do batch
	if 1:
		dataPath = '/media/cudmore/data/'
		channel = 1
		# san1
		pathList = [
			f'{dataPath}san-density/SAN1/SAN1_head/aicsAnalysis/SAN1_head_ch{channel}.tif',
			f'{dataPath}san-density/SAN1/SAN1_mid/aicsAnalysis/SAN1_mid_ch{channel}.tif',
			f'{dataPath}san-density/SAN1/SAN1_tail/aicsAnalysis/SAN1_tail_ch2.tif',
		]
		# san2
		pathList += [
			f'{dataPath}san-density/SAN2/SAN2_head/aicsAnalysis/SAN2_head_ch{channel}.tif',
			f'{dataPath}san-density/SAN2/SAN2_mid/aicsAnalysis/SAN2_mid_ch{channel}.tif',
			f'{dataPath}san-density/SAN2/SAN2_tail/aicsAnalysis/SAN2_tail_ch{channel}.tif',
		]
		# san3
		pathList += [
			f'{dataPath}san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch{channel}.tif',
			f'{dataPath}san-density/SAN3/SAN3_mid/aicsAnalysis/SAN3_mid_ch{channel}.tif',
			f'{dataPath}san-density/SAN3/SAN3_tail/aicsAnalysis/SAN3_tail_ch{channel}.tif',
		]
		# san4
		pathList += [
			f'{dataPath}san-density/SAN4/SAN4_head/aicsAnalysis/SAN4_head_ch{channel}.tif',
			f'{dataPath}san-density/SAN4/SAN4_mid/aicsAnalysis/SAN4_mid_ch{channel}.tif',
			f'{dataPath}san-density/SAN4/SAN4_tail/aicsAnalysis/SAN4_tail_ch{channel}.tif',
		]

		# san7
		pathList += [
			# head
			#f'{dataPath}san-density/SAN7/SAN7_head/aicsAnalysis/20201202__0000_ch{channel}.tif',
			f'{dataPath}san-density/SAN7/SAN7_head/aicsAnalysis/20201202__0001_ch{channel}.tif',
			f'{dataPath}san-density/SAN7/SAN7_head/aicsAnalysis/20201202__0002_ch{channel}.tif',

			# mid
			f'{dataPath}san-density/SAN7/SAN7_mid/aicsAnalysis/20201202__0008_ch{channel}.tif',
			f'{dataPath}san-density/SAN7/SAN7_mid/aicsAnalysis/20201202__0009_ch{channel}.tif',
			f'{dataPath}san-density/SAN7/SAN7_mid/aicsAnalysis/20201202__0010_ch{channel}.tif',
			f'{dataPath}san-density/SAN7/SAN7_mid/aicsAnalysis/20201202__0011_ch{channel}.tif',

			# tail
			f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0003_ch{channel}.tif',
			f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0004_ch{channel}.tif',
			f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0005_ch{channel}.tif',
			f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0006_ch{channel}.tif',
			f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0007_ch{channel}.tif',

		]

		# san8
		pathList += [
			f'{dataPath}san-density/SAN8/SAN8_head/aicsAnalysis/SAN8_head_ch{channel}.tif',
			f'{dataPath}san-density/SAN8/SAN8_mid/aicsAnalysis/SAN8_mid_ch{channel}.tif',
			f'{dataPath}san-density/SAN8/SAN8_tail/aicsAnalysis/SAN8_tail_ch{channel}.tif',
		]

		import pandas as pd

		for idx, path in enumerate(pathList):
			if not os.path.isfile(path):
				print('\nERROR: did not find path:', path, '\n')
			retDict = aicsMaskDen(path)
			print(f'\n{idx+1} of {len(pathList)}')
			if retDict is not None:
				#print(json.dumps(retDict, indent=2))
				print('  got good answer')
			else:
				print('  ERROR !!!!!!!!!!!!!!!!!!!!!!')

			# append/save to csv with pandas
			csvPath = f'/home/cudmore/Sites/saNode/Density-Result-ch{channel}.csv'
			df = pd.DataFrame(retDict, index=[idx])
			doHeader = True #pandasIdx==0
			df.to_csv(csvPath, header=idx==0, mode='a')
