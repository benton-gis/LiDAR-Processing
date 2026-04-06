import os
import json
import subprocess
import laspy
import numpy as np
import rasterio
from rasterio.crs import CRS
from datetime import datetime
from tqdm import tqdm

# ==== CONFIGURATION ====
input_folder = r"E:\map_data\common\LiDAR-Germany\Berlin-Nordost"
resolution = 0.5
nodata_value = -9999

# Output folders
dtm_folder = os.path.join(input_folder, "DTM")
dsm_folder = os.path.join(input_folder, "DSM")
chm_folder = os.path.join(input_folder, "CHM")
log_folder = os.path.join(input_folder, "logs")

for folder in [dtm_folder, dsm_folder, chm_folder, log_folder]:
    os.makedirs(folder, exist_ok=True)

log_file = os.path.join(log_folder, "processing.log")

# ==== LOGGING ====
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ==== CRS EXTRACTION ====
def extract_las_crs(las):
    if las.header.vlrs.get("WKT"):
        try:
            return CRS.from_wkt(las.header.vlrs["WKT"].string)
        except:
            pass
    try:
        crs = las.header.parse_crs()
        if crs:
            return CRS.from_wkt(crs.to_wkt())
    except:
        pass
    return CRS.from_epsg(25833)

# ==== PDAL PIPELINES ====
def run_pdal_pipeline(pipeline_json):
    result = subprocess.run(
        ["pdal", "pipeline", "--stdin"],
        input=pipeline_json.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8"))

# ---- DTM (TIN) ----
def build_dtm_pipeline(las_path, dtm_out, xmin, ymin, xmax, ymax):
    width = int(np.ceil((xmax - xmin) / resolution))
    height = int(np.ceil((ymax - ymin) / resolution))

    pipeline = [
        {"type": "readers.las", "filename": las_path},
        {"type": "filters.range", "limits": "Classification[2:2]"},
        {"type": "filters.delaunay"},
        {
            "type": "filters.faceraster",
            "resolution": resolution,
            "origin_x": float(xmin),
            "origin_y": float(ymax),
            "width": width,
            "height": height,
            "nodata": nodata_value
        },
        {
            "type": "writers.gdal",
            "filename": dtm_out,
            "resolution": resolution,
            "output_type": "all",
            "gdaldriver": "GTiff",
            "nodata": nodata_value
        }
    ]
    return json.dumps(pipeline)

# ---- DSM (GRID) using EXACT DTM geotransform ----
def build_dsm_pipeline_from_dtm(las_path, dsm_out, dtm_profile):
    transform = dtm_profile["transform"]
    width = dtm_profile["width"]
    height = dtm_profile["height"]

    origin_x = transform.c
    origin_y = transform.f

    pipeline = [
        {"type": "readers.las", "filename": las_path},
        {
            "type": "writers.gdal",
            "filename": dsm_out,
            "resolution": resolution,
            "origin_x": float(origin_x),
            "origin_y": float(origin_y),
            "width": width,
            "height": height,
            "output_type": "max",
            "gdaldriver": "GTiff",
            "nodata": nodata_value
        }
    ]
    return json.dumps(pipeline)

# ==== PROCESS FILES ====
files = [f for f in os.listdir(input_folder) if f.lower().endswith((".las", ".laz"))]

log(f"Starting processing of {len(files)} tiles")

for filename in tqdm(files, desc="Processing tiles"):
    las_path = os.path.join(input_folder, filename)

    base = os.path.splitext(filename)[0]
    dtm_out = os.path.join(dtm_folder, f"{base}_dtm_50cm.tif")
    dsm_out = os.path.join(dsm_folder, f"{base}_dsm_50cm.tif")
    chm_out = os.path.join(chm_folder, f"{base}_chm_50cm.tif")

    log(f"Processing {filename}")

    las = laspy.read(las_path)
    crs = extract_las_crs(las)
    log(f"CRS: {crs}")

    xmin, xmax = las.x.min(), las.x.max()
    ymin, ymax = las.y.min(), las.y.max()

    # ---- DTM ----
    log("Running PDAL TIN DTM...")
    dtm_pipeline = build_dtm_pipeline(las_path, dtm_out, xmin, ymin, xmax, ymax)
    run_pdal_pipeline(dtm_pipeline)
    log(f"Saved DTM -> {dtm_out}")

    # ---- Read DTM profile (THIS FIXES EVERYTHING) ----
    with rasterio.open(dtm_out) as dtm_ds:
        dtm_profile = dtm_ds.profile

    # ---- DSM using EXACT DTM grid ----
    log("Running PDAL DSM (max grid)...")
    dsm_pipeline = build_dsm_pipeline_from_dtm(las_path, dsm_out, dtm_profile)
    run_pdal_pipeline(dsm_pipeline)
    log(f"Saved DSM -> {dsm_out}")

    # ---- CHM ----
    log("Computing CHM...")
    with rasterio.open(dtm_out) as dtm_ds, rasterio.open(dsm_out) as dsm_ds:
        dtm = dtm_ds.read(1)
        dsm = dsm_ds.read(1)
        profile = dtm_ds.profile

    chm = dsm - dtm
    chm[(dtm == nodata_value) | (dsm == nodata_value)] = nodata_value

    profile.update(dtype=chm.dtype, nodata=nodata_value)

    with rasterio.open(chm_out, "w", **profile) as dst:
        dst.write(chm, 1)

    log(f"Saved CHM -> {chm_out}")

log("All tiles processed successfully.")
