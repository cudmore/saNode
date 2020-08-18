from collections import OrderedDict

from aicsGridNapari import aicsGridNapari

masterFilePath = 'aicsBatch/20200717_cell_db.csv'
path = '/Volumes/ThreeRed/nathan/20200717/aicsAnalysis0'
path = '/Users/cudmore/Desktop/aicsAnalysis0'
prefixStr = '20200717__A01_G001_'
commonShape = (88,740,740)
commonVoxelSize = (1, 0.3977476, 0.3977476)
channelList = [1,2]
gridShape = (11,4)
finalPostfixList = ['', '_mask', '_labeled']
#doUseInclude = True
#doUseFirstLast = True

# raw data ... WILL NOT BE TRIMMED BY OVERLAP
'''
masterFilePath = ''
path = '/Volumes/ThreeRed/nathan/20200717'
commonShape = (88,800,800)
commonVoxelSize = (1, 0.3977476, 0.3977476)
channelList = [1,2]
gridShape = (11,4)
finalPostfixList = [''] # '' is no postfix, e.g. raw tiff like _ch1.tif and _ch2.tif
'''

aicsGridParam = OrderedDict()
aicsGridParam['masterFilePath'] = masterFilePath
aicsGridParam['path'] = path
aicsGridParam['prefixStr'] = prefixStr
aicsGridParam['commonShape'] =  commonShape# shape of each stack in aicsAnalysis (already trimmed)
aicsGridParam['commonVoxelSize'] = commonVoxelSize
aicsGridParam['channelList'] = channelList
aicsGridParam['gridShape'] = gridShape
aicsGridParam['finalPostfixList'] = finalPostfixList
#aicsGridParam['doUseInclude'] = doUseInclude
#aicsGridParam['doUseFirstLast'] = doUseFirstLast

aicsGridNapari(aicsGridParam)
