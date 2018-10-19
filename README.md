# araw2tif
[![Travis CI Status](https://travis-ci.org/chunglabmit/araw2tif.svg?branch=master)](https://travis-ci.org/chunglabmit/araw2tif)

A utility for backing up .raw files to .tif

This is a handy little utility for monitoring a file hierarchy of .raw files, 
archiving them as .tif to a new location.

To install:
```
$ pip install https://github.com/chunglabmit/araw2tif
```

Usage:
```
araw2tif --src <source-folder>\
         --dest <dest-folder>\
         [--n-cpus <cpu-count>]\
         [--compress <compress-level>]\
         [--silent]\
         [--src-ext <source-extension>]\
         [--dest-ext <destination-extension]
```
Where:
* **source-folder** - the root of the source hierarchy
* **dest-folder** - the root of the destination hierarchy
* **cpu-count** - the number of CPUs to operate in parallel (default all cpus)
* **compress-level** - the TIFF compression level (default 3)
* **--silent** - suppress console progress bars
* **source-extension** - extension of raw image files (defaults to .raw)
* **destination-extension** - extension of tiff image files (defaults to .tiff) 

All .raw files with a modification date after that of corresponding .tiff files
(and .raw files not included in the .tiff hierarchy) are queued for copy.
