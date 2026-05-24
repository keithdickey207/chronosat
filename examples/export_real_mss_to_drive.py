"""
Example: Export real 1970s Landsat MSS imagery to Google Drive

This shows the practical workflow for getting actual historical GeoTIFFs.

Requirements:
    pip install earthengine-api
    earthengine authenticate

Then run this script. It will start an export task in Earth Engine.

After it finishes, you can download the GeoTIFF from your Google Drive
and feed it into your PyVista / Godot pipeline (similar to NAIP).
"""

from chronosat.gee import search_real_scenes, export_to_drive, print_scene_summary

# Target: Waterville, Maine (or change to anywhere)
LAT = 44.55
LON = -69.63

print("Searching for the clearest real Landsat MSS scenes over Waterville in summer 1975...\n")

scenes = search_real_scenes(
    LAT, LON,
    start="1975-06-01",
    end="1975-08-31",
    max_cloud=35.0,
    limit=5
)

print_scene_summary(scenes)

if not scenes:
    print("No scenes found. Try a different date range or relax the cloud filter.")
    exit()

best = scenes[0]
print(f"\n→ Best candidate: {best.id} ({best.mission}, {best.cloud_cover}% cloud)")

print("\nStarting export to Google Drive folder 'chronosat_exports'...")
print("This will run in the cloud (Earth Engine). It can take several minutes.\n")

result = export_to_drive(
    best,
    folder="chronosat_exports",
    scale=60,                    # ~60m is appropriate for MSS data
    region_buffer_km=12.0,
    wait=True                    # Block until finished (good for scripts)
)

print("\nExport result:")
for k, v in result.items():
    print(f"  {k}: {v}")

print("\nWhen complete, download the GeoTIFF from your Google Drive.")
print("You can then process it with rasterio + pyvista, just like your modern NAIP data.")
print("\nNext step idea: Adapt naip_urban_pipeline.py to accept 4-band MSS input.")