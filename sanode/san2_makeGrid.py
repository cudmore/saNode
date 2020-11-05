"""
make san2

take very large row X col grid from immuno
and make a single merged stack of a few stacks from head/mid/tail
"""

import aicsUtil2 # does not require bimpy

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#
gDataPath = '/media/cudmore/data/san-density'


# Head
# file numbers 45,46,51,52
'''
folderStr = '20200722'
dateStr = '20200722'
gridShape = (10,6)

smallDict = {
	'mainFolder': 'SAN2', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN2_head',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(7,2), (7,3),
					(8,2), (8,3)
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
'''

# Mid
# file numbers 3,4,9,10
'''
folderStr = '20200722'
dateStr = '20200722'
gridShape = (10,6)

smallDict = {
	'mainFolder': 'SAN2', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN2_mid',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(0,2), (0,3),
					(1,2), (1,3)
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
'''

# tail
# file numbers 11,12,19,20
folderStr = '20200724'
dateStr = '20200724'
gridShape = (7,5)

smallDict = {
	'mainFolder': 'SAN2', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN2_tail',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(2,0), (2,1),
					(3,0), (3,1)
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
