## Database

A summary database of SAN mosaics (off the fv300) is at

https://docs.google.com/spreadsheets/d/1hdYQya7l_i1I7T3XF2XnsGIFni4HsOQTna12DoIrWmg/edit#gid=0

## Plotting percent vascular volume

1) generate Density-Result-ch2.csv

```
python sanode/aicsMaskDen.py
```

2) Plot with Jupyter notebook

```
notebooks/manuscript-20201103.ipynb
```

## Plotting hcn4 dist to nearest vasculature

1) generate hcn4-Distance-Result.csv

```
python aicsMyocyteDistToVasc.py
```

2) plot with Jupyter notebook

```
notebooks/manuscript-20201103.ipynb
```

## Histograms/Violin plots of istance of each HCN4 pixel to nearest vasculature

hcn4Dist.csv is a comma separated file (csv) with columns

SAN: from ('SAN1', 'SAN2', 'SAN3', 'SAN4')
headMidTail: from ('head', 'mid', 'tail')
hcn4DistToVasc: Value of distance from one HCN4 pixel to closest vasculature (um)

1) Generate hcn4Dist.csv with

```
aicsPlot.plot_hcn4_dist_hist(pathList, doPlot=False, verbose=False)
```

2) Plot with Jupyter notebook

```
notebooks/hcn4Dist.ipynb
```
