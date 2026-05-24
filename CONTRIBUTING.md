""# Contributing to chronosat

Thank you for your interest in contributing to chronosat — the open source toolkit for NASA Earth observation history (1970–1981).

We welcome contributions of all sizes: bug reports, documentation improvements, new features, example scripts, and integration code for visualization pipelines.

## Code of Conduct

Be respectful, constructive, and inclusive. This is a small historical + creative visualization project.

## How to Contribute

### Reporting Issues

- Use the [GitHub Issues](https://github.com/keithdickey207/chronosat/issues) page.
- For bugs, please include:
  - Python version
  - Exact command or code that failed
  - Full error traceback
  - Whether you are using simulation mode or real Google Earth Engine

### Suggesting Features

We are especially interested in:

- Better historical orbit / TLE reconstruction (using Skyfield + archived elements)
- Atmospheric correction or radiometric calibration helpers for early MSS data
- Godot / Blender exporters for time-lapse historical visualization
- Integration examples with QGIS, Blender, or other 3D tools
- Web UI / dashboard for timeline exploration

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-cool-thing`)
3. Make your changes
4. Add or update tests/examples if applicable
5. Update documentation (README or docstrings)
6. Submit a Pull Request

We prefer small, focused PRs when possible.

### Development Setup

```bash
git clone https://github.com/keithdickey207/chronosat.git
cd chronosat
pip install -e ".[full]"
```

Optional but recommended for full development:
- `earthengine-api` + authenticated account (for real data work)
- `pyvista`, `rasterio`, `planetary-computer` (for mesh pipeline examples)

### Coding Style

- Keep the code readable and well-commented.
- Prefer practical, working examples over theoretical perfection.
- Historical accuracy matters — when in doubt, cite sources in comments.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Open an issue or reach out to the maintainer via GitHub.

Thank you for helping preserve and visualize early satellite Earth observation history!""