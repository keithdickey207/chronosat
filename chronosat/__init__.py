"""
chronosat — NASA Earth Observation 1970-1981 Historical Mapping Toolkit

Built to extend your existing Landsat/NAIP + PyVista + Godot pipelines
with the earliest civilian satellite Earth observation record.

GitHub: https://github.com/keithdickey207/chronosat
"""

from .missions import (
    Mission,
    MISSIONS,
    get_active_missions,
    get_missions_in_range,
    describe_mission,
)
from .orbits import estimate_landsat_passes, get_coverage_summary, PassWindow
from .catalog import Scene, get_catalog, SimulationCatalog, GoogleEarthEngineCatalog

__version__ = "0.2.0"
__all__ = [
    "Mission", "MISSIONS", "get_active_missions", "get_missions_in_range",
    "estimate_landsat_passes", "get_coverage_summary", "PassWindow",
    "Scene", "get_catalog", "SimulationCatalog", "GoogleEarthEngineCatalog",
]