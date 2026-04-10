import Metashape

doc = Metashape.app.document
chunk = doc.addChunk()

# -----------------------------
# 1. Add Photos
# -----------------------------
# Replace with your image folder
image_folder = r"C:\path\to\images"
import os
photos = [os.path.join(image_folder, f) for f in os.listdir(image_folder)
          if f.lower().endswith((".jpg", ".jpeg", ".tif", ".tiff", ".png"))]
chunk.addPhotos(photos)

# -----------------------------
# 2. Align Photos (Sparse Cloud)
# -----------------------------
chunk.matchPhotos(
    accuracy=Metashape.HighAccuracy,
    generic_preselection=True,
    reference_preselection=False,
    keypoint_limit=40000,
    tiepoint_limit=4000,
    adaptive_fitting=True
)

chunk.alignCameras()

# -----------------------------
# 3. Gradual Selection + Optimization
# -----------------------------
f = chunk.point_cloud

# Reconstruction Uncertainty
f.removePoints(f.selectPoints(Metashape.PointCloud.Filter.ReconstructionUncertainty, 10))
chunk.optimizeCameras()

# Projection Accuracy
f.removePoints(f.selectPoints(Metashape.PointCloud.Filter.ProjectionAccuracy, 3))
chunk.optimizeCameras()

# Reprojection Error
f.removePoints(f.selectPoints(Metashape.PointCloud.Filter.ReprojectionError, 0.5))
chunk.optimizeCameras()

# -----------------------------
# 4. Build Depth Maps
# -----------------------------
chunk.buildDepthMaps(
    quality=Metashape.MediumQuality,
    filter=Metashape.MildFiltering,
    downscale=2,
    reuse_depth=True
)

# -----------------------------
# 5. Build Mesh
# -----------------------------
chunk.buildModel(
    source_data=Metashape.DepthMapsData,
    interpolation=Metashape.EnabledInterpolation,
    face_count=Metashape.MediumFaceCount
)

# -----------------------------
# 6. Build Texture
# -----------------------------
chunk.buildUV(mapping_mode=Metashape.GenericMapping)
chunk.buildTexture(
    blending_mode=Metashape.MosaicBlending,
    texture_size=4096,
    texture_count=1,
    fill_holes=True
)

# -----------------------------
# 7. Save Project
# -----------------------------
doc.save(r"C:\path\to\project.psx")
