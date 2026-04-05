# Notes
## Sunday 05 April 2026
Created a Win11 user named GIS-2 with no other applications installed other than miniforge (Miniforge3-26.1.1-2-Windows-x86_64.exe)

https://github.com/conda-forge/miniforge

The reason for this is QGIS and other applications where causing Path conflicts.
### Actions
1. conda activate base
2. conda env remove --name lidar_env
3. conda create -n lidar_env -c conda-forge python=3.10 pdal rasterio gdal numpy scipy shapely geopandas laspy
4. conda activate lidar_env
5. python test_create_dtm-ver3.py

conda create was stalling so co-pilot suggested using
1. conda config --set solver libmamba
