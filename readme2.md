## Workflow 20201101

1) take original (row x col) tiling and make a small (2,2) grid for each of
	san3
		head
		mid
		tail

```
python san3_makeGrid.py
```

2) make _labeled and _mask (using aics)

```
aicsCell.py
aicsVasc.py
```

Use batch for each of san3, san4, ...

Be sure to modify ...Batch.py with correct files for San3, San4, etc

aicsVasc.py takes 2-3 minutes per file

```
python aicsCellBatch.py
python aicsVascBatch.py
```

2.1) blank slices on top bottom of mask

In aicsBlankSlices.py, add a key to aicsBlankSlicesDict['SAN3Head']

Like this

```
# in aicsBlankSlices.py
aicsBlankSlicesDict['SAN3Head'] = {}
aicsBlankSlicesDict['SAN3Head']['top'] = 25 # the first good slice
aicsBlankSlicesDict['SAN3Head']['bottom'] = 43 # the last good slice
```
Use this to
	1) in bMakeDistanceMap.py, set upper/lower slices of edt to np.nan
	2) in bimpy/analysis/bMakeSkelFromMask.py,

2.2) Once we have a mask, we can always get voxel volume in mask

Use this to generate saNode/Density-Result-ch{channel}.csv

Be sure to specify list of files and channel in aicsMaskDen.py

One row per file in SAN 1/2/3/4, h/m/d
```
python aicsMaskDen.py
```

Will return a dict like

```
{
  "path": "/media/cudmore/data/san-density/SAN3/SAN3_tail/aicsAnalysis/SAN3_tail_ch1.tif",
  "maskShape": [
    77,
    948,
    948
  ],
  "xyzVoxel": [
    0.6214808646041788,
    0.6214808646041788,
    1
  ],
  "maskStart": 21,
  "maskStop": 31,
  "numGoodSlices": 11,
  "totalNumPixels": 9885744,
  "numPixelsInMask": 4538349,
  "maskRatio": 0.45908016634863297,
  "maskPercent": 45.908016634863294
}
```

3) make edt

When making edt we need to blank top/bottom bad slices

```
# was this
#python bimpy/analysis/bMakeDistanceMap.py
python aicsDistMap.py

# or
python aicsDistMapBatch.py
```

3.5 Calculate distance of each pixel in hcn4 mask (_ch1_mask.tif) using vasc edt (_ch2_edt.tif)

Use

```
# this creates/appends to sanNode/hcn4-Distance-Result.csv
python aicsMyocyteDistToVasc.py
```

4) plot
	(i) aicsPlot.plotMaskDensity(): cell or vasc mask percent (of volume)
	(ii) aicsPlot.plotMeanDist(): mean hcn4 distance to vasculature
	(iii) aicsPlot.plot_hcn4_dist_hist(): histogram of hcn4 distance to vasculature
	(iv) aicsPlot.plotSlabDiamHist(): histogram of slab diameter

```
python aicsPlot.py
```

5) make tracing in bImpy

need to specify first/last slice

be sure to set path in file aicsMakeSkel.py

```
python aicsMakeSkel.py
```

6) Get all the diameters (from skel) in accept first/last of mask

```
aicsAnalyzeSlabDiameter.py
```

7) pool all distances into one big hcn4Dist.csv

This subsamples a random 1e6 slab diameters

```
# see: aicsPlot.plot_hcn4_dist_hist(pathList, doPlot=False, verbose=False)
# and see
notebooks/hcn4Dist.ipynb
```

8) Analyze length of tracing (202101)

The following outputs 2x files (pooled across all head/mid/tail san 1-4, 7, 8)

Like this:
	dfNodesOut.to_csv('nodes_db_20210125.csv')
	dfEdgesOut.to_csv('edges_db.20210125.csv')

```
bimpy/analysis/bScrapeEdgesAndNodes.py
```

- I need (CONVERT LEN 2d/3d TO UM) then sum the length in each stack and then divide by volume.
- Where volume is actually our top/bottom from aicsBlankSlices
- Double check that bimpy tracing 'len 2d' and 'len 3d' are in um
	IT IS NOT
	NEITHER is diam2
	BOTH ARE SET IN bVascularTracing._analyze()

	make len and diam in um and go all the way back to
		aicsAnalyzeSlabDiameter
- Expand bScrapeEdgesAndNode to also make a short (per san-region table of TOTAL LENGTH, TOTAL VOLUME, LENGTH/VOLUME
	)
9)

todo:
0) add heuristic to reject slab that have their tails (start/stop of line) at different intensities
1) calculate diameter of each slab in entire tracing
2) plot these diameters as a histogram

20210111
1) calculate vessel length hist (and mean/median/std/sem)
2) calculate total vessel length

# Old

## aics analysis

aicsVasc

aicsCell

aicsBatch.py, run aicsVasc or aicsCell and save _out.csv with parameters used

### View in Napari

aicsDaskNapari.py

aicsOneNapari.py

### Post

aicsInterSelectSlice.py, A browser to show all stacks in grid and select first/last slice

aicsInterEditNapari.py, Use napari to manually remove large vessels from mask.

## To Do

### First

- select first/last slice
- remove from labeled
- calculate convex hull (per slice)

- vasc edt
- grab vasc edt for pixels in cell mask

### Then

- mask percent as function of per slice convex hull
