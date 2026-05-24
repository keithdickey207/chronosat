"""
chronosat.catalog
Data access layer for historical (1970-1981) NASA satellite imagery.

Current reality (2026):
- True "real-time" is impossible — these are archival datasets only.
- Most complete programmatic access: Google Earth Engine (Landsat MSS Collection 2)
- Alternative: USGS EarthExplorer M2M API (requires free account)
- Microsoft Planetary Computer: limited or no easy STAC access for pre-1982 MSS
- Many early scenes exist only as raw or minimally processed products.

This module provides:
  - Abstract interface
  - Google Earth Engine stub (recommended path)
  - Guidance for USGS M2M
  - Fallback "simulation / known scene list" mode for offline use
"""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Protocol


@dataclass
class Scene:
    id: str
    mission: str
    acquisition_date: date
    path: int
    row: int
    cloud_cover: Optional[float]
    asset_url: Optional[str]          # direct download or GEE export link
    thumbnail_url: Optional[str]
    sensor: str
    notes: str = ""


class HistoricalCatalog(Protocol):
    def search(
        self,
        lat: float,
        lon: float,
        start: date,
        end: date,
        max_cloud: float = 30.0,
    ) -> List[Scene]:
        ...


class SimulationCatalog:
    """
    Offline mode. Uses the orbit estimator to synthesize plausible scene metadata
    without network calls. Useful for timeline visualization and Godot integration
    planning before you authenticate to real data sources.
    """

    def search(
        self,
        lat: float,
        lon: float,
        start: date,
        end: date,
        max_cloud: float = 30.0,
    ) -> List[Scene]:
        from .orbits import estimate_landsat_passes
        from .missions import get_missions_in_range

        missions = get_missions_in_range(start, end)
        scenes: List[Scene] = []

        current = start
        while current <= end:
            passes = estimate_landsat_passes(lat, lon, current, missions=missions)
            for p in passes:
                if "Landsat" in p.mission:
                    # Fabricate a plausible WRS-1 path/row (early Landsat used WRS-1)
                    # Rough mapping for demo purposes only
                    path = int((lon + 180) / 5) % 251 + 1
                    row = int((lat + 90) / 3) % 248 + 1

                    scenes.append(
                        Scene(
                            id=f"{p.mission.replace(' ', '')}_{current.strftime('%Y%m%d')}_{path:03d}{row:03d}",
                            mission=p.mission,
                            acquisition_date=current,
                            path=path,
                            row=row,
                            cloud_cover=15.0,   # fake typical value
                            asset_url=None,
                            thumbnail_url=None,
                            sensor="MSS",
                            notes="SIMULATED — based on 18-day repeat cycle. "
                                  "Not a real scene ID. Use for planning/visualization only.",
                        )
                    )
            current += __import__("datetime").timedelta(days=1)

        return scenes


class GoogleEarthEngineCatalog:
    """
    Recommended path for real data.

    Requires:
        pip install earthengine-api
        earthengine authenticate   (one-time, opens browser)

    Collection examples (Collection 2, Level 1):
        "LANDSAT/LM01/C02/T1"   # Landsat 1 MSS
        "LANDSAT/LM02/C02/T1"
        "LANDSAT/LM03/C02/T1"

    Once authenticated, you can export GeoTIFFs, compute indices, etc.
    """

    def __init__(self):
        self._ee = None

    def _init_ee(self):
        if self._ee is not None:
            return
        try:
            import ee
            ee.Initialize()
            self._ee = ee
        except Exception as e:
            raise RuntimeError(
                "Google Earth Engine not available or not authenticated.\n"
                "Install: pip install earthengine-api\n"
                "Authenticate: earthengine authenticate\n"
                f"Original error: {e}"
            ) from e

    def search(
        self,
        lat: float,
        lon: float,
        start: date,
        end: date,
        max_cloud: float = 30.0,
    ) -> List[Scene]:
        self._init_ee()
        ee = self._ee

        # Build a point geometry
        point = ee.Geometry.Point([lon, lat])

        # We would normally search multiple collections and merge.
        # For brevity here we demonstrate the pattern with one collection.
        # In production you would union results from LM01/LM02/LM03.
        collection = (
            ee.ImageCollection("LANDSAT/LM01/C02/T1")
            .filterBounds(point)
            .filterDate(start.isoformat(), end.isoformat())
            .filter(ee.Filter.lt("CLOUD_COVER", max_cloud))
        )

        # This is a skeleton — real usage would map over features and pull metadata
        # then construct Scene objects.
        # For now we return an empty list to indicate "real implementation goes here".
        # The pattern is well documented in the GEE Python docs.
        print("[GEE] Real search executed (stub). Implement full mapping in production.")
        return []


def get_catalog(mode: str = "simulation") -> HistoricalCatalog:
    if mode == "gee":
        return GoogleEarthEngineCatalog()
    return SimulationCatalog()


if __name__ == "__main__":
    from datetime import date

    cat = get_catalog("simulation")
    scenes = cat.search(44.55, -69.63, date(1975, 6, 1), date(1975, 6, 20))
    for s in scenes[:5]:
        print(f"{s.acquisition_date} | {s.mission} | path/row {s.path:03d}/{s.row:03d} | {s.notes[:50]}...")
    print(f"\nTotal simulated scenes in window: {len(scenes)}")