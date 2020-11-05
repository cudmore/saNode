import myDaskNapari

myGridParams = myDaskNapari.getDaskGridDict()
myGridParams['path'] = '/Users/cudmore/box/data/nathan/20200518/analysis_full'
myGridParams['prefixStr'] = '20200518__A01_G001_'

#myGridParams['finalPostfixStr'] = 'raw'
myGridParams['finalPostfixList'] = ['raw', 'finalMask', 'finalMask_edt']
myGridParams['finalPostfixList'] = ['raw', 'finalMask_edt']

myGridParams['channelList'] = [1, 2]

# trimmed shape
myGridParams['commonShape'] = (64,474,474)

myGridParams['commonVoxelSize'] = (1, 0.621480865, 0.621480865)

# analysis is already trimmed
myGridParams['trimPercent'] = 0

myGridParams['trimPixels'] = None # calculated
myGridParams['nRow'] = 8
myGridParams['nCol'] = 6

#
# 20200717
# edt 007 is corrpupt, missing slices, got 10 but should be 88 ???
myGridParams = myDaskNapari.getDaskGridDict()
myGridParams['path'] = '/Volumes/ThreeRed/nathan/20200717/analysis_full'
myGridParams['prefixStr'] = '20200717__A01_G001_'

#myGridParams['finalPostfixStr'] = 'raw'
myGridParams['finalPostfixList'] = ['raw', 'finalMask', 'finalMask_edt']
myGridParams['finalPostfixList'] = ['raw', 'finalMask_edt']
myGridParams['finalPostfixList'] = ['raw', 'finalMask']

myGridParams['channelList'] = [1, 2]

# trimmed shape
myGridParams['commonShape'] = (88,740,740)

myGridParams['commonVoxelSize'] = (1, 0.3977476, 0.3977476)

# analysis is already trimmed
myGridParams['trimPercent'] = 0

myGridParams['trimPixels'] = None # calculated
myGridParams['nRow'] = 11
myGridParams['nCol'] = 4

myDaskNapari.openDaskNapari2(myGridParams)