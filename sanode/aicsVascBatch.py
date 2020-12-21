"""
run aicsVasc.py aicsVasc.vascDenRun(path) for a number of stacks
like for
	san3
		head
		mid
		tail

This takes about 2-3 minutes per file

"""

import os

import aicsVasc

if  __name__ == '__main__':

	# san1
	'''
	pathList = [
		#'/media/cudmore/data/san-density/SAN1/SAN1_head/SAN1_head_ch2.tif',
		#'/media/cudmore/data/san-density/SAN1/SAN1_mid/SAN1_mid_ch2.tif',
		'/media/cudmore/data/san-density/SAN1/SAN1_tail/SAN1_tail_ch2.tif',
	]
	'''

	# san2
	'''
	pathList = [
		'/media/cudmore/data/san-density/SAN2/SAN2_head/SAN2_head_ch2.tif',
		'/media/cudmore/data/san-density/SAN2/SAN2_mid/SAN2_mid_ch2.tif',
		'/media/cudmore/data/san-density/SAN2/SAN2_tail/SAN2_tail_ch2.tif',
	]
	'''

	# SAN3
	'''
	pathList = [
		'/media/cudmore/data/san-density/SAN3/SAN3_head/SAN3_head_ch2.tif',
		'/media/cudmore/data/san-density/SAN3/SAN3_mid/SAN3_mid_ch2.tif',
		'/media/cudmore/data/san-density/SAN3/SAN3_tail/SAN3_tail_ch2.tif',

	]
	'''

	# san4
	'''
	pathList = [
		'/media/cudmore/data/san-density/SAN4/SAN4_head/SAN4_head_ch2.tif',
		'/media/cudmore/data/san-density/SAN4/SAN4_mid/SAN4_mid_ch2.tif',
		'/media/cudmore/data/san-density/SAN4/SAN4_tail/SAN4_tail_ch2.tif',
	]
	'''

	# san 7
	pathList = [
		'/media/cudmore/data/san-density/SAN7/SAN7_head/20201202__0000_ch2.tif',
		'/media/cudmore/data/san-density/SAN7/SAN7_head/20201202__0001_ch2.tif',
		'/media/cudmore/data/san-density/SAN7/SAN7_head/20201202__0002_ch2.tif',

		'/media/cudmore/data/san-density/SAN7/SAN7_tail/20201202__0003_ch2.tif',
		'/media/cudmore/data/san-density/SAN7/SAN7_tail/20201202__0004_ch2.tif',
		'/media/cudmore/data/san-density/SAN7/SAN7_tail/20201202__0005_ch2.tif',
		'/media/cudmore/data/san-density/SAN7/SAN7_tail/20201202__0006_ch2.tif',
		'/media/cudmore/data/san-density/SAN7/SAN7_tail/20201202__0007_ch2.tif',
	]

	trimPercent = None
	m = len(pathList)
	for idx, path in enumerate(pathList):
		print(f'\n{idx+1} of {m} path:{path}')
		if not os.path.isfile(path):
			print('ERROR: did not find path', path)
		else:
			print('  calling aicsCellBath() path:', path)
			# trimPercent does NOT defult to None
			aicsVasc.vascDenRun(path, trimPercent=trimPercent)
