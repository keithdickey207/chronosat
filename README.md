# chronosat

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/keithdickey207/chronosat/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![GitHub](https://img.shields.io/badge/GitHub-keithdickey207/chronosat-181717?logo=github)](https://github.com/keithdickey207/chronosat)

**NASA Earth observation history (1970–1981) for mapping and 3D visualization.**

Query and reconstruct what Landsat 1–3 and Skylab EREP satellites saw over any location on Earth during the earliest years of civilian satellite remote sensing.

> **Important**: This is strictly historical/archival data. There are no live feeds from 1975.

---

## Features

- Authoritative mission timeline for Landsat 1, 2, 3 and Skylab (1972–1981)
- Lightweight 18-day repeat cycle pass estimation for any lat/lon + date
- Simulation catalog (works offline immediately)
- Google Earth Engine integration path for real historical MSS imagery
- Designed to plug directly into modern 3D pipelines (PyVista, Godot, etc.)

## Quick Start

```bash
git clone https://github.com/keithdickey207/chronosat.git
cd chronosat

# Explore missions
python3 cli.py missions

# What was flying over a location on a specific historical date?
python3 cli.py coverage --lat 44.55 --lon -69.63 --date 1975-06-14

# Search for coverage windows (simulation mode)
python3 cli.py search --lat 44.55 --lon -69.63 --start 1975-01-01 --end 1975-12-31
```

## Installation

```bash
pip install -e .
```

Optional extras:

```bash
pip install -e ".[gee]"      # Google Earth Engine support
pip install -e ".[viz]"      # PyVista + rasterio pipeline helpers
```

## Real Historical Data (Google Earth Engine)

The most complete source for 1972–1981 Landsat MSS data:

```bash
pip install earthengine-api
earthengine authenticate
```

Then run searches against real data:

```bash
python3 cli.py search --lat 44.55 --lon -69.63 --start 1975-06-01 --end 1975-06-30 --real
```

## Integration With Your Workflows

This project was built to extend existing modern satellite + 3D pipelines:

- Use `chronosat` to discover historically interesting dates
- Export real MSS scenes via Google Earth Engine
- Feed them into adapted versions of your NAIP/PyVista mesh pipelines
- Generate 1975 vs 2025 comparison renders or time-lapse sequences

The orbit module can be upgraded with real historical TLEs using Skyfield + your existing `de421.bsp`.

## Repository Structure

```
chronosat/
├── chronosat/
│   ├── __init__.py
│   ├── missions.py      # Mission facts & timeline
│   ├── orbits.py        # Pass estimation
│   └── catalog.py       # Simulation + GEE data access
├── cli.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

## License

MIT License © 2026 [Keith Dickey](https://github.com/keithdickey207)

See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please open an issue or pull request on GitHub.

Ideas for future work:
- Full Google Earth Engine scene export helpers
- Historical mesh generation pipeline (MSS radiometry)
- Skyfield-based precise orbit reconstruction using archived TLEs
- Godot exporter for time-travel visualization sequences
- Web timeline UI

## Links

- **Repository**: https://github.com/keithdickey207/chronosat
- **Issues**: https://github.com/keithdickey207/chronosat/issues
- **Author**: https://github.com/keithdickey207

---

Built for historical Earth observation research and creative 3D visualization projects.