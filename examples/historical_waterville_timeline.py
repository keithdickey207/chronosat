"""
Example: Historical NASA satellite coverage for Waterville, Maine

This script demonstrates both the offline simulation mode and real
Google Earth Engine data for the exact location used in your modern
NAIP/PyVista pipelines.

Run:
    python examples/historical_waterville_timeline.py
"""

from datetime import date
from chronosat import get_coverage_summary
from chronosat.missions import get_active_missions

# Waterville, Maine coordinates (same as your NAIP work)
LAT = 44.55
LON = -69.63

print("=" * 70)
print("CHRONOSAT — Historical NASA Coverage for Waterville, Maine")
print("=" * 70)
print()

# === 1. What missions were active on key dates? ===
print("Active missions on selected historical dates:\n")

dates_of_interest = [
    date(1973, 8, 15),   # Skylab era
    date(1975, 6, 14),   # Landsat 1 + 2 overlap
    date(1978, 4, 10),   # Just after Landsat 3 launch
    date(1980, 9, 5),    # Late period
]

for d in dates_of_interest:
    active = get_active_missions(d)
    names = ", ".join(m.short_name for m in active)
    print(f"  {d}  →  {names}")

print()

# === 2. Detailed pass estimation (simulation) ===
print("Estimated satellite overpass opportunities (simulation mode):\n")

for d in [date(1975, 6, 14), date(1978, 7, 22)]:
    print(get_coverage_summary(LAT, LON, d))
    print("-" * 60)
    print()

# === 3. Try real data (requires GEE auth) ===
print("\n[Real Data] Attempting Google Earth Engine search for June 1975...")
print("   (This will only work if you have run 'earthengine authenticate')\n")

try:
    from chronosat.gee import search_real_scenes, print_scene_summary

    real_scenes = search_real_scenes(
        LAT, LON,
        start="1975-06-01",
        end="1975-06-30",
        max_cloud=50.0,
        limit=8
    )
    print_scene_summary(real_scenes)

except Exception as e:
    print(f"   Real GEE search failed (expected if not authenticated): {e}")
    print("   To enable real data: pip install earthengine-api && earthengine authenticate")

print("\n" + "=" * 70)
print("Tip: Use these dates as input to your historical mesh / render pipeline.")
print("=" * 70)