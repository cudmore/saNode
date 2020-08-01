"""
Run vascDen and/or cellDen on all raw _ch1 or _ch2 files

Usage:
	python crossChannelFolder.py <channel>, <type>, <folder>
	
	Something like
        python denAnalysisFolder.py 1 cellDen 15 /Users/cudmore/box/data/nathan/20200518
        python denAnalysisFolder.py 2 vascDen 15 /Users/cudmore/box/data/nathan/20200518
	
"""
import os, argparse, time

from cellDen import myRun as cellDenRun
from vascDen import myRun as vasDenRun

import multiprocessing as mp

def densityFolder(path, channel, analysisType, trimPercent):
	"""
	path: path to original _ch1/_ch2 .tif files (not analysis2)
	channel: (1,2)
	analysisType: (cellDen, vascDen)
	"""
	
	startTime = time.time()

	if channel == 1:
		chStr = '_ch1'
	elif channel == 2:
		chStr = '_ch2'

	#masterFilePath = 'master_cell_db.csv'
	masterFilePath = '20200518_cell_db.csv'
	
	filePathList = []
	for file in os.listdir(path):
		if file.startswith('.'):
			continue
		if not file.endswith('.tif'):
			continue
		
		fileNameExtension, fileExtension = file.split('.')
		if not fileNameExtension.endswith(chStr):
			continue
		filePath = os.path.join(path, file)
	
		'''
		baseFile = file
		baseFile = baseFile.replace('_ch1.tif', '')
		baseFile = baseFile.replace('_ch2.tif', '')
		baseFile = baseFile.replace('_ch3.tif', '')
		print(baseFile)
		'''

		filePathList.append(filePath)
	
	numFiles = len(filePathList)

	
	# run in series
	'''
	for idx, filePath in enumerate(filePathList):
		print('\n====== file', idx+1, 'of', numFiles, 'path:', filePath)
		if analysisType == 'cellDen':
			cellDenRun(filePath, trimPercent, masterFilePath)
		elif analysisType == 'vascDen':
			vasDenRun(filePath, trimPercent, masterFilePath)
	'''
	
	#
	# parallel
	cpuCount = mp.cpu_count()
	cpuCount -= 2
	pool = mp.Pool(processes=cpuCount)
	pResults = []

	for idx, filePath in enumerate(filePathList):
		if analysisType == 'vascDen':
			args = [filePath, trimPercent, masterFilePath]
			oneAnswer = pool.apply_async(vasDenRun, args=args)
			pResults.append(oneAnswer)
		elif analysisType == 'cellDen':
			args = [filePath, trimPercent, masterFilePath]
			oneAnswer = pool.apply_async(cellDenRun, args=args)
			pResults.append(oneAnswer)

	# run in parallel
	for pResult in pResults:
		oneResult = pResult.get()
		#if tiffFileInfo is not None:
		#	fileDictList.append(tiffFileInfo)

	stopTime = time.time()
	print('finished in', round(stopTime-startTime,2), 'seconds')
		
################################################################################
if __name__ == '__main__':
	#
	# read master_cell_db.csv (same folder as this file, for now)
	masterFilePath = 'master_cell_db.csv'
	masterFilePath = '20200518_cell_db.csv'

	masterFilePath = '20200717_cell_db.csv'

	#dfMasterCellDB = pd.read_csv('master_cell_db.csv')
	
	parser = argparse.ArgumentParser(description = 'Process a vascular stack')
	parser.add_argument('channel', nargs=1, default='', help='channel 1 or 2')
	parser.add_argument('analysisType', nargs=1, default='', help='either "cellDen" or "vascDen"')
	parser.add_argument('trimPercent', nargs=1, default='15', help='Percent overlap in tiling')
	parser.add_argument('analysisPath', nargs=1, default='', help='path to original .tif file')
	args = parser.parse_args() # args is a list of command line arguments

	print('args.channel:', args.channel)
	print('args.analysisType:', args.analysisType)
	print('args.analysisPath:', args.analysisPath)
	
	if len(args.channel)>0:
		channel = int(args.channel[0])	
	if len(args.analysisType)>0:
		analysisType = args.analysisType[0]		
	if len(args.trimPercent)>0:
		trimPercent = int(args.trimPercent[0])	
	if len(args.analysisPath)>0:
		path = args.analysisPath[0]		

	# HARD CODED
	trimPercent = 15
	
	print('crossChannelFolder channe:', channel, 'analysisType:', analysisType, 'path:', path)
	densityFolder(path, channel, analysisType, trimPercent)
