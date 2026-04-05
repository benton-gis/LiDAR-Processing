# Notes
## Sunday 05 April 2026
Created a Win11 user named GIS-2 with no other applications installed other than miniforge (Miniforge3-26.1.1-2-Windows-x86_64.exe)

https://github.com/conda-forge/miniforge

The reason for this is QGIS and other applications where causing Path conflicts.
### Actions 1 
1. conda activate base
2. conda env remove --name lidar_env
3. conda create -n lidar_env -c conda-forge python=3.10 pdal rasterio gdal numpy scipy shapely geopandas laspy
4. The above point 3 stalled so went onto Actions 2
5. conda activate lidar_env
6. python test_create_dtm-ver3.py
### Actions 2
conda create was stalling so co-pilot suggested using
1. conda config --set solver libmamba
2. conda create -n lidar_env python=3.10
3. conda activate lidar_env
4. conda install -c conda-forge numpy scipy shapely geopandas
5. conda install -c laspy conda-forge
6. conda install -c conda-forge rasterio=1.4 gdal=3.8
7. python E:\map_data\scripts\LiDAR\test_create_dtm-ver3.py
### Actions 3
Installation is still failing going to try the following
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
#### Test Rasterio
9. python -c "import rasterio; print(rasterio.__version__)"
### Actions 4
#### Remove from system variables (Administrator Account)
1. C:\Program Files\QGIS 3.40.13\bin.
2. C:\Program Files\PostgreSQL\17\bin
#### Add environment variables to GIS-1
1. C:\Program Files\QGIS 3.40.13\bin
2. C:\Program Files\PostgreSQL\17\bin
