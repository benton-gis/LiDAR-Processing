# LiDAR Processing

## Create envvironment and activate

Install packages below so that all packages are compaible, do not install seperately.

1. conda create -n lidar_env -c conda-forge python=3.10 pdal rasterio gdal numpy scipy
2. conda activate lidar_env

These are the packags that are required
1. laspy
2. numpy
3. scipy
4. rasterio

## Handy commands
conda list

To see details and if a package exists.
1. conda list laspy

Install package if missing.
1. conda install laspy -c conda-forge

Update everything
1. conda update -n base -c conda-forge conda

## Free Data
### Berlin LiDAR List
https://gdi.berlin.de/geonetwork/srv/ger/catalog.search#/metadata/f4a8997d-4dea-382f-aa3a-d452f4bf3943

## Useful tools
The Berlin LiDAR portal times out after several minutes. Use [aria2](https://aria2.github.io) for a more positive download experience

Unzip aria2 into C Drive something like this C:\aria2-1.37.0-win-64bit-build1 and then add to Windows Path or use full path in command line as per below (note that there are other parts of the city available [view index](https://gdi.berlin.de/data/a_als/atom/Blattschnitt2x2km.gif))

<pre>C:\aria2-1.37.0-win-64bit-build1\aria2c.exe -x 16 -s 16 -k 1M --continue=true "https://gdi.berlin.de/data/a_als/atom/Nordost.zip"</pre>

<pre>C:\aria2-1.37.0-win-64bit-build1\aria2c.exe -x 16 -s 16 -k 1M --continue=true "https://gdi.berlin.de/data/a_als/atom/Mitte.zip"</pre>

<pre>C:\aria2-1.37.0-win-64bit-build1\aria2c.exe -x 16 -s 16 -k 1M --continue=true "https://gdi.berlin.de/data/a_als/atom/Sued.zip"</pre>

