"""
this code will
	1) open a napari viewer with an entire grid of Tiff(s)
	2) save a single .tif specified in 'smallDict'

Should be run in a conda environment

conda activate sanode-env
"""

import aicsUtil2 # does not require bimpy

'''
Head: 10, 11, 14, 15 (20200901_SAN4_TOP)
Mid: 57, 58, 63, 64  (20200901_SAN4_TOP)
Tail: 23, 35, 38, 39 (20200914_SAN4_BOTTOM)
'''

gDataPath = '/home/cudmore/data/nathan'
folderStr = '20200901_SAN4_TOP'
dateStr = '20200901'
gridShape = (12,6)

'''
# Head: 10, 11, 14, 15 (20200901_SAN4_TOP)
smallDict = {
	'saveName': 'SAN4_head', # will append _ch1/_ch2 to this
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [
				(1,1), (1,2),
				(2,1), (2,2)
				]
}
'''

'''
#Mid: 57, 58, 63, 64  (20200901_SAN4_TOP)
smallDict = {
	'saveName': 'SAN4_mid', # will append _ch1/_ch2 to this
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [
				(9,2), (9,3),
				(10,2), (10,3),
				]
}
'''

# TAIL is in other folder
folderStr = '20200914_SAN4_BOTTOM'
dateStr = '20200914'
gridShape = (14,6)

# Tail: 23, 35, 38, 39 (20200914_SAN4_BOTTOM)
smallDict = {
	'saveName': 'SAN4_tail', # will append _ch1/_ch2 to this
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [
				(5,1), (5,2),
				(6,1), (6,2)
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
