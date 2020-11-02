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

	# san3
	pathList = [
		'/media/cudmore/data/san-density/SAN3/SAN3_head/SAN3_head_ch1.tif',
		'/media/cudmore/data/san-density/SAN3/SAN3_mid/SAN3_mid_ch1.tif',
		'/media/cudmore/data/san-density/SAN3/SAN3_tail/SAN3_tail_ch1.tif',

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
