# chronosat

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/keithdickey207/chronosat/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![GitHub stars](https://img.shields.io/github/stars/keithdickey207/chronosat?style=social)](https://github.com/keithdickey207/chronosat)
[![GitHub](https://img.shields.io/badge/GitHub-keithdickey207/chronosat-181717?logo=github)](https://github.com/keithdickey207/chronosat)

**NASA Earth observation history (1970–1981) for mapping and 3D visualization.**

Reconstruct what the earliest civilian Earth-observation satellites (Landsat 1–3 and Skylab EREP) saw over any location during the 1970s and early 1980s.

> **Reality check**: This is purely historical/archival work. There are no real-time feeds from 1975.

---

## WQSH Orbital Daemon v0.1-alpha (Live Layer)

This repo also ships a **zero-dependency live orbital layer** for the sovereign stack — circuit-compressed Keplerian propagation, JSON export, and a Godot 4 viewer. No pip required for the daemon.

```bash
cd orbital_daemon
bash run_demo.sh
# → output/orbital_positions.json

# Godot twin: open orbital_daemon/godot/chronosat_viewer/ in Godot 4.3+
python3 chronosat_daemon.py -w 2   # live refresh
```

See [`orbital_daemon/README.md`](orbital_daemon/README.md) for details.

---

## Why This Exists

Modern satellite data (Landsat 8/9, Sentinel-2, NAIP, etc.) is abundant and high quality. The earliest years of the Landsat program (1972–1981) are much harder to work with, yet they represent the beginning of continuous global land imaging.

`chronosat` gives you:

- Accurate knowledge of what satellites were operating on any given date
- Practical tools to discover and retrieve real historical imagery
- Clear bridges to 3D visualization and creative pipelines

## Features

- **Mission database** — Complete facts for Landsat 1, 2, 3 + Skylab EREP (1972–1981)
- **Pass estimation** — Lightweight 18-day repeat cycle modeling for any location + date
- **Offline simulation** — Works immediately with no accounts or API keys
- **Real data access** — First-class Google Earth Engine support for actual MSS imagery
- **Export pipeline** — One-command exports to Google Drive as GeoTIFFs
- **Designed for creators** — Built to integrate with PyVista, rasterio, Godot, and similar tools
- **Live orbital daemon** — Stdlib Keplerian circuits + Godot viewer for real-time demos

## Quick Start

```bash
git clone https://github.com/keithdickey207/chronosat.git
cd chronosat

# 1. See the mission timeline
python3 cli.py missions

# 2. What NASA satellites were overhead on a specific historical date?
python3 cli.py coverage --lat 44.55 --lon -69.63 --date 1975-06-14

# 3. Find real historical coverage (simulation)
python3 cli.py search --lat 44.55 --lon -69.63 --start 1975-01-01 --end 1975-12-31
```

## Installation

```bash
pip install -e .
```

Recommended extras:

```bash
pip install -e ".[gee]"     # Google Earth Engine support
pip install -e ".[viz]"     # PyVista + raster tools for mesh generation
```

## Real Historical Imagery (Google Earth Engine)

This is the most powerful part of the project.

```bash
pip install earthengine-api
earthengine authenticate     # one-time browser login
```

Then use the new GEE module:

```python
from chronosat.gee import search_real_scenes, export_to_drive, print_scene_summary

scenes = search_real_scenes(44.55, -69.63, "1975-06-01", "1975-08-31", max_cloud=30)
print_scene_summary(scenes)

# Export the best one to your Google Drive
export_to_drive(scenes[0], folder="chronosat_exports", wait=True)
```

See the full examples in the [`examples/`](examples/) directory.

## Example Scripts

Located in `examples/`:

| Script | Purpose |
|--------|---------|
| `historical_waterville_timeline.py` | Timeline + pass estimation for Waterville, Maine (the location used in many modern pipelines) |
| `export_real_mss_to_drive.py` | End-to-end: search real 1975 scenes and export GeoTIFF to Drive |
| `feed_into_mesh_pipeline.py` | Shows how to adapt existing raster → PyVista mesh code for historical MSS data |

## Integration With Modern Pipelines

This tool was created specifically to extend existing modern workflows (NAIP, Sentinel, high-res 3D meshing, Godot visualization, etc.).

Typical creative/research flow:

1. Use `chronosat` to discover interesting historical dates for a location
2. Export real MSS GeoTIFFs via Google Earth Engine
3. Adapt your existing rasterio + PyVista code to handle the older 4-band, lower-resolution data
4. Generate 1975 vs 2025 comparison renders or time-lapse sequences

The orbit module can be upgraded with real historical TLEs using Skyfield (you may already have this in your environment).

## Repository Structure

```
chronosat/
├── chronosat/
│   ├── missions.py       # Authoritative mission facts
│   ├── orbits.py         # Pass estimation engine
│   ├── catalog.py        # Simulation catalog
│   ├── gee.py            # Real Google Earth Engine helpers
│   └── __init__.py
├── orbital_daemon/       # Live Keplerian layer + Godot viewer (v0.1-alpha)
├── examples/             # Ready-to-run demonstration scripts
├── cli.py
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── LICENSE
└── .github/              # Issue & PR templates
```

## License

MIT License © 2026 [Keith Dickey](https://github.com/keithdickey207)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Particularly valuable areas right now:
- Historical TLE / precise orbit reconstruction
- Better radiometric or atmospheric handling for early MSS
- Godot / Blender exporters
- More example locations and creative visualizations
- SGP4 / TLE ingestion for the live orbital daemon

## Links

- **Repository**: https://github.com/keithdickey207/chronosat
- **Issues**: https://github.com/keithdickey207/chronosat/issues
- **Author**: https://github.com/keithdickey207

---

Built for historical research, creative visualization, and extending modern Earth observation pipelines into the past.