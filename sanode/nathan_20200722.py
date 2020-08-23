import aicsUtil2 # does not require bimpy

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#
folderStr = '20200722'
dateStr = '20200722'
gridShape = (10,6)

aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape)