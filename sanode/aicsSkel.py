"""

taken from bimpy.bVascularTracing.loadDeepVess()

THIS DOES NOT WORK  !!!!

"""

import os

import numpy as np

from skimage import morphology
from scipy.sparse import csgraph # to get dijoint segments

import tifffile

# see: https://github.com/jni/skan
# pip install skan
import skan 

def _defaultNodeDict(x=None, y=None, z=None, nodeIdx=None, slabIdx=None):
	nodeDict = OrderedDict({
		#'idx': nodeIdx, # index into self.nodeDictList
		#'slabIdx': slabIdx, # index into self.x/self.y etc
		'idx': None,
		'nEdges': 0,
		'type': '',
		'isBad': False,
		'note': '',
		'x': round(x,2),
		'y': round(y,2),
		'z': round(z,2),
		#'zSlice': None, #todo remember this when I convert to um/pixel !!!
		'skelID': None, # used by deepves
		'slabIdx': slabIdx,
		'edgeList': [],
	})
	return nodeDict

def _appendSlab(x, y, z, d=np.nan, edgeIdx=np.nan, nodeIdx=np.nan):
	newSlabIdx = self.numSlabs()
	self.x = np.append(self.x, x)
	self.y = np.append(self.y, y)
	self.z = np.append(self.z, z)
	self.d = np.append(self.d, d)
	self.d2 = np.append(self.d2, np.nan) # will be filled in by bLineIntensity profile
	self.int = np.append(self.int, np.nan)
	self.edgeIdx = np.append(self.edgeIdx, edgeIdx)
	self.nodeIdx = np.append(self.nodeIdx, nodeIdx)
	#self.slabIdx = np.append(self.slabIdx, newSlabIdx)
	return newSlabIdx

