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
folderStr = '20201202_SAN7/Superior'
dateStr = '20201202'
gridShape = (16,5)

smallDict = {
	'mainFolder': 'SAN7', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN7_head',
	'nRows': 0,
	'nCols': 0,
	'rowColIdxList': [
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
