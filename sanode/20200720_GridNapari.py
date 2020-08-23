from collections import OrderedDict

from aicsGridNapari import aicsGridNapari

masterFilePath = 'aicsBatch/20200720_cell_db.csv'
path = '/Users/cudmore/data/20200720/aicsAnalysis'
prefixStr = '20200720__A01_G001_'
commonShape = (96,740,740)
commonVoxelSize = (1, 0.3977476, 0.3977476)
channelList = [1,2]
gridShape = (12,4)
trimPercent = 0 # aicsAnalysis is already trimmed
finalPostfixList = ['', '_mask', '_labeled']
finalPostfixList = ['', '_mask']
doUseInclude = True
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

# aicsAnalysis
masterFilePath = '' #'aicsBatch/20200720_cell_db.csv'
path = '/Users/cudmore/data/20200720/aicsAnalysis'
commonShape = (96,740,740)
commonVoxelSize = (1, 0.3977476, 0.3977476)
channelList = [1,2]
gridShape = (12,4)
finalPostfixList = [''] # '' is no postfix, e.g. raw tiff like _ch1.tif and _ch2.tif
doUseInclude = False

# raw
masterFilePath = '' #'aicsBatch/20200720_cell_db.csv'
path = '/Users/cudmore/data/20200720'
commonShape = (96,740,740) # if trimPercent then AFTER trimming
commonVoxelSize = (1, 0.3977476, 0.3977476)
channelList = [1,2]
gridShape = (12,4)
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
