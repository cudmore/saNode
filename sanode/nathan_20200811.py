import aicsUtil2 # does not require bimpy

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#
folderStr = '20200811_SAN3_TOP'
dateStr = '20200811'
gridShape = (7,5)

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape)