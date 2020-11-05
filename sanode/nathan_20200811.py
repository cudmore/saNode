import aicsUtil2 # does not require bimpy

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#
gDataPath = '/home/cudmore/data/nathan'
folderStr = '20200811_SAN3_TOP'
dateStr = '20200811'
#gridShape = (7,5)
gridShape = (11,5)

smallDict = {
	'saveName': '0200811_SAN3_TOP_head', # will append _ch1/_ch2 to this
	'nRows': 3,
	'nCols': 3,
	'rowColIdxList': [(1,1), (1,2), (1,3),
				(2,1), (2,2), (2,3),
				(3,1), (3,2), (3,3),
				]
}
'''
smallDict = {
	'saveName': '0200811_SAN3_TOP_mid', # will append _ch1/_ch2 to this
	'nRows': 3,
	'nCols': 3,
	'rowColIdxList': [(6,0), (6,1), (6,2),
				(7,0), (7,1), (7,2),
				(8,0), (8,1), (8,2),
				]
}
'''

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
