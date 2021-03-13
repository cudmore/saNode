"""
make san8

take very large row X col grid from immuno
and make a single merged stack of a few stacks from head/mid/tail
"""
import sys
import aicsUtil2 # does not require bimpy

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#
gDataPath = '/media/cudmore/data1/san-density' # moved to ssd drive


'''
# Head
# file numbers 10,11,14,15
folderStr = 'SAN8_head' # folder in san-density
dateStr = '20210106'
gridShape = (2,2)

smallDict = {
	'mainFolder': 'SAN8', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN8_head',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(0,0), (0,1),
					(1,0), (1,1)
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
'''

'''
# mid
# file numbers 57, 58, 63, 64
folderStr = 'SAN8_mid'
dateStr = '20210106'
gridShape = (2,2)

smallDict = {
	'mainFolder': 'SAN8', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN8_mid',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(0,0), (0,1),
					(1,0), (1,1)
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
'''

# tail
# file numbers 34, 35, 38, 39
folderStr = 'SAN8_tail'
dateStr = '20210106'
gridShape = (2,2)

smallDict = {
	'mainFolder': 'SAN8', # will create 2-folders SAN3/SAN3_tail/
	'saveName': 'SAN8_tail',
	'nRows': 2,
	'nCols': 2,
	'rowColIdxList': [(0,0), (0,1),
					(1,0), (1,1)
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
