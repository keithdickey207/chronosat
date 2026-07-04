# chronosat

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/keithdickey207/chronosat/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![GitHub stars](https://img.shields.io/github/stars/keithdickey207/chronosat?style=social)](https://github.com/keithdickey207/chronosat)
[![GitHub](https://img.shields.io/badge/GitHub-keithdickey207/chronosat-181717?logo=github)](https://github.com/keithdickey207/chronosat)

**NASA Earth observation history (1970–1981) for mapping and 3D visualization.**

Reconstruct what the earliest civilian Earth-observation satellites (Landsat 1–3 and Skylab EREP) saw over any location during the 1970s and early 1980s.

**Anchor:** `44.5520°N, 69.6317°W` (Waterville, ME 04901)


> **Reality check**: Historical/archival work uses real MSS archives. The live orbital daemon is a **present-day** Keplerian demo layer — not a 1975 real-time feed.

---

## WQSH Orbital Daemon v0.1-alpha (Live Layer)

Zero-dependency live orbital layer for the sovereign stack — circuit-compressed Keplerian propagation, JSON export, and a Godot 4 viewer. No pip required for the daemon.

```
chronosat_daemon.py  ──JSON──►  Godot chronosat_viewer
                         │
                         └──►  Aether Navigation / District 04901 spatial layers (future)
```

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
- A live orbital daemon for Godot demos on edge nodes (Penguin, Red Laptop, Synology)

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
| `historical_waterville_timeline.py` | Timeline + pass estimation for Waterville, Maine (04901 anchor) |
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

## Sovereign Stack

| Project | Role |
|---------|------|
| **[Aether Core](https://github.com/keithdickey207/aether)** | Brain hub — USD-4 protocol, RF lab, medical, Godot 4 bridge |
| **[District 04901 Grid](https://github.com/keithdickey207/District_04901_Grid)** | Spatial C2 — React VM canvas, UDP/WS telemetry mesh |
| **[dickey-sovereign-core](https://github.com/keithdickey207/dickey-sovereign-core)** | Fusion + tactile physics + LogisticsMatrix |
| **[waterville-ar](https://github.com/keithdickey207/waterville-ar)** | Godot city builder — 78 building footprints |
| **[04901-digital-twin](https://github.com/keithdickey207/04901-digital-twin)** | Godot digital twin — ram ingest lattice |
| **[04901-alchemical-chamber](https://github.com/keithdickey207/04901-alchemical-chamber)** | Godot Newton chymical lab node |
| **chronosat** (this repo) | Orbital daemon + historical Landsat viewer |
| **[04901-sentinel](https://github.com/keithdickey207/04901-sentinel)** | NORAD tracker + bug bounty hunter |
| **[04901_Taxi_Dispatch](https://github.com/keithdickey207/04901_Taxi_Dispatch)** | Local-first taxi dispatch + fleet sim |
| **[document-fraud-detection-engine](https://github.com/keithdickey207/document-fraud-detection-engine)** | Sovereign document forensics |
| **[secure-self-healing-orchestrator](https://github.com/keithdickey207/secure-self-healing-orchestrator)** | Zero-trust LLM self-repair + FBI OSINT |
| **[newtons-alchemical-lab](https://github.com/keithdickey207/newtons-alchemical-lab)** | Historical chymistry CLI explorer |
| **[sovereign-sync](https://github.com/keithdickey207/sovereign-sync)** | Mesh glue — Syncthing, Tailscale, worktrees |
| **[dotfiles](https://github.com/keithdickey207/dotfiles)** | Multi-device bootstrap shell + env |
| **[goodperson](https://github.com/keithdickey207/goodperson)** | Good Person Protocol — daily practice CLI |

Sync mesh: Tailscale + Syncthing + git worktrees — see `~/SOVEREIGN_SYNC_QUICKSTART.md` and [sovereign-sync](https://github.com/keithdickey207/sovereign-sync).

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

MIT License — Copyright (c) 2026 Keith Dickey. See [LICENSE](LICENSE).

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Particularly valuable areas right now:
- Historical TLE / precise orbit reconstruction
- Better radiometric or atmospheric handling for early MSS
- Godot / Blender exporters
- More example locations and creative visualizations
- SGP4 / TLE ingestion for the live orbital daemon
- UDP/JSON feed from `orbital_daemon` → District 04901 Grid spatial layer

## Links

- **Repository**: https://github.com/keithdickey207/chronosat
- **Issues**: https://github.com/keithdickey207/chronosat/issues
- **Author**: https://github.com/keithdickey207

---

Built for historical research, creative visualization, and extending modern Earth observation pipelines into the past.
