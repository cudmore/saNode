"""
Set gDataPath to point to all the raw data

	cudmore home desktop is '/Users/cudmore/data'
	cudmore i9 linux is '/home/cudmore/data'
"""

#
# set this to the full path to your data folder
#
gDataPath = '/Users/cudmore/data'

import os

def getDataPath():
	if not os.path.isdir(gDataPath):
		print('ERROR: aicsDataPath.getDataPath() did not find gDataPath:', gDataPath)
		print('  please edit file aicsDataPath.py and set a proper gDataPath like "/Users/cudmore/data"')
		return None
	else:
		return gDataPath