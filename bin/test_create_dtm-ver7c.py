import os
import laspy
import numpy as np
from scipy.interpolate import griddata
import rasterio
from rasterio.transform import from_origin
from rasterio.crs import CRS
from datetime import datetime
from tqdm import tqdm   # progress bar

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

# ==== LOGGING (ASCII SAFE) ====
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)  # console may be cp1252 → keep ASCII only
    with open(os.path.join(log_folder, "processing.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ==== CRS EXTRACTION ====
def extract_las_crs(las):
    # 1. Try WKT VLR
    if las.header.vlrs.get("WKT"):
        try:
            return CRS.from_wkt(las.header.vlrs["WKT"].string)
        except:
            pass

    # 2. Try laspy parser
    try:
        crs = las.header.parse_crs()
        if crs:
            return CRS.from_wkt(crs.to_wkt())
    except:
        pass

    # 3. Fallback for Berlin (ETRS89 / UTM 33N)
    return CRS.from_epsg(25833)

# ==== PROCESS ALL LAS/LAZ FILES ====
files = [f for f in os.listdir(input_folder) if f.lower().endswith((".las", ".laz"))]

log(f"Starting processing of {len(files)} tiles")

for filename in tqdm(files, desc="Processing tiles"):
    las_path = os.path.join(input_folder, filename)

    base = os.path.splitext(filename)[0]
    dtm_out = os.path.join(dtm_folder, f"{base}_dtm_50cm.tif")
    dsm_out = os.path.join(dsm_folder, f"{base}_dsm_50cm.tif")
    chm_out = os.path.join(chm_folder, f"{base}_chm_50cm.tif")

    log(f"Processing {filename}")

    # ---- 1. READ LAS ----
    las = laspy.read(las_path)

    # ---- 1b. CRS ----
    crs = extract_las_crs(las)
    log(f"CRS: {crs}")

    # ---- 2. FILTER CLASSES ----
    ground_mask = las.classification == 2
    non_ground_mask = las.classification != 2

    if not np.any(ground_mask):
        log("No ground points found, skipping.")
        continue

    # Ground points
    xg = las.x[ground_mask]
    yg = las.y[ground_mask]
    zg = las.z[ground_mask]

    # All points (for DSM)
    xa = las.x
    ya = las.y
    za = las.z

    # ---- 3. GRID EXTENT ----
    xmin, xmax = xa.min(), xa.max()
    ymin, ymax = ya.min(), ya.max()

    nx = int(np.ceil((xmax - xmin) / resolution))
    ny = int(np.ceil((ymax - ymin) / resolution))

    grid_x, grid_y = np.meshgrid(
        np.linspace(xmin, xmax, nx),
        np.linspace(ymax, ymin, ny)
    )

    # ---- 4. INTERPOLATE DTM ----
    log("Interpolating DTM...")
    dtm = griddata(
        points=(xg, yg),
        values=zg,
        xi=(grid_x, grid_y),
        method='linear',
        fill_value=nodata_value
    )

    # ---- 5. INTERPOLATE DSM ----
    log("Interpolating DSM...")
    dsm = griddata(
        points=(xa, ya),
        values=za,
        xi=(grid_x, grid_y),
        method='linear',
        fill_value=nodata_value
    )

    # ---- 6. CHM = DSM - DTM ----
    log("Computing CHM...")
    chm = dsm - dtm
    chm[dtm == nodata_value] = nodata_value
    chm[dsm == nodata_value] = nodata_value

    # ---- 7. SAVE RASTERS ----
    transform = from_origin(xmin, ymax, resolution, resolution)

    def save_raster(path, array):
        with rasterio.open(
            path,
            'w',
            driver='GTiff',
            height=array.shape[0],
            width=array.shape[1],
            count=1,
            dtype=array.dtype,
            crs=crs,
            transform=transform,
            nodata=nodata_value
        ) as dst:
            dst.write(array, 1)

    save_raster(dtm_out, dtm)
    save_raster(dsm_out, dsm)
    save_raster(chm_out, chm)

    log(f"Saved DTM -> {dtm_out}")
    log(f"Saved DSM -> {dsm_out}")
    log(f"Saved CHM -> {chm_out}")

log("All tiles processed successfully.")
