"""
make san4

take very large row X col grid from immuno
and make a single merged stack of a few stacks from head/mid/tail
"""

import aicsUtil2 # does not require bimpy

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#
gDataPath = '/media/cudmore/data/san-density' # moved to ssd drive


# Head
# file numbers 10,11,14,15
folderStr = '20200901_SAN4_TOP'
dateStr = '20200901'
gridShape = (12,6)

smallDict = {
	'mainFolder': 'SAN4', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN4_head',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(1,1), (1,2),
					(2,1), (2,2)
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)



# mid
# file numbers 57, 58, 63, 64
folderStr = '20200901_SAN4_TOP'
dateStr = '20200901'
gridShape = (12,6)

smallDict = {
	'mainFolder': 'SAN4', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN4_mid',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(9,2), (9,3),
					(10,2), (10,3),
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)



# tail
# file numbers 34, 35, 38, 39
folderStr = '20200914_SAN4_BOTTOM'
dateStr = '20200914'
gridShape = (14,6)

smallDict = {
	'mainFolder': 'SAN4', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN4_tail',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(5,1), (5,2),
					(6,1), (6,2)
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
