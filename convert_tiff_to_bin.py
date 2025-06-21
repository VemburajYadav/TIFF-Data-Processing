import os.path
import rasterio
import argparse
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from rasterio.warp import transform_bounds
from pyproj import Transformer
import json


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-path", type=str, help="Path to data",
                        default="./tiff_samples/flood_data.tif")
    parser.add_argument("--save_dir", type=str, help="Directory to save the processed data",
                        default="./processed_samples")

    args = parser.parse_args()

    src = rasterio.open(args.data_path, mode='r')
    data = src.read(1)

    masked_matrix = np.ma.masked_where(data == -9999.0, data)
    cmap_values = plt.cm.Blues
    cmap_values.set_bad('gray')

    norm = plt.Normalize(vmin=np.min(data[data != -9999.0]), vmax=np.max(data[data != -9999.0]))

    # Plot
    plt.figure()
    plt.imshow(masked_matrix, cmap=cmap_values, norm=norm, interpolation='nearest')
    plt.colorbar()
    plt.show()

    # coordinate transformation
    data_bounds = src.bounds
    data_src = src.crs

    # convert to EPSG:4326 CRS (Longitude, Latitude)
    wgs84_bounds = transform_bounds(data_src, "EPSG:4326", *data_bounds)
    wgs84_transformer = Transformer.from_crs(data_src, "EPSG:4326", always_xy=True)
    min_lon, min_lat = wgs84_transformer.transform(data_bounds.left, data_bounds.top)
    wgs84_matrix = np.empty((src.height, src.width, 2), dtype=np.double)

    # convert to EPSG:4978 CRS (Earth Centered, Earth Fixed)
    ecef_bounds = transform_bounds(data_src, "EPSG:4978", *data_bounds)
    ecef_transformer = Transformer.from_crs(data_src, "EPSG:4978", always_xy=True)
    ecef_matrix = np.empty((src.height, src.width, 2), dtype=np.double)

    src_crs_matrix = np.empty((src.height, src.width, 2), dtype=np.double)

    for i in range(src.height):
        for j in range(src.width):
            src_crs_x, src_crs_y = src.xy(i, j, offset="center")
            src_crs_matrix[i, j, 0], src_crs_matrix[i, j, 1] = src_crs_x, src_crs_y

            lon, lat = wgs84_transformer.transform(src_crs_x, src_crs_y)
            wgs84_matrix[i, j, 0], wgs84_matrix[i, j, 1] = lon, lat

            ecef_x, ecef_y = ecef_transformer.transform(src_crs_x, src_crs_y)
            ecef_matrix[i, j, 0], ecef_matrix[i, j, 1] = ecef_x, ecef_y

    save_dir = os.path.join(args.save_dir, args.data_path.split("/")[-1].split('.tif')[0])
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    # Save the main matrices as float64
    ecef_matrix.astype('float64').tofile(os.path.join(save_dir, "ecef_matrix.bin"))
    wgs84_matrix.astype('float64').tofile(os.path.join(save_dir, "wgs84_matrix.bin"))
    src_crs_matrix.astype('float64').tofile(os.path.join(save_dir, "src_crs_matrix.bin"))
    masked_matrix.data.astype('float64').tofile(os.path.join(save_dir, "water_depth_matrix.bin"))

    # Save the invalid mask as uint8 (1 for True, 0 for False)
    masked_matrix.mask.astype('uint8').tofile(os.path.join(save_dir, "invalid_mask.bin"))

    # Metadata
    meta = {
        "shape": ecef_matrix.shape[:2],              # (height, width)
        "dtype": "float64",                             # for the numeric matrices
        "mask_dtype": "uint8",                          # for the invalid mask
        "ecef_format": "x,y",
        "wgs84_format": "lon,lat",
        "src_crs_format": "x,y",
        "crs": str(src.crs),
        "transform": src.transform.to_gdal()        # affine geotransform
    }

    with open(os.path.join(save_dir, "flood_data_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)


