"""
Run one or the other (vasc, cell) across an entire directory

See __main__ to set parameters like:

	dataDir = '/Volumes/ThreeRed/nathan'
	
	date = '20200717'
	# 1
	'''
	type = 'cell'
	channel = 1
	cpuCount -= 2
	'''
	# 2
	type = 'vasc'
	channel = 2
	cpuCount = cpuCount - 5

This make a lot of assumptions about file names, like
	20200717__A01_G001_*_ch1.tif
	
"""

import os, sys, glob
import multiprocessing as mp

from aicsVasc import vascDenRun
from aicsCell import cellDenRun

import bimpy

import aicsUtil

def aicsBatch(path, masterFilePath, type, channel, cpuCount=None):
	"""
	path: wildcard path like, /Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_*_ch1.tif
	"""
	print('=== aicsBatch()')
	print('  path:', path)
	print('  masterFilePath:', masterFilePath)
	print('  type:', type)
	print('  channel:', channel)
		
	
	if cpuCount is None:
		cpuCount = mp.cpu_count()
		print('cpuCount:', cpuCount)
		cpuCount -= 2

	print('  cpuCount:', cpuCount)

	myTimer = bimpy.util.bTimer('aicsBatch ' + type + ' ' + str(channel) + ' path:' + path)

	filenames = glob.glob(path)
	print('  proccessing', len(filenames), 'files')
	
	trimPercent = 15
	saveFolder = 'aicsAnalysis'
	
		
	'''
	if type == 'vasc':
		# vasc takes up to 7 GB per file, can only run a limited number of files in parallel based on memory
		# home computer has 32 GB
		cpuCount = 3 #aics code is taking up to > 7 GB per stack , can't run in parallel with only 32 GB !!!
	else:
		cpuCount -= 2
	'''
	pool = mp.Pool(processes=cpuCount)
		
	myTimer = bimpy.util.bTimer('aicsBatch ' + type + ' ' + str(channel))
	
	#
	# build async pool
	numFilesToAnalyze = 0
	results = []
	for filePath in filenames:
		# file is full file path
		
		uInclude, uFirstSlice, uLastSlice = aicsUtil.parseMasterFile(masterFilePath, filePath)
		
		if uInclude:
			# path, trimPercent=trimPercent, firstSlice=uFirstSlice, lastSlice=uLastSlice, saveFolder=saveFolder
			
			if type == 'vasc':
				args = [filePath, trimPercent, uFirstSlice, uLastSlice, saveFolder]
				oneResult = pool.apply_async(vascDenRun, args=args)
			elif type == 'cell':
				args = [filePath, trimPercent]
				oneResult = pool.apply_async(cellDenRun, args=args)
			
			if oneResult is not None:
				results.append(oneResult)

			numFilesToAnalyze += 1
			
	#
	# run
	paramList = []
	numResults = len(results)
	for idx, result in enumerate(results):
		print('=== running file', idx+1, 'of', numFilesToAnalyze)
		
		oneParamDict = None
		oneParamDict = result.get()
		
		if oneParamDict is not None:
			paramList.append(oneParamDict)
		
		print('  DONE with file idx:', idx+1, 'of', numResults)
		
	if paramList:
		# path to *this source file
		srcPath = os.path.dirname(os.path.abspath(__file__))

		tmpPath, tmpFile = os.path.split(masterFilePath)
		tmpFileNoExtension, tmpExt = tmpFile.split('.')
		analysisFile = tmpFileNoExtension + '_ch' + str(channel) + '_out.csv'
		saveAnalysisPath = os.path.join(srcPath, tmpPath, analysisFile)
		

		print('saving _out.csv:', saveAnalysisPath)
		bimpy.util.dictListToFile(paramList, saveAnalysisPath)
		
	print(myTimer.elapsed())
	
if __name__ == '__main__':

	'''
	masterFilePath = 'aicsBatch/20200717_cell_db.csv'
	path = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_*_ch1.tif'
	type = 'cell'
	channel = 1
	'''
	
	cpuCount = mp.cpu_count()

	dataDir = '/Volumes/ThreeRed/nathan'
	
	date = '20200717'
	# 1
	'''
	type = 'cell'
	channel = 1
	cpuCount -= 2
	'''
	# 2
	type = 'vasc'
	channel = 2
	#cpuCount = cpuCount - 5
	cpuCount = cpuCount - 5
	
	# leave this
	masterFilePath = 'aicsBatch/' + date + '_cell_db.csv'
	path = '/Volumes/ThreeRed/nathan' + '/' + date + '/' + date + '__A01_G001_*_ch' + str(channel) + '.tif'
	
	
	aicsBatch(path, masterFilePath, type, channel, cpuCount=cpuCount)
	
