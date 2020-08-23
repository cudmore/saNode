import aicsUtil2 # does not require bimpy

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#
folderStr = '20200720'
dateStr = '20200720'
gridShape = (8,6)

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape)