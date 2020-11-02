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
	pathList = [
		'/media/cudmore/data/san-density/SAN3/SAN3_head/SAN3_head_ch2.tif',
		'/media/cudmore/data/san-density/SAN3/SAN3_mid/SAN3_mid_ch2.tif',
		'/media/cudmore/data/san-density/SAN3/SAN3_tail/SAN3_tail_ch2.tif',

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
