import aicsUtil2 # does not require bimpy

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#
gDataPath = '/home/cudmore/data/nathan'
folderStr = '20200814_SAN3_BOTTOM'
dateStr = '20200814'
gridShape = (6,6)

# Tail: 2 (20200814_SAN3_BOTTOM)
smallDict = {
	'saveName': '20200814_SAN3_BOTTOM_tail', # will append _ch1/_ch2 to this
	'nRows': 2,
	'nCols': 3,
	'rowColIdxList': [(0,0), (0,1), (0,2),
				(1,0), (1,1), (1,2),
				]
}

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape, gDataPath=gDataPath, smallDict=smallDict)
