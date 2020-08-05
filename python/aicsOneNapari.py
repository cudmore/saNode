import os, sys, time, glob, logging

import numpy as np

import napari

import bimpy

def aicsOneNapari(path):
	"""
	path: path to vasc raw stack
		e.g.: /Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0014_ch2.tif
		
	path to analysisAics/ folder'
	"""
	
	print('oneNapari() path:', path)
	
	rawPath, rawFile = os.path.split(path)
	rawFileNoExtension, tmpExtension = rawFile.split('.')
	
	analysisFolder = os.path.join(rawPath, 'analysisAics')
	
	rawAnalysisPath = os.path.join(analysisFolder,rawFile)
	print(rawAnalysisPath)
	
	maskFile = rawFileNoExtension + '_mask.tif'
	maskAnalysisPath = os.path.join(analysisFolder,maskFile)
	print(maskAnalysisPath)
	
	labeledFile = rawFileNoExtension + '_labeled.tif'
	labeledFilePath = os.path.join(analysisFolder,labeledFile)
	print(labeledFilePath)
	
	labeledRemovedFile = rawFileNoExtension + '_labeled_removed.tif'
	labeledRemovedPath = os.path.join(analysisFolder,labeledRemovedFile)
	print(labeledRemovedPath)
	
	#
	# load
	rawData, tiffHeader = bimpy.util.bTiffFile.imread(rawAnalysisPath)
	maskData, tmp = bimpy.util.bTiffFile.imread(maskAnalysisPath)
	labeledData, tmp = bimpy.util.bTiffFile.imread(labeledFilePath)
	labeledRemovedData, tmp = bimpy.util.bTiffFile.imread(labeledRemovedPath)
	
	xVoxel = tiffHeader['xVoxel']
	yVoxel = tiffHeader['yVoxel']
	zVoxel = tiffHeader['zVoxel']
	
	#
	# get label and count for final labels (which then make mask)
	# visually inspect results and see if we need to increase 'removeSmallLabels'
	uniqueOrig, countsOrig = np.unique(labeledData, return_counts=True)
	origNumLabels = len(uniqueOrig)
	myPrettyPrint = np.asarray((uniqueOrig, countsOrig)).T
	print(myPrettyPrint)

	scale = (zVoxel, xVoxel, yVoxel)
	with napari.gui_qt():
		titleStr = 'aicsOneNapari:' + path
		viewer = napari.Viewer(title=titleStr)
	
		blending = 'additive'
		opacity = 1.0
		
		minContrast = 0
		maxContrast = 180
		myImageLayer = viewer.add_image(rawData, scale=scale, contrast_limits=(minContrast, maxContrast),
							blending=blending, opacity=opacity, colormap='green', visible=True, name='_ch2')
	
		minContrast = 0
		maxContrast = 1
		myImageLayer = viewer.add_image(maskData, scale=scale, contrast_limits=(minContrast, maxContrast),
							blending=blending, opacity=opacity, colormap='blue', visible=True, name='_mask')
	
		myImageLayer = viewer.add_labels(labeledData, scale=scale,
							blending=blending, opacity=opacity, visible=True, name='_labeled')

		myImageLayer = viewer.add_labels(labeledRemovedData, scale=scale,
							blending=blending, opacity=opacity, visible=True, name='_removed')

if __name__ == '__main__':
	path = '/Volumes/ThreeRed/nathan/20200717/20200717__A01_G001_0014_ch2.tif'
	
	aicsOneNapari(path)