def aicsMakeSkel(path, uFirstSlice=None, uLastSlice=None):

	stackData = tifffile.imread(path)

	basePath, ext = os.path.splitext(path)
	maskPath = basePath + '_mask.tif'

	maskData = tifffile.imread(maskPath)
	
	if uFirstSlice is not None and uLastSlice is not None:
		print('aicsMakeSkel() pruning slices:', uFirstSlice, uLastSlice)
		maskData[0:uFirstSlice-1,:,:] = 0
		maskData[uLastSlice:-1,:,:] = 0
		
	print('  morphology.skeletonize_3d')
	mySkeleton = morphology.skeletonize_3d(maskData)

	#
	# convert raw skeleton into a proper graph with nodes/edges
	#skanSkel = skan.Skeleton(mySkeleton, source_image=stackData.astype('float'))
	print('  skan.Skeleton (slow)')
	skanSkel = skan.Skeleton(mySkeleton, source_image=stackData)

	branch_data = skan.summarize(skanSkel) # branch_data is a pandas dataframe
	print('    branch_data.shape:', branch_data.shape)
	print(branch_data.head())

	# make a list of coordinate[i] that are segment endpoints_src
	nCoordinates = skanSkel.coordinates.shape[0]
	slabs = skanSkel.coordinates.copy() #np.full((nCoordinates,3), np.nan)
	nodes = np.full((nCoordinates), np.nan)
	nodeEdgeList = [[] for tmp in range(nCoordinates)]
	edges = np.full((nCoordinates), np.nan)

	_, skeleton_ids = csgraph.connected_components(skanSkel.graph, directed=False)

	path_lengths = skanSkel.path_lengths()
	path_means = skanSkel.path_means() # does not return intensity of image, always 1 (e.g. the mask?)

	# these were in self.
	
	#
	masterNodeIdx = 0
	masterEdgeIdx = 0
	nPath = len(skanSkel.paths_list())
	print('    parsing nPath:', nPath, '...')
	for edgeIdx, path in enumerate(skanSkel.paths_list()):
		# edgeIdx: int

		# skip paths made of just two nodes
		if len(path)<=2:
			#print('skipping edgeIdx:', edgeIdx)
			continue

		# remember to remove
		#if int(float(skeleton_ids[edgeIdx])) == 2:
		#	continue

		srcPnt = path[0]
		dstPnt = path[-1]

		z = float(skanSkel.coordinates[srcPnt,0]) # deepvess uses (slice, x, y)
		x = float(skanSkel.coordinates[srcPnt,1])
		y = float(skanSkel.coordinates[srcPnt,2])
		diam = 5 # todo: add this to _analysis

		if nodes[srcPnt] >= 0:
			srcNodeIdx = int(float(nodes[srcPnt]))
			self.nodeDictList[srcNodeIdx]['edgeList'].append(masterEdgeIdx)
			self.nodeDictList[srcNodeIdx]['nEdges'] = len(self.nodeDictList[srcNodeIdx]['edgeList'])
			'''
			print('=== srcPnt appended to node', srcNodeIdx, 'edge list:',masterEdgeIdx)
			print('    ', self.nodeDictList[srcNodeIdx])
			'''
		else:
			# new node
			srcNodeIdx = masterNodeIdx
			masterNodeIdx += 1
			#
			nodes[srcPnt] = srcNodeIdx
			#
			nodeDict = self._defaultNodeDict(x=x, y=y, z=z, nodeIdx=srcNodeIdx)
			nodeDict['idx'] = srcNodeIdx
			nodeDict['edgeList'].append(masterEdgeIdx)
			nodeDict['nEdges'] = 1
			nodeDict['skelID'] = int(float(skeleton_ids[edgeIdx]))
			self.nodeDictList.append(nodeDict)
			# always append slab
			self._appendSlab(x, y, z, d=diam, edgeIdx=np.nan, nodeIdx=srcNodeIdx)

		z = float(skanSkel.coordinates[dstPnt,0]) # deepvess uses (slice, x, y)
		x = float(skanSkel.coordinates[dstPnt,1])
		y = float(skanSkel.coordinates[dstPnt,2])
		diam = 5 # todo: add this to _analysis
		if nodes[dstPnt] >= 0:
			dstNodeIdx = int(float(nodes[dstPnt]))
			self.nodeDictList[dstNodeIdx]['edgeList'].append(masterEdgeIdx)
			self.nodeDictList[dstNodeIdx]['nEdges'] = len(self.nodeDictList[dstNodeIdx]['edgeList'])
			'''
			print('=== dstPnt appended to node', dstNodeIdx, 'edge list:',masterEdgeIdx)
			print('    ', self.nodeDictList[dstNodeIdx])
			'''
		else:
			# new node
			dstNodeIdx = masterNodeIdx
			masterNodeIdx += 1
			#
			nodes[dstPnt] = dstNodeIdx
			#
			nodeDict = self._defaultNodeDict(x=x, y=y, z=z, nodeIdx=dstNodeIdx)
			nodeDict['idx'] = dstNodeIdx
			nodeDict['edgeList'].append(masterEdgeIdx)
			nodeDict['nEdges'] = 1
			nodeDict['skelID'] = int(float(skeleton_ids[edgeIdx]))
			self.nodeDictList.append(nodeDict)
			# always append slab
			self._appendSlab(x, y, z, d=diam, edgeIdx=np.nan, nodeIdx=dstNodeIdx)

		#print('path_lengths[] edgeIdx:', edgeIdx, path_lengths[edgeIdx], 'skeleton_ids:', skeleton_ids[edgeIdx], 'len(path):', len(path), 'path_means:', path_means[edgeIdx])
		newZList = []
		#if len(path)>2:
		if 1:
			for idx2 in path[1:-2]:
				#edges[idx2] = idx
				zEdge = float(skanSkel.coordinates[idx2,0]) # deepvess uses (slice, x, y)
				xEdge = float(skanSkel.coordinates[idx2,1])
				yEdge = float(skanSkel.coordinates[idx2,2])
				newZList.append(zEdge)
				diam = 3
				newSlabIdx = self._appendSlab(xEdge, yEdge, zEdge, d=diam, edgeIdx=masterEdgeIdx, nodeIdx=np.nan)

			# always append an edge
			edgeDict = self._defaultEdgeDict(edgeIdx=masterEdgeIdx, srcNode=srcNodeIdx, dstNode=dstNodeIdx)
			masterEdgeIdx += 1
			if len(newZList) > 0:
				edgeDict['z'] = int(round(statistics.median(newZList)))
			self.edgeDictList.append(edgeDict)

		else:
			pass # this happens a lot ???
			#print('    warning: got len(path)<=2 at edgeIdx:',edgeIdx)

	self._analyze()

	print('    done loadDeepVess()')
	return True
	
if __name__ == '__main__':

	path = '/Users/cudmore/data/20200717/aicsAnalysis/20200717__A01_G001_0014_ch2.tif'
	uFirstSlice = 44
	uLastSlice = 64
	
	aicsMakeSkel(path, uFirstSlice, uLastSlice)