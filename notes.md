# Notes
## Sunday 05 April 2026
1. conda activate base
2. conda env remove --name lidar_env
3. conda create -n lidar_env -c conda-forge python=3.10 pdal rasterio gdal numpy scipy shapely geopandas laspy
4. conda activate lidar_env
5. python test_create_dtm-ver3.py
