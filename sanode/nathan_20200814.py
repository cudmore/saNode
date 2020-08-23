import aicsUtil2 # does not require bimpy

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#
folderStr = '20200814_SAN3_BOTTOM'
dateStr = '20200814'
gridShape = (6,6)

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape)