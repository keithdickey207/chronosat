"""
Example: Feeding historical Landsat MSS data into a 3D mesh pipeline

This is a conceptual bridge between chronosat historical data and
your existing modern workflows (naip_urban_pipeline.py + PyVista + Godot).

Once you have downloaded a GeoTIFF from the GEE export example,
you can adapt this pattern.

Key differences from modern NAIP:
- Much lower resolution (~60-80m vs 30cm)
- Only 4 bands (MSS)
- Different radiometric calibration
- Heavy atmospheric effects possible in 1970s data
"""

import os
import rasterio
from rasterio.vrt import WarpedVRT
from rasterio.windows import from_bounds
import numpy as np
import pyvista as pv

# Example bounding box for Waterville core (same as your modern work)
BBOX = [-69.65, 44.53, -69.61, 44.56]


def process_historical_mss_geotiff(
    geotiff_path: str,
    output_mesh: str = "~/chronosat_historical_mesh.ply",
    target_dim: int = 512,   # Much lower than modern 2000 because of resolution
):
    """
    Convert a downloaded historical MSS GeoTIFF into a 3D mesh.
    This is intentionally simplified — real work would need better
    band selection, atmospheric correction, and color balancing.
    """
    print(f"[*] Processing historical MSS: {geotiff_path}")

    with rasterio.Env(GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(geotiff_path) as src:
            with WarpedVRT(src, crs="EPSG:4326") as vrt:
                window = from_bounds(*BBOX, vrt.transform).round()
                # MSS has bands 4,5,6,7 (NIR + visible). We take what we can.
                matrix = vrt.read([1, 2, 3], window=window, out_shape=(3, target_dim, target_dim))

    bands, height, width = matrix.shape

    # Very crude "elevation" from brightness (not real terrain!)
    x, y = np.meshgrid(np.arange(0, width, dtype=np.float32),
                       np.arange(0, height, dtype=np.float32))
    z = (matrix[1].astype(np.float32) / 255.0) * 30.0   # smaller height exaggeration

    grid = pv.StructuredGrid(x, y, z)
    grid.point_data["RGB"] = np.column_stack((
        matrix[0].flatten(),
        matrix[1].flatten(),
        matrix[2].flatten()
    ))

    surface = grid.extract_surface(algorithm="dataset_surface")

    out_path = os.path.expanduser(output_mesh)
    surface.save(out_path, binary=True)
    print(f"[Success] Historical mesh saved → {out_path}")
    print("You can now load this in render_snapshot.py or your Godot scenes.")


if __name__ == "__main__":
    # After running the GEE export example and downloading a file:
    example_path = "~/Downloads/chronosat_LM01_19750614_023045.tif"  # placeholder name

    if os.path.exists(os.path.expanduser(example_path)):
        process_historical_mss_geotiff(example_path)
    else:
        print("No example GeoTIFF found at the placeholder path.")
        print("1. Run examples/export_real_mss_to_drive.py")
        print("2. Download the resulting file from Google Drive")
        print("3. Update the path in this script and re-run.")