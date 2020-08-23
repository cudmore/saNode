import aicsUtil2 # does not require bimpy
import aicsGridNapari # to display the grid in napari
import aicsDataPath
gDataPath = aicsDataPath.getDataPath()

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#

dateStr = '20200717'
gridShape = (11,4)

'''
dateStr = '20200720'
gridShape = (12,4)
gridShape = (8,6)
'''

'''
dateStr = '20200722'
gridShape = (10,6)
'''

'''
dateStr = '20200724'
gridShape = (7,5)
'''


#
# don't change this
#
aicsGridParam = aicsUtil2.mySetDefaultGridParams(gDataPath, dateStr, gridShape)
if aicsGridParam is None:
	pass
else:
	aicsGridNapari.aicsGridNapari(aicsGridParam)
