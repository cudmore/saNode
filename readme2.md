## Workflow 20201101

1) take original (rwo x col) tiling and make a small (2,2) grid for each of
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

Be sure to modify ...Batch.py with correct files for San3, San4

aicsVasc.py takes 2-3 minutes per file

```
python aicsCellBatch.py
python aicsVascBatch.py
```

3) make edt

```
# was this
#python bimpy/analysis/bMakeDistanceMap.py
python aicsDistMap.py

# or
python aicsDistMapBatch.py
```

4) make tracing in bImpy

need to specify first/last slice
```
python bimpy/analysis/xxx
```


## aics analysis

aicsVasc

aicsCell

aicsBatch.py, run aicsVasc or aicsCell and save _out.csv with parameters used

### View in Napari

aicsDaskNapari.py

aicsOneNapari.py

### Post

aicsInterSelectSlice.py, for each stack, select first/last slice

aicsInterEditNapari.py

## To Do

### First

- select first/last slice
- remove from labeled
- calculate convex hull (per slice)

- vasc edt
- grab vasc edt for pixels in cell mask

### Then

- mask percent as function of per slice convex hull
