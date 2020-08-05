"""
20200803 plot distribution of label sizes

trying to figure out how to safely exclude small labels
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter

import numpy as np

#labelIndices = np.load('/Users/cudmore/Desktop/labelIndices.npy')

# labelCounts is a list of label sizes (area per label)
#labelCounts = np.load('/Users/cudmore/Desktop/labelCount.npy')
labelCounts = np.load('/Users/cudmore/Desktop/20200717__A01_G001_0014_ch2_labelSizeList.npy')

#print(labelIndices)

# remove the first two labels, they are huge (obscure other values, even in log plots)
#print(np.max(labelCounts))
labelCounts = labelCounts[2:]
#print(np.max(labelCounts))

print(labelCounts)

numLabels = len(labelCounts)
xAxis = range(numLabels)

print('numLabels:', numLabels)

fig, axs = plt.subplots(1, 3)

axs[0].plot(xAxis, labelCounts)
axs[0].set_yscale('log')
axs[0].set_xlabel('Marker Numbers')
axs[0].set_ylabel('Pixel Area')

nBins = 250
binWidth = numLabels / nBins

print('nBins:', nBins)
print('binWidth:', binWidth)

axs[1].hist(labelCounts, log=True, bins=nBins)
axs[1].set_xlabel('Pixel Area')
axs[1].set_ylabel('# Labels')

'''
axs[2].plot(labelIndices)
axs[2].set_xlabel('Label Index')
axs[2].set_ylabel('Count')
'''

plt.show()
