# WQSH Chronosat Orbital Daemon v0.1-alpha

Zero-dependency, hardware-aware **live** orbital layer for the sovereign stack.
Complements the historical Landsat tooling in the parent `chronosat` package.

## Quick start

```bash
cd orbital_daemon
bash run_demo.sh
# → output/orbital_positions.json

# Continuous refresh (for Godot twin)
python3 chronosat_daemon.py -w 2
```

## Godot viewer

Open `godot/chronosat_viewer/` in Godot 4.3+, press Play.
Default JSON path: `../../output/orbital_positions.json`.

## Design

- **Circuit compression:** Keplerian parameter circuits, not full ephemeris state vectors (~100× smaller than full state)
- **100% stdlib Python:** runs on Penguin, Red Laptop, Synology, air-gapped nodes
- **On-demand fidelity:** SGP4 / high-fidelity propagation hooks reserved for v0.2+

## License

MIT — Keith Dickey / District 04901
