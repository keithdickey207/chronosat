# Changelog

All notable changes to chronosat will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **WQSH Orbital Daemon v0.1-alpha** (`orbital_daemon/`)
  - Zero-dependency stdlib Python Keplerian circuit propagation
  - JSON export (`chronosat.v0.1` schema) for sovereign stack integration
  - Godot 4.3 viewer (`orbital_daemon/godot/chronosat_viewer/`)
  - One-command demo script (`orbital_daemon/run_demo.sh`)
- Real Google Earth Engine integration (`chronosat/gee.py`)
  - `search_real_scenes()` across Landsat 1–3 MSS collections
  - `export_to_drive()` for practical GeoTIFF exports
- Three high-quality example scripts in `examples/`
- `CONTRIBUTING.md`
- `CHANGELOG.md`
- Professional open source packaging (`pyproject.toml`, `.gitignore`, LICENSE)

### Changed
- Significantly improved README with badges, installation instructions, and workflow integration guidance

## [0.1.0] - 2026-05

### Added
- Initial public release
- Core mission database (Landsat 1–3 + Skylab 1972–1981)
- Lightweight 18-day repeat cycle orbit/pass estimation
- Simulation catalog for offline historical timeline queries
- CLI (`chronosat` / `cli.py`) with `missions`, `coverage`, and `search` commands
- MIT License
- Public GitHub repository: https://github.com/keithdickey207/chronosat
