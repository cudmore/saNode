"""
analyze all slab diameters

todo: add new heuristic to check start (5 pnts) and stop (5 points)

todo: add to aicsPlot.plotDiam() to explore the distribution of diameters

"""

import bimpy

if __name__ == '__main__':

	channelToAnalyze = 2 # channel 2 is vasculature

	pathList = []

	# SAN1
	pathList += [
				'/media/cudmore/data/san-density/SAN1/SAN1_head/aicsAnalysis/SAN1_head_ch2.tif',
				'/media/cudmore/data/san-density/SAN1/SAN1_mid/aicsAnalysis/SAN1_mid_ch2.tif',
				#'/media/cudmore/data/san-density/SAN1/SAN1_tail/aicsAnalysis/SAN1_tail_ch2.tif',
				]

	# SAN2
	pathList += [
				'/media/cudmore/data/san-density/SAN2/SAN2_head/aicsAnalysis/SAN2_head_ch2.tif',
				'/media/cudmore/data/san-density/SAN2/SAN2_mid/aicsAnalysis/SAN2_mid_ch2.tif',
				'/media/cudmore/data/san-density/SAN2/SAN2_tail/aicsAnalysis/SAN2_tail_ch2.tif',
				]

	# SAN3
	pathList += [
				'/media/cudmore/data/san-density/SAN3/SAN3_head/aicsAnalysis/SAN3_head_ch2.tif',
				'/media/cudmore/data/san-density/SAN3/SAN3_mid/aicsAnalysis/SAN3_mid_ch2.tif',
				'/media/cudmore/data/san-density/SAN3/SAN3_tail/aicsAnalysis/SAN3_tail_ch2.tif',
				]
	# SAN4
	pathList += [
				'/media/cudmore/data/san-density/SAN4/SAN4_head/aicsAnalysis/SAN4_head_ch2.tif',
				'/media/cudmore/data/san-density/SAN4/SAN4_mid/aicsAnalysis/SAN4_mid_ch2.tif',
				'/media/cudmore/data/san-density/SAN4/SAN4_tail/aicsAnalysis/SAN4_tail_ch2.tif',
				]

	for path in pathList:

		# tempted to put in os.path.isfile(path)
		# but would rather have this fail rather than continue

		# load stack
		myStack = bimpy.bStack(path=path, loadImages=True, loadTracing=True)

		# assume we have a skeleton for ch2 (vasculature)
		# we make it with aicsMakeSkel.py
		# this removes a number of noisy things from tracing

		# todo: add new heuristic comparing tails of line intensity profile
		# if they do not match then reject the fit
		# to do this, add code in gStackObject.myLineProfile.getLineProfile2

		# analyze all slab diameter in a cpu pool
		bimpy.analysis.b_mpAnalyzeSlabs.runDiameterPool(myStack, channelToAnalyze)

		myStack.slabList._preComputeAllMasks()

		myStack.slabList._analyze() # analyze all edges to get 'diam2' updated

		# save, next time we load, we do not need to (make skel, analyze diameter)
		myStack.saveAnnotations()
