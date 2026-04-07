import os
import json
import subprocess
import laspy
import numpy as np
import rasterio
from rasterio.crs import CRS
from datetime import datetime
from tqdm import tqdm
from multiprocessing import Pool, cpu_count

# =========================
# LIMIT INTERNAL THREADING TO 75% CPU
# =========================
max_threads = max(1, int(cpu_count() * 0.75))

os.environ["OMP_NUM_THREADS"] = str(max_threads)
os.environ["OPENBLAS_NUM_THREADS"] = str(max_threads)
os.environ["MKL_NUM_THREADS"] = str(max_threads)
os.environ["NUMEXPR_NUM_THREADS"] = str(max_threads)

# ==== CONFIGURATION ====
#input_folder = r"E:\map_data\common\LiDAR-Germany\Berlin-Nordost"
input_folder = r"F:\map_data\Common\LiDAR-Germany\Berlin-Mitte\Mitte"
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

# ==== PDAL RUNNER ====
def run_pdal_pipeline(pipeline_json):
    result = subprocess.run(
        ["pdal", "pipeline", "--stdin"],
        input=pipeline_json.encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8"))

# ==== DTM / DSM PIPELINES ====
def build_dtm_pipeline(las_path, dtm_out, xmin, ymin, xmax, ymax):
    bounds_str = f"([{xmin},{xmax}],[{ymin},{ymax}])"
    pipeline = [
        {"type": "readers.las", "filename": las_path},
        {"type": "filters.range", "limits": "Classification[2:2]"},
        {
            "type": "writers.gdal",
            "filename": dtm_out,
            "resolution": resolution,
            "bounds": bounds_str,
            "output_type": "min",
            "gdaldriver": "GTiff",
            "nodata": nodata_value
        }
    ]
    return json.dumps(pipeline)

def build_dsm_pipeline(las_path, dsm_out, xmin, ymin, xmax, ymax):
    bounds_str = f"([{xmin},{xmax}],[{ymin},{ymax}])"
    pipeline = [
        {"type": "readers.las", "filename": las_path},
        {
            "type": "writers.gdal",
            "filename": dsm_out,
            "resolution": resolution,
            "bounds": bounds_str,
            "output_type": "max",
            "gdaldriver": "GTiff",
            "nodata": nodata_value
        }
    ]
    return json.dumps(pipeline)

# ==== PER-TILE PROCESSING FUNCTION ====
def process_tile(filename):
    try:
        las_path = os.path.join(input_folder, filename)

        base = os.path.splitext(filename)[0]
        dtm_out = os.path.join(dtm_folder, f"{base}_dtm_50cm.tif")
        dsm_out = os.path.join(dsm_folder, f"{base}_dsm_50cm.tif")
        chm_out = os.path.join(chm_folder, f"{base}_chm_50cm.tif")

        log(f"[{filename}] Starting")

        # ---- READ LAS ----
        las = laspy.read(las_path)

        # ---- CRS ----
        crs = extract_las_crs(las)
        log(f"[{filename}] CRS: {crs}")

        # ---- BOUNDS ----
        xmin, xmax = las.x.min(), las.x.max()
        ymin, ymax = las.y.min(), las.y.max()

        # ---- DTM ----
        log(f"[{filename}] Running PDAL DTM...")
        dtm_pipeline = build_dtm_pipeline(las_path, dtm_out, xmin, ymin, xmax, ymax)
        run_pdal_pipeline(dtm_pipeline)
        log(f"[{filename}] Saved DTM")

        # ---- DSM ----
        log(f"[{filename}] Running PDAL DSM...")
        dsm_pipeline = build_dsm_pipeline(las_path, dsm_out, xmin, ymin, xmax, ymax)
        run_pdal_pipeline(dsm_pipeline)
        log(f"[{filename}] Saved DSM")

        # ---- CHM ----
        log(f"[{filename}] Computing CHM...")
        with rasterio.open(dtm_out) as dtm_ds, rasterio.open(dsm_out) as dsm_ds:
            dtm = dtm_ds.read(1)
            dsm = dsm_ds.read(1)
            profile = dtm_ds.profile

        # Shape guard
        if dsm.shape != dtm.shape:
            log(f"[{filename}] Shape mismatch, cropping")
            min_rows = min(dtm.shape[0], dsm.shape[0])
            min_cols = min(dtm.shape[1], dsm.shape[1])
            dtm = dtm[:min_rows, :min_cols]
            dsm = dsm[:min_rows, :min_cols]

        chm = dsm - dtm
        chm[(dtm == nodata_value) | (dsm == nodata_value)] = nodata_value

        profile.update(dtype=chm.dtype, nodata=nodata_value)

        with rasterio.open(chm_out, "w", **profile) as dst:
            dst.write(chm, 1)

        log(f"[{filename}] Saved CHM")
        return True

    except Exception as e:
        log(f"[{filename}] ERROR: {e}")
        return False

# ==== MULTIPROCESSING DRIVER (75% CPU) ====
if __name__ == "__main__":
    files = [f for f in os.listdir(input_folder) if f.lower().endswith((".las", ".laz"))]
    log(f"Starting multiprocessing of {len(files)} tiles")

    # USE 75% OF CPU CORES
    workers = max(1, int(cpu_count() * 0.75))
    log(f"Using {workers} CPU cores (75% of system cores)")

    with Pool(processes=workers) as pool:
        results = list(
            tqdm(
                pool.imap_unordered(process_tile, files),
                total=len(files),
                desc="Processing tiles"
            )
        )

    success = sum(results)
    log(f"Completed {success}/{len(files)} tiles successfully.")
