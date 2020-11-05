"""
make san3

take very large row X col grid from immuno
and make a single merged stack of a few stacks from head/mid/tail
"""

import aicsUtil2 # does not require bimpy

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#
gDataPath = '/media/cudmore/data/san-density' # moved to ssd drive


# Head
# file numbers 13,14,17,18
folderStr = '20200811_SAN3_TOP'
dateStr = '20200811'
gridShape = (11,5)

smallDict = {
	'mainFolder': 'SAN3', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN3_head',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(2,2), (2,3),
					(3,2), (3,3)
				]
}


aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)

# mid
# file numbers 39, 40, 41, 42
folderStr = '20200811_SAN3_TOP'
dateStr = '20200811'
gridShape = (11,5)
smallDict = {
	'mainFolder': 'SAN3', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN3_mid',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(7,1), (7,2),
					(8,1), (8,2)
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)



folderStr = '20200814_SAN3_BOTTOM'
dateStr = '20200814'
gridShape = (6,6)

# Tail: 2 (20200814_SAN3_BOTTOM)
# file numbers 2,3,10,11
smallDict = {
	#'saveName': '20200814_SAN3_BOTTOM_tail', # will append _ch1/_ch2 to this
	'mainFolder': 'SAN3', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN3_tail',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(0,1), (0,2),
				(1,1), (1,2),
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
