"""
run aicsCell.py aicsCell.cellDenRun(path) for a number of stacks
like for
	san3
		head
		mid
		tail
"""

import os

import aicsCell

if  __name__ == '__main__':

	# san1
	'''
	pathList = [
		#'/media/cudmore/data/san-density/SAN1/SAN1_head/SAN1_head_ch1.tif',
		#'/media/cudmore/data/san-density/SAN1/SAN1_mid/SAN1_mid_ch1.tif',
		'/media/cudmore/data/san-density/SAN1/SAN1_tail/SAN1_tail_ch1.tif',
	]
	'''

	# san2
	'''
	pathList = [
		'/media/cudmore/data/san-density/SAN2/SAN2_head/SAN2_head_ch1.tif',
		'/media/cudmore/data/san-density/SAN2/SAN2_mid/SAN2_mid_ch1.tif',
		'/media/cudmore/data/san-density/SAN2/SAN2_tail/SAN2_tail_ch1.tif',
	]
	'''

	# san3
	'''
	pathList = [
		'/media/cudmore/data/san-density/SAN3/SAN3_head/SAN3_head_ch1.tif',
		'/media/cudmore/data/san-density/SAN3/SAN3_mid/SAN3_mid_ch1.tif',
		'/media/cudmore/data/san-density/SAN3/SAN3_tail/SAN3_tail_ch1.tif',
	]
	'''

	# san4
	'''
	pathList = [
		'/media/cudmore/data/san-density/SAN4/SAN4_head/SAN4_head_ch1.tif',
		'/media/cudmore/data/san-density/SAN4/SAN4_mid/SAN4_mid_ch1.tif',
		'/media/cudmore/data/san-density/SAN4/SAN4_tail/SAN4_tail_ch1.tif',
	]
	'''

	# san 7 - this was NOT taken in a grid - forced to do individual stacks
	'''
	pathList = [
		# head
		#'/media/cudmore/data/san-density/SAN7/SAN7_head/20201202__0000_ch1.tif',
		#'/media/cudmore/data/san-density/SAN7/SAN7_head/20201202__0001_ch1.tif',
		#'/media/cudmore/data/san-density/SAN7/SAN7_head/20201202__0002_ch1.tif',

		# mid
		'/media/cudmore/data1/san-density/SAN7/SAN7_mid/20201202__0008_ch1.tif',
		'/media/cudmore/data1/san-density/SAN7/SAN7_mid/20201202__0009_ch1.tif',
		'/media/cudmore/data1/san-density/SAN7/SAN7_mid/20201202__0010_ch1.tif',
		'/media/cudmore/data1/san-density/SAN7/SAN7_mid/20201202__0011_ch1.tif',

		# tail
		#'/media/cudmore/data/san-density/SAN7/SAN7_tail/20201202__0003_ch1.tif',
		#'/media/cudmore/data/san-density/SAN7/SAN7_tail/20201202__0004_ch1.tif',
		#'/media/cudmore/data/san-density/SAN7/SAN7_tail/20201202__0005_ch1.tif',
		#'/media/cudmore/data/san-density/SAN7/SAN7_tail/20201202__0006_ch1.tif',
		#'/media/cudmore/data/san-density/SAN7/SAN7_tail/20201202__0007_ch1.tif',
	]
	'''

	# san8
	pathList = [
		'/media/cudmore/data1/san-density/SAN8/SAN8_head/SAN8_head_ch1.tif',
		'/media/cudmore/data1/san-density/SAN8/SAN8_mid/SAN8_mid_ch1.tif',
		'/media/cudmore/data1/san-density/SAN8/SAN8_tail/SAN8_tail_ch1.tif',
	]

	#trimPercent = None
	m = len(pathList)
	for idx, path in enumerate(pathList):
		print(f'\n{idx+1} of {m} path:{path}')
		if not os.path.isfile(path):
			print('ERROR: did not find path', path)
		else:
			print('  calling aicsCellBath() path:', path)
			aicsCell.cellDenRun(path) # trimPercent defaults to None
