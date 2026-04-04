import json
import pdal
import numpy as np
import rasterio
from rasterio.transform import from_origin

# Path to your LAS file
las_file = r"C:\Users\GIS-1\Downloads\Nordost\3dm_33_402_5826_1_be.las"
output_tif = r"C:\Users\GIS-1\Downloads\Nordost\3dm_33_402_5826_1_be_dtm.tif"

# PDAL pipeline to filter ground points and create a raster
pipeline_json = {
    "pipeline": [
        las_file,
        {
            "type": "filters.range",  # Keep only ground points (ASPRS class 2)
            "limits": "Classification[2:2]"
        },
        {
            "type": "writers.gdal",   # Output raster
            "filename": output_tif,
            "resolution": 1.0,        # Grid resolution in meters
            "output_type": "idw",     # Interpolation method: inverse distance weighting
            "gdaldriver": "GTiff"
        }
    ]
}

# Run the PDAL pipeline
pipeline = pdal.Pipeline(json.dumps(pipeline_json))
try:
    pipeline.execute()
    print(f"DTM saved to {output_tif}")
except RuntimeError as e:
    print(f"Error creating DTM: {e}")


#conda install pdal -c conda-forge
