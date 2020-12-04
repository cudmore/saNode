"""
Try getting suite2p to detect Ca++ in (i) video and then (ii) 2p movies

After that, use FISSA

https://github.com/rochefort-lab/fissa

"""

import os
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

# FISSA toolbox
#import fissa

# suite2p toolbox
import suite2p

def runAlignment(myPath, savePath, fs):
	print('runAlignment()')
	save_path0 = savePath

	# Set your options for running
	ops = suite2p.default_ops()  # populates ops with the default options

	# Provide an h5 path in 'h5py' or a tiff path in 'data_path'
	# db overwrites any ops (allows for experiment specific settings)
	db = {
	    'h5py': [],  # a single h5 file path
	    'h5py_key': 'data',
	    'look_one_level_down': False,  # whether to look in ALL subfolders when searching for tiffs
	    'data_path': [myPath],  # a list of folders with tiffs
	    #'data_path': ['exampleData/20150529'],  # a list of folders with tiffs
	                                            # (or folder of folders with tiffs if look_one_level_down is True,
	                                            # or subfolders is not empty)
	    'save_path0': save_path0,  # save path
	    'subfolders': [],  # choose subfolders of 'data_path' to look in (optional)
	    'fast_disk': './',  # string which specifies where the binary file will be stored (should be an SSD)
	    'reg_tif': True,  # save the motion corrected tiffs
	    'tau': 0.7,  # timescale of gcamp6f
	    'fs': mySamplingRate,  # sampling rate
	    'spatial_scale': 0
	}

	# Run one experiment
	opsEnd = suite2p.run_s2p(ops=ops, db=db)

def loadResults(myPath):
	print('loadResults() myPath:', myPath)
	savePath = 'suite2p/plane0'
	output_op_file = np.load(os.path.join(myPath, savePath, 'ops.npy'), allow_pickle=True).item()
	#output_op_file.keys() == output_op.keys()
	#print(output_op_file)
	return output_op_file

def plotRegistrationResults(output_op):
	# plot
	plt.subplot(1, 4, 1)
	plt.imshow(output_op['refImg'], cmap='gray', )
	plt.title("Reference Image for Registration");

	plt.subplot(1, 4, 2)
	plt.imshow(output_op['max_proj'], cmap='gray')
	plt.title("Registered Image, Max Projection");

	plt.subplot(1, 4, 3)
	plt.imshow(output_op['meanImg'], cmap='gray')
	plt.title("Mean registered image")

	plt.subplot(1, 4, 4)
	plt.imshow(output_op['meanImgE'], cmap='gray')
	plt.title("High-pass filtered Mean registered image");

	plt.show()

def detect(output_op):
	stats_file = Path(output_op['save_path']).joinpath('stat.npy')
	iscell = np.load(Path(output_op['save_path']).joinpath('iscell.npy'), allow_pickle=True)[:, 0].astype(bool)
	stats = np.load(stats_file, allow_pickle=True)
	stats.shape, iscell.shape

	return stats, iscell

def plotDetection(output_op, stats, iscell):
	im = suite2p.ROI.stats_dicts_to_3d_array(stats, Ly=output_op['Ly'], Lx=output_op['Lx'], label_id=True)
	im[im == 0] = np.nan

	plt.subplot(1, 4, 1)
	plt.imshow(output_op['max_proj'], cmap='gray')
	plt.title("Registered Image, Max Projection")

	plt.subplot(1, 4, 2)
	plt.imshow(np.nanmax(im, axis=0), cmap='jet')
	plt.title("All ROIs Found")

	plt.subplot(1, 4, 3)
	plt.imshow(np.nanmax(im[~iscell], axis=0, ), cmap='jet')
	plt.title("All Non-Cell ROIs")

	plt.subplot(1, 4, 4)
	plt.imshow(np.nanmax(im[iscell], axis=0), cmap='jet')
	plt.title("All Cell ROIs");

	plt.show()

if __name__ == '__main__':
	myPath = '/media/cudmore/data/20201111/tif1d'
	savePath = '/media/cudmore/data/20201111/tif1d_analysis'
	mySamplingRate = .02 # never sure on this, video is at 18 fps

	# slow
	runAlignment(myPath, savePath, mySamplingRate)
	#sys.exit()

	output_op = loadResults(savePath)
	print('  data_path:', output_op['data_path'])
	print('  save_path:', output_op['save_path'])

	stats, iscell = detect(output_op)

	plotDetection(output_op, stats, iscell)
