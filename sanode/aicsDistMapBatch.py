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
	'''
	pathList = [
		# san1 _ch1
		#'/media/cudmore/data/san-density/SAN1/SAN1_head/aicsAnalysis/SAN1_head_ch1.tif',
		#'/media/cudmore/data/san-density/SAN1/SAN1_mid/aicsAnalysis/SAN1_mid_ch1.tif',
		'/media/cudmore/data/san-density/SAN1/SAN1_tail/aicsAnalysis/SAN1_tail_ch1.tif',
		# san1 _ch2
		#'/media/cudmore/data/san-density/SAN1/SAN1_head/aicsAnalysis/SAN1_head_ch2.tif',
		#'/media/cudmore/data/san-density/SAN1/SAN1_mid/aicsAnalysis/SAN1_mid_ch2.tif',
		'/media/cudmore/data/san-density/SAN1/SAN1_tail/aicsAnalysis/SAN1_tail_ch2.tif',
	]
	'''

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

	# san7
	# on reboot, my data drives keeps getting mounted on /media/cudmore/data1
	dataPath = '/media/cudmore/data1/'

	'''
	pathList = [
		# san7 _ch1
		# head
		f'{dataPath}san-density/SAN7/SAN7_head/aicsAnalysis/20201202__0001_ch1.tif',
		f'{dataPath}san-density/SAN7/SAN7_head/aicsAnalysis/20201202__0002_ch1.tif',

		# mid
		f'{dataPath}san-density/SAN7/SAN7_mid/aicsAnalysis/20201202__0008_ch1.tif',
		f'{dataPath}san-density/SAN7/SAN7_mid/aicsAnalysis/20201202__0009_ch1.tif',
		f'{dataPath}san-density/SAN7/SAN7_mid/aicsAnalysis/20201202__0010_ch1.tif',
		f'{dataPath}san-density/SAN7/SAN7_mid/aicsAnalysis/20201202__0011_ch1.tif',

		# tail
		f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0003_ch1.tif',
		f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0004_ch1.tif',
		f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0005_ch1.tif',
		f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0006_ch1.tif',
		f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0007_ch1.tif',

		# san7 _ch2
		# head
		f'{dataPath}san-density/SAN7/SAN7_head/aicsAnalysis/20201202__0001_ch2.tif',
		f'{dataPath}san-density/SAN7/SAN7_head/aicsAnalysis/20201202__0002_ch2.tif',

		# mid
		f'{dataPath}san-density/SAN7/SAN7_mid/aicsAnalysis/20201202__0008_ch2.tif',
		f'{dataPath}san-density/SAN7/SAN7_mid/aicsAnalysis/20201202__0009_ch2.tif',
		f'{dataPath}san-density/SAN7/SAN7_mid/aicsAnalysis/20201202__0010_ch2.tif',
		f'{dataPath}san-density/SAN7/SAN7_mid/aicsAnalysis/20201202__0011_ch2.tif',

		# tail
		f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0003_ch2.tif',
		f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0004_ch2.tif',
		f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0005_ch2.tif',
		f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0006_ch2.tif',
		f'{dataPath}san-density/SAN7/SAN7_tail/aicsAnalysis/20201202__0007_ch2.tif',
	]
	'''

	# san8
	channel = 2
	pathList = [
		f'{dataPath}san-density/SAN8/SAN8_head/aicsAnalysis/SAN8_head_ch{channel}.tif',
		f'{dataPath}san-density/SAN8/SAN8_mid/aicsAnalysis/SAN8_mid_ch{channel}.tif',
		f'{dataPath}san-density/SAN8/SAN8_tail/aicsAnalysis/SAN8_tail_ch{channel}.tif',
	]

	# remember, was NEED TO LIMIT top/bottom slice with aicsBlankSlices.getTopBottom(path)

	m = len(pathList)
	for idx, path in enumerate(pathList):
		print(f'\n{idx+1} of {m} {path}')

		if not os.path.isfile(path):
			print('ERROR: aicsDistMapBath() file does not exist:', path)
			continue

		(maskStart, maskStop) = aicsBlankSlices.getTopBottom(path)
		# we require start/stop
		if maskStart is None or maskStop is None:
			print('  error: aicsDistMapBatch.__main__ did not get start/stop for path', path)
		else:
			print('  maskStart:', maskStart)
			print('  maskStop:', maskStop)
			aicsDistMap.aicsDistMap(path, maskStart=maskStart, maskStop=maskStop)
