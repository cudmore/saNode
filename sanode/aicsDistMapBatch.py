"""
run aicsDistMap.aicsDistMap on a number of files

aicsDistMap.aicsDistMap(path) creates _edt.tif with um distance of
	each pixel not in the mask to the nearest pixel in the mask

"""

import os

import aicsDistMap
import aicsBlankSlices

if __name__ == '__main__':

	#
	# san1
	pathList = [
		# san1 _ch1
		'/media/cudmore/data/san-density/SAN1/SAN1_head/aicsAnalysis/SAN1_head_ch1.tif',
		'/media/cudmore/data/san-density/SAN1/SAN1_mid/aicsAnalysis/SAN1_mid_ch1.tif',
		#'/media/cudmore/data/san-density/SAN1/SAN1_tail/aicsAnalysis/SAN1_tail_ch1.tif',
		# san1 _ch2
		'/media/cudmore/data/san-density/SAN1/SAN1_head/aicsAnalysis/SAN1_head_ch2.tif',
		'/media/cudmore/data/san-density/SAN1/SAN1_mid/aicsAnalysis/SAN1_mid_ch2.tif',
		#'/media/cudmore/data/san-density/SAN1/SAN1_tail/aicsAnalysis/SAN1_tail_ch2.tif',
	]

	#
	# san2
	'''
	pathList = [
		# san2 _ch1
		'/media/cudmore/data/san-density/SAN2/SAN2_head/aicsAnalysis/SAN2_head_ch1.tif',
		'/media/cudmore/data/san-density/SAN2/SAN2_mid/aicsAnalysis/SAN2_mid_ch1.tif',
		'/media/cudmore/data/san-density/SAN2/SAN2_tail/aicsAnalysis/SAN2_tail_ch1.tif',
		# san2 _ch2
		'/media/cudmore/data/san-density/SAN2/SAN2_head/aicsAnalysis/SAN2_head_ch2.tif',
		'/media/cudmore/data/san-density/SAN2/SAN2_mid/aicsAnalysis/SAN2_mid_ch2.tif',
		'/media/cudmore/data/san-density/SAN2/SAN2_tail/aicsAnalysis/SAN2_tail_ch2.tif',
	]
	'''

	#
	# san3
	'''
	pathList = [
		# san3 _ch1
		'/media/cudmore/data/san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch1.tif',
		'/media/cudmore/data/san-density/SAN3/SAN3_mid/aicsAnalysis/SAN3_mid_ch1.tif',
		'/media/cudmore/data/san-density/SAN3/SAN3_tail/aicsAnalysis/SAN3_tail_ch1.tif',
		# san3 _ch2
		'/media/cudmore/data/san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch2.tif',
		'/media/cudmore/data/san-density/SAN3/SAN3_mid/aicsAnalysis/SAN3_mid_ch2.tif',
		'/media/cudmore/data/san-density/SAN3/SAN3_tail/aicsAnalysis/SAN3_tail_ch2.tif',
	]
	'''

	#
	# san4
	'''
	pathList = [
		# san3 _ch1
		'/media/cudmore/data/san-density/SAN4/SAN4_head/aicsAnalysis/SAN4_head_ch1.tif',
		'/media/cudmore/data/san-density/SAN4/SAN4_mid/aicsAnalysis/SAN4_mid_ch1.tif',
		'/media/cudmore/data/san-density/SAN4/SAN4_tail/aicsAnalysis/SAN4_tail_ch1.tif',
		# san3 _ch2
		'/media/cudmore/data/san-density/SAN4/SAN4_head/aicsAnalysis/SAN4_head_ch2.tif',
		'/media/cudmore/data/san-density/SAN4/SAN4_mid/aicsAnalysis/SAN4_mid_ch2.tif',
		'/media/cudmore/data/san-density/SAN4/SAN4_tail/aicsAnalysis/SAN4_tail_ch2.tif',
	]
	'''

	# remember, was NEED TO LIMIT top/bottom slice with aicsBlankSlices.getTopBottom(path)

	m = len(pathList)
	for idx, path in enumerate(pathList):
		print(f'\n{idx+1} of {m} {path}')

		if not os.path.exists(path):
			print('ERROR: aicsDistMapBath() path does not exist:', path)
			continue

		(maskStart, maskStop) = aicsBlankSlices.getTopBottom(path)
		# we require start/stop
		if maskStart is None or maskStop is None:
			print('  error: aicsDistMapBatch.__main__ did not get start/stop for path', path)
		else:
			print('  maskStart:', maskStart)
			print('  maskStop:', maskStop)
			aicsDistMap.aicsDistMap(path, maskStart=maskStart, maskStop=maskStop)
