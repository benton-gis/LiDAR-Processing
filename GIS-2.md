# GIS-2
## Introduction
Some of the packages (gdal) required for LiDAR processing where clashing with QGIS and PostgreSQL installs on GIS-1. The solution was to create a Win11 user account that is only used for Python LiDAR processing.
The following explains how to install a Python environment suitable for LiDAR processing on Win11 and avoid conflicts with QGIS and PostgreSQL

Created a Win11 user named GIS-2 with no other applications installed other than miniforge (Miniforge3-26.1.1-2-Windows-x86_64.exe)

https://github.com/conda-forge/miniforge

It is also noted that Python 3.10 was required as some packages in this stack are incompatible with higher versions.

### Instructions
The following worked on 5 April 2026
#### Remove broken environment
<pre>1. conda activate base</pre>
<pre>2. conda env remove -n lidar_env</pre>
#### Force conda to use conda-forge only
<pre>4. conda config --set channel_priority strict</pre>
<pre>5. conda config --add channels conda-forge</pre>
#### Create a clean environment with Python 3.10
<pre>6. conda create -n lidar_env python=3.10</pre>
<pre>7. conda activate lidar_env</pre>
#### Install a compatible geospatial stack
<pre>8. conda install rasterio gdal geopandas shapely numpy scipy laspy pdal -c conda-forge</pre>
#### Remove from system variables (Administrator Account)
<pre>1. C:\Program Files\QGIS 3.40.13\bin</pre>
<pre>2. C:\Program Files\PostgreSQL\17\bin</pre>
#### Add environment variables to GIS-1 (So QGIS and PostgreSQL function correctly)
<pre>1. C:\Program Files\QGIS 3.40.13\bin</pre>
<pre>2. C:\Program Files\PostgreSQL\17\bin</pre>
### Run python script
[test_create_dtm-ver7c.py](bin/test_create_dtm-ver7c.py)
### Create virtual mosaic
#### Use CMD and enter the following
The following set command had to be use because of "GDAL is accidentally loading the PROJ database from PostgreSQL 17/PostGIS 3.5, which is older than the PROJ version GDAL was built against.
This breaks CRS loading, reprojection, and anything that touches coordinate systems." - reference Copilot
<pre>1. set PROJ_LIB=C:\Program Files\QGIS 3.40.13\share\proj</pre>
The following set command had to be used because of "That warning is GDAL being brutally honest with you:
your GeoTIFF contains GeoKey‑encoded CRS parameters that do not exactly match the official EPSG definition of EPSG:25833 (ETRS89 / UTM 33N).
This is extremely common with German LiDAR because many state agencies embed slightly customised projection parameters in the TIFF header." reference Copilot
<pre>2. set GTIFF_SRS_SOURCE=EPSG</pre>
<pre>3. gdalbuildvrt F:\map_data\Common\LiDAR-Germany\Berlin-Mitte\vrt_dtm.vrt F:\map_data\Common\LiDAR-Germany\Berlin-Mitte\Mitte\DTM\*.tif</pre>
<pre>4. gdalbuildvrt F:\map_data\Common\LiDAR-Germany\Berlin-Mitte\vrt_chm.vrt F:\map_data\Common\LiDAR-Germany\Berlin-Mitte\Mitte\CHM\*.tif</pre>
<pre>5. gdalbuildvrt F:\map_data\Common\LiDAR-Germany\Berlin-Mitte\vrt_dsm.vrt F:\map_data\Common\LiDAR-Germany\Berlin-Mitte\Mitte\DSM\*.tif</pre>
# Chapter 2 - LiDAR Processing
## Introduction
Problem experienced is a clash with PDAL and RASTERIO when installing. The suggestion is to install PDAL first and then all other packages.
#### Force conda to use conda-forge only
<pre>4. conda config --set channel_priority strict</pre>
<pre>5. conda config --add channels conda-forge</pre>
#### Create a clean environment with Python 3.10
<pre>6. conda create -n ldar_env python=3.10</pre>
<pre>7. conda activate ldar_env</pre>
#### Install a compatible geospatial stack
<pre>8. conda install rasterio gdal geopandas shapely numpy scipy laspy pdal -c conda-forge</pre>

