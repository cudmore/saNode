
"""
this is to analyze Ca++ transients in video

1) manually create roi(s) in Fiji
2) save with multi measure (this gives us Mean1, Mean2, ...) one mean per ROI per frame
3) run this to load multimeasure .csv and plot

I am using data from
	'/media/cudmore/data/20201111/tif1d_aligned.tif'
	'/media/cudmore/data/20201111/Results.csv'

The _aligned.tif is after caiman alignment but it does not seem to correct for stage/prep drift

"""

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import bReadROI

# these are manually selected rois on file tif1d_aligned.tif
#roiSetPath = '/media/cudmore/data/20201111/RoiSet.zip'
resultsPath = '/media/cudmore/data/20201111/Results.csv'

df = pd.read_csv(resultsPath)

#roiSetPath = '/media/cudmore/data/san-density/SAN4/tracing/RoiSet.zip'
#resultsPath = '/media/cudmore/data/san-density/SAN4/tracing/Results.csv'
#df = bReadROI.loadRoiZip(roiSetPath, resultsPath)

#print(df)

# there are 6 rois Mean1, Mean2, ...
numRoi = 8

# in this tif, the image is shifted at frame 400
# I tried correcting with Caiman and souite2p but it did not work (try Fiji MultiStackReg)
frames = [0, 400]
startFrame = frames[0]
stopFrame = frames[1]

for idx in range (numRoi):
	roiIdx = idx + 1
	meanKey = 'Mean' + str(roiIdx)
	mean1 = df[meanKey].tolist()

	mean1 = mean1[startFrame:stopFrame]

	# subtract the mean from the intensity trace
	theMean = np.nanmean(mean1)
	mean1 -= theMean

	# offset for plot
	offset = idx * 50
	mean1 += offset

	plt.plot(mean1)

#
plt.show()
