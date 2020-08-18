from collections import OrderedDict

from aicsGridNapari import aicsGridNapari

# raw
masterFilePath = '' #'aicsBatch/20200720_cell_db.csv'
path = '/Users/cudmore/data/20200722'
prefixStr = '20200722__A01_G001_'
commonShape = (72,740,740) # if trimPercent then AFTER trimming
commonVoxelSize = (1, 0.3977476, 0.3977476)
channelList = [1,2]
gridShape = (10,6) # (11, 5)
finalPostfixList = [''] # '' is no postfix, e.g. raw tiff like _ch1.tif and _ch2.tif
trimPercent = 15 # aicsAnalysis is already trimmed
doUseInclude = False

aicsGridParam = OrderedDict()
aicsGridParam['masterFilePath'] = masterFilePath
aicsGridParam['path'] = path
aicsGridParam['prefixStr'] = prefixStr
aicsGridParam['commonShape'] =  commonShape# shape of each stack in aicsAnalysis (already trimmed)
aicsGridParam['commonVoxelSize'] = commonVoxelSize
aicsGridParam['channelList'] = channelList
aicsGridParam['gridShape'] = gridShape
aicsGridParam['finalPostfixList'] = finalPostfixList
aicsGridParam['trimPercent'] = trimPercent
aicsGridParam['doUseInclude'] = doUseInclude
#aicsGridParam['doUseInclude'] = doUseInclude
#aicsGridParam['doUseFirstLast'] = doUseFirstLast

aicsGridNapari(aicsGridParam)
