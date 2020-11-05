"""
create a skeleton using bimpy and save in a .h5f file

only create skeletons fom vasculr channel 2
"""

import os

import bimpy

import aicsBlankSlices

if __name__ == '__main__':

	# do one
	if 0:
		path = '/media/cudmore/data/san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch2.tif'

		(maskStart, maskStop) = aicsBlankSlices.getTopBottom(path)
		maskStartStop = (maskStart, maskStop)

		okGo = True
		if maskStart is None or maskStop is None:
			print('  ERROR: aicsMakeSkel got None maskStart/maskStop for path:', path)
			okGo = False

		if okGo:
			channelToAnalyze = 2 # only make this for vascular channel
			bimpy.analysis.bMakeSkelFromMask(path, channelToAnalyze, maskStartStop)

	# do batch
	if 1:
		channel = 2
		pathList = []

		# san1
		sanNumber = 1
		pathList += aicsBlankSlices.getCondList(sanNumber, channel)
		# san2
		sanNumber = 2
		pathList += aicsBlankSlices.getCondList(sanNumber, channel)
		# san3
		sanNumber = 3
		pathList += aicsBlankSlices.getCondList(sanNumber, channel)
		# san4
		sanNumber = 4
		pathList += aicsBlankSlices.getCondList(sanNumber, channel)

		for idx, path in enumerate(pathList):
			print(f'\n{idx+1} of {len(pathList)} aicsMakeSkel.__main__()')

			(maskStart, maskStop) = aicsBlankSlices.getTopBottom(path)
			maskStartStop = (maskStart, maskStop)

			okGo = True
			if maskStart is None or maskStop is None:
				print('\n  ERROR: aicsMakeSkel got None maskStart/maskStop for path:', path)
				print('    -->> skipping')
				okGo = False

			if okGo:
				channelToAnalyze = 2 # only make this for vascular channel
				bimpy.analysis.bMakeSkelFromMask(path, channelToAnalyze, maskStartStop)
