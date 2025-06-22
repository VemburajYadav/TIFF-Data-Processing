# 🛰️ TIF to Binary Converter for Flood Data Processing

This repository provides a simple Python script to process GeoTIFF flood data (e.g., from hydrological simulations or satellite sources) and convert it into binary files compatible with this [Unity-based immersive flood visualization system](https://github.com/VemburajYadav/Unity-Cesium-Flood-VR-MetaQuest).

The script extracts spatial and flood depth information, transforms coordinates into different reference systems (WGS84, ECEF), and saves structured binary outputs for efficient runtime use in Unity.

The script is modular and self-explanatory, and can be easily adapted to perform coordinate transformations to reference systems other than WGS84 and ECEF if needed.

---

## ⚙️ Installation

This project requires Python **3.10+**. It's recommended to use a **Conda environment**. [Rasterio](https://rasterio.readthedocs.io/en/stable/) is a Pythonic wrapper around [GDAL](https://gdal.org/en/stable/), which 
simplifies reading raster files and accessing geospatial metadata. [pyproj](https://pyproj4.github.io/pyproj/stable/index.html) provides a Python interface to the PROJ library for coordinate reference system (CRS) transformations.

```bash
conda create -n tiff-env python=3.10
conda activate tiff-env
conda install -c conda-forge numpy matplotlib
conda install -c conda-forge gdal
pip install rasterio
python -m pip install pyproj
```

---

## 🚀 Usage

```bash
python convert_tiff_to_bin.py --data_path ./data/flood_data.tif --save_dir ./processed/
```

- `--data_path`: Path to the input `.tif` file containing flood depth or elevation data.
- `--save_dir`: Path to the root directory where processed outputs should be stored.

A subdirectory will automatically be created inside `save_dir`, named after the TIF file (without extension).  

📁 Resulting structure:

```plaintext
processed/flood_data/
├── wgs84_matrix.bin
├── ecef_matrix.bin
├── src_crs_matrix.bin
├── water_depth_matrix.bin
├── invalid_mask.bin
└── flood_data_meta.json
```

## 🗃 Output Files Description

Each binary file is stored in **row-major order**, matching the layout of the original raster data:

- `wgs84_matrix.bin`: Latitude/longitude grid (EPSG:4326)
- `ecef_matrix.bin`: Earth-Centered, Earth-Fixed coordinates
- `src_crs_matrix.bin`: Grid in the original CRS of the GeoTIFF
- `water_depth_matrix.bin`: Flood depth values
- `invalid_mask.bin`: Binary mask for invalid or missing data points
- `flood_data_meta.json`: Metadata file describing the dataset's shape, data types, CRS, coordinate formats, and raster transform matrix

---
