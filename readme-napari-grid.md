## Purpose:

Open a napari viewer with all the raw ch1/ch2 Tiff stacks in a folder.
	
We are assuming a folder containing the output of Fiji conversion from raw Olympus files to to ch1/ch2 Tiff files.
	
## Requires these files
	
	aicsDataPath.py
	aicsGridNapari.py
	aicsUtil2.py

## 1) Install a virtual environment

### a) Either install with venv

```
# use 'deactivate' to make sure you are not already in a venv
# deactivate

# should make venv in nathan-raw-viewer folder
# cd nathan-raw-viewer

python -m venv raw_viewer_env
source raw_viewer_env/bin/activate
	
pip install pandas
pip install napari[all]

pip uninstall -y PyQt5
pip install PyQt5==5.13.1
```
	
#### Run from a virtual environment (see #2 below)

```
source raw_viewer_env/bin/activate
python nathan_20200717.py
```

### b) Or install with conda
	
```
conda create -y -n raw-viewer-env python=3.8
conda activate raw-viewer-env
pip install pandas
pip install napari[all]
	
pip uninstall -y PyQt5
pip install PyQt5==5.13.1
```

#### Run from a conda environment (see #2 below)

```
conda activate raw-viewer-env
python nathan_20200717.py
```

## 2) Point 'gDataPath' in 'aicsDataPath.py' to your raw data folder

Before you run your scripts, you need to specify the full path to your data folder. Open 'aicsDataPath.py' in a text editor and modify it

```
#
# set this to the full path to your data folder
#
gDataPath = '/Users/cudmore/data'
```


## 3) Writing scripts for new data folders

Each Python .py script to open a folder of raw data should look like this

```
import aicsUtil2 # does not require bimpy

#
# change this for each dataset (e.g. each folder of _ch1/_ch2 files)
#
folderStr = '20200717a'
dateStr = '20200717'
gridShape = (11,4)

# leave this
aicsUtil2.rawDataDriver(folderStr, dateStr, gridShape)
```

- folderStr: The name of the folder the ch1/ch2 files are in (often is the same as dateStr)
- dateStr: The yyyymmdd date in the filename, like 20200717__A01_G001_0004_ch2.tif
- gridShape: (rows,col)