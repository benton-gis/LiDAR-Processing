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
1. conda activate base
2. conda env remove -n lidar_env
#### Force conda to use conda-forge only
4. conda config --set channel_priority strict
5. conda config --add channels conda-forge
#### Create a clean environment with Python 3.10
6. conda create -n lidar_env python=3.10
7. conda activate lidar_env
#### Install a compatible geospatial stack
8. conda install rasterio gdal geopandas shapely numpy scipy laspy -c conda-forge
#### Remove from system variables (Administrator Account)
1. C:\Program Files\QGIS 3.40.13\bin.
2. C:\Program Files\PostgreSQL\17\bin
#### Add environment variables to GIS-1 (So QGIS and PostgreSQL function correctly)
1. C:\Program Files\QGIS 3.40.13\bin
2. C:\Program Files\PostgreSQL\17\bin
