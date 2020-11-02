"""
run aicsDistMap.aicsDistMap on a number of files

aicsDistMap.aicsDistMap(path) creates _edt.tif with um distance of
	each pixel not in the mask to the nearest pixel in the mask

"""

import os

import aicsDistMap

if __name__ == '__main__':

	#
	# san3
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

	# might want to limit the mask in z ???
	maskStartStop = None

	m = len(pathList)
	for idx, path in enumerate(pathList):
		print(f'\n{idx+1} of {m} {path}')
		if not os.path.exists(path):
			print('ERROR: aicsDistMapBath() path does not exist:', path)
		else:
			aicsDistMap.aicsDistMap(path, maskStartStop=maskStartStop)
