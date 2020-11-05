"""
make san2

take very large row X col grid from immuno
and make a single merged stack of a few stacks from head/mid/tail

Note:
	can run this from bimpy_env
"""

import aicsUtil2 # does not require bimpy

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#
gDataPath = '/media/cudmore/data/san-density'


# Head
# file numbers 34,35,38,39
'''
folderStr = '20200717'
dateStr = '20200717'
gridShape = (11,4)

smallDict = {
	'mainFolder': 'SAN1', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN1_head',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(8,1), (8,2),
					(9,1), (9,2)
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
'''


# Mid
# file numbers 11,12,13,14
'''
folderStr = '20200717'
dateStr = '20200717'
gridShape = (11,4)

smallDict = {
	'mainFolder': 'SAN1', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN1_mid',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(2,2), (2,3),
					(3,2), (3,3)
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
'''

# tail
# file numbers
folderStr = '20200720'
dateStr = '20200720'
gridShape = (8,6)

smallDict = {
	'mainFolder': 'SAN1', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN1_tail',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
