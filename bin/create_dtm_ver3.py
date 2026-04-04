import laspy
import numpy as np
from scipy.interpolate import griddata
import rasterio
from rasterio.transform import from_origin

# ==== CONFIGURATION ====
las_file = r"C:\Users\GIS-1\Downloads\Nordost\3dm_33_402_5826_1_be.las"   # Path to your LAS file
output_tif = r"C:\Users\GIS-1\Downloads\Nordost\3dm_33_402_5826_1_be_dtm.tif"   # Output raster file
resolution = 1.0         # Grid resolution in meters
nodata_value = -9999     # Value for empty cells

# ==== 1. READ LAS FILE ====
try:
    las = laspy.read(las_file)
except Exception as e:
    raise RuntimeError(f"Error reading LAS file: {e}")

# ==== 2. FILTER GROUND POINTS ====
# ASPRS classification 2 = Ground
mask = las.classification == 2
if not np.any(mask):
    raise ValueError("No ground points found in the LAS file.")

x = las.x[mask]
y = las.y[mask]
z = las.z[mask]

# ==== 3. CREATE GRID ====
xmin, xmax = x.min(), x.max()
ymin, ymax = y.min(), y.max()

# Number of grid cells
nx = int(np.ceil((xmax - xmin) / resolution))
ny = int(np.ceil((ymax - ymin) / resolution))

# Grid coordinates
grid_x, grid_y = np.meshgrid(
    np.linspace(xmin, xmax, nx),
    np.linspace(ymax, ymin, ny)  # Note: y reversed for raster orientation
)

# ==== 4. INTERPOLATE ====
print("Interpolating... This may take time for large datasets.")
grid_z = griddata(
    points=(x, y),
    values=z,
    xi=(grid_x, grid_y),
    method='linear',
    fill_value=nodata_value
)

# ==== 5. SAVE AS GEOTIFF ====
transform = from_origin(xmin, ymax, resolution, resolution)

with rasterio.open(
    output_tif,
    'w',
    driver='GTiff',
    height=grid_z.shape[0],
    width=grid_z.shape[1],
    count=1,
    dtype=grid_z.dtype,
    crs=las.header.parse_crs() or "EPSG:4326",  # Use LAS CRS if available
    transform=transform,
    nodata=nodata_value
) as dst:
    dst.write(grid_z, 1)

print(f"✅ DTM saved to {output_tif}")
