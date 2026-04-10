Great — now I can build you a **Metashape settings profile tuned specifically for an AMD Ryzen 5 5600G with 8 GB RAM**.  
I’ll give you the **exact settings** that keep your machine stable, avoid memory crashes, and still produce clean terrestrial SfM results.

---

# ⚙️ **Metashape Profile for: Ryzen 5 5600G + 8 GB RAM (Integrated GPU)**

### **The core constraint:**  
Your system has **8 GB RAM** and **no discrete GPU**, which means:

- Depth maps must be run at **Low or Medium**  
- Meshes must be built from **Depth Maps**, not Dense Cloud  
- You must avoid High/Ultra settings (they will crash or swap to disk)  
- You should use **downscale factors** to keep memory safe  
- CPU-only processing is fine — the 5600G is actually quite capable for its class  

This profile is designed to be **bulletproof**, not “fast”.

---

# 🧩 **1. Preferences → GPU / CPU**
Since the 5600G uses integrated graphics:

- **Enable integrated GPU:** OFF  
  (Metashape’s OpenCL on iGPUs is slower and unstable)

- **Use CPU when performing GPU accelerated tasks:** ON  
- **CPU cores to use:** All cores  
- **RAM reserved for system:** 2 GB  
  (Metashape → Preferences → Advanced → “RAM reserved”)

---

# 📸 **2. Align Photos (Sparse Cloud)**
This step is light on RAM, so you can run it at high quality.

- **Accuracy:** High  
- **Generic preselection:** ON  
- **Reference preselection:** OFF (unless you have geotags)  
- **Key point limit:** 40,000  
- **Tie point limit:** 4,000  
- **Adaptive camera model fitting:** ON  

After alignment:
- **Gradual Selection:**  
  - Reconstruction Uncertainty: 10  
  - Projection Accuracy: 3  
  - Reprojection Error: 0.3–0.5  
- **Optimize Cameras** after each cleaning pass

This keeps your sparse cloud clean and improves depth-map quality later.

---

# 🌊 **3. Build Depth Maps**
This is the most memory‑intensive step.  
These settings prevent crashes on 8 GB RAM.

- **Quality:** Medium  
- **Downscale:** 2  
- **Filtering:** Mild  
- **Reuse depth maps:** ON (important for reprocessing)  
- **Calculate point colors:** OFF (saves RAM)  

If Medium crashes, drop to:

- **Quality:** Low  
- **Downscale:** 2  

---

# 🧱 **4. Build Mesh**
Use depth maps as the source.

- **Source data:** Depth Maps  
- **Face count:** Medium (1–2 million faces)  
- **Interpolation:** Enabled  
- **Point cloud source:** N/A  
- **Vertex colors:** OFF (optional)  

If you need a lighter model:

- **Face count:** Low (250k–500k)

---

# 🎨 **5. Build Texture**
Textures are not RAM‑heavy, so you can use decent settings.

- **Mapping mode:** Generic  
- **Blending mode:** Mosaic  
- **Texture size:** 4096 px  
- **Texture count:** 1  
- **Hole filling:** ON  

If you need a very lightweight model:

- **Texture size:** 2048 px

---

# 🗺️ **6. DEM / Orthomosaic (if needed)**
For terrestrial SfM, these are optional.

- **Build DEM:** From mesh  
- **Build Orthomosaic:** From DEM  
- **Blending mode:** Mosaic  
- **Fill holes:** ON  

---

# 📦 **7. Export Settings**
To keep file sizes manageable:

- **Mesh:** OBJ or PLY  
- **Texture:** JPG (lighter) or PNG (cleaner)  
- **Point cloud:** LAS (if needed)  

---

# 🧠 **8. Workflow Strategy for Low‑RAM Systems**
To avoid crashes:

- Restart Metashape before depth maps  
- Close all other apps  
- Keep project on an SSD  
- Use **chunks** if you have >300 images  
- Save after every major step  
- Use **Medium** depth maps as your default  

---

# 🎯 **Your optimized profile is ready**
This setup will give you:

- Stable processing  
- No out‑of‑memory errors  
- Clean terrestrial SfM results  
- Predictable runtimes  
- A workflow that respects your hardware limits  

---

If you want, I can also generate:

- A **printable version** of this profile  
- A **Metashape batch script** using these settings  
- A **field capture protocol** optimized for low‑RAM reconstruction  

Just tell me what you want next.
