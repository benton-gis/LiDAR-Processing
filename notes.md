# Notes
## Sunday 05 April 2026
conda activate base
conda env remove --name lidar_env
conda create -n lidar_env -c conda-forge python=3.10 pdal rasterio gdal numpy scipy shapely geopandas laspy
conda activate lidar_env
python test_create_dtm-ver3.py
