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
	pathList = [
		#'/media/cudmore/data/san-density/SAN1/SAN1_head/SAN1_head_ch1.tif',
		#'/media/cudmore/data/san-density/SAN1/SAN1_mid/SAN1_mid_ch1.tif',
		'/media/cudmore/data/san-density/SAN1/SAN1_tail/SAN1_tail_ch1.tif',
	]

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

	#trimPercent = None
	m = len(pathList)
	for idx, path in enumerate(pathList):
		print(f'\n{idx+1} of {m} path:{path}')
		if not os.path.isfile(path):
			print('ERROR: did not find path', path)
		else:
			print('  calling aicsCellBath() path:', path)
			aicsCell.cellDenRun(path) # trimPercent defaults to None
