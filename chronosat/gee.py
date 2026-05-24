"""
chronosat.gee
Practical Google Earth Engine helpers for real 1970-1981 Landsat MSS data.

This module provides the bridge from simulation → real historical imagery.

Requirements:
    pip install earthengine-api

One-time setup:
    earthengine authenticate

Collections used (Collection 2, Level 1):
    - LANDSAT/LM01/C02/T1   (Landsat 1 MSS)
    - LANDSAT/LM02/C02/T1   (Landsat 2 MSS)
    - LANDSAT/LM03/C02/T1   (Landsat 3 MSS)

Typical usage:
    from chronosat.gee import search_real_scenes, export_to_drive

    scenes = search_real_scenes(44.55, -69.63, "1975-06-01", "1975-06-20")
    task = export_to_drive(scenes[0], folder="chronosat_exports")
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import date
from typing import List, Optional, Dict, Any
import time

try:
    import ee
except ImportError:
    ee = None


@dataclass
class RealScene:
    """Clean representation of a real historical Landsat MSS scene."""
    id: str
    mission: str
    acquisition_date: str
    path: int
    row: int
    cloud_cover: float
    collection: str
    geometry: Optional[Dict] = None
    bands: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GEEAuthError(RuntimeError):
    """Raised when GEE is not initialized or authentication fails."""
    pass


def _ensure_ee() -> None:
    """Initialize Earth Engine if not already done."""
    if ee is None:
        raise ImportError(
            "earthengine-api is not installed. Run: pip install earthengine-api"
        )
    try:
        ee.Initialize()
    except Exception as e:
        raise GEEAuthError(
            "Google Earth Engine not initialized.\n"
            "Run this once in your terminal:\n"
            "    earthengine authenticate\n"
            f"Original error: {e}"
        ) from e


def search_real_scenes(
    lat: float,
    lon: float,
    start: str | date,
    end: str | date,
    max_cloud: float = 40.0,
    limit: int = 20,
) -> List[RealScene]:
    """
    Search real Landsat 1-3 MSS scenes on Google Earth Engine.

    Returns a list of RealScene objects sorted by cloud cover (best first).
    """
    _ensure_ee()

    if isinstance(start, date):
        start = start.isoformat()
    if isinstance(end, date):
        end = end.isoformat()

    point = ee.Geometry.Point([lon, lat])

    collections = [
        ("LANDSAT/LM01/C02/T1", "Landsat 1"),
        ("LANDSAT/LM02/C02/T1", "Landsat 2"),
        ("LANDSAT/LM03/C02/T1", "Landsat 3"),
    ]

    all_scenes: List[RealScene] = []

    for collection_id, mission_name in collections:
        try:
            coll = (
                ee.ImageCollection(collection_id)
                .filterBounds(point)
                .filterDate(start, end)
                .filter(ee.Filter.lt("CLOUD_COVER", max_cloud))
                .sort("CLOUD_COVER")
                .limit(limit)
            )

            features = coll.getInfo().get("features", [])

            for feat in features:
                props = feat.get("properties", {})
                scene = RealScene(
                    id=props.get("system:index", "unknown"),
                    mission=mission_name,
                    acquisition_date=props.get("DATE_ACQUIRED", props.get("system:time_start")),
                    path=props.get("WRS_PATH", props.get("path", 0)),
                    row=props.get("WRS_ROW", props.get("row", 0)),
                    cloud_cover=round(props.get("CLOUD_COVER", 99.0), 1),
                    collection=collection_id,
                    bands=["B4", "B5", "B6", "B7"] if "LM0" in collection_id else ["B1", "B2", "B3", "B4"],
                )
                all_scenes.append(scene)

        except Exception as e:
            print(f"[GEE] Warning: Could not query {collection_id}: {e}")
            continue

    # Sort by cloud cover (lowest first)
    all_scenes.sort(key=lambda s: s.cloud_cover)
    return all_scenes[:limit]


def export_to_drive(
    scene: RealScene | str,
    folder: str = "chronosat_exports",
    scale: int = 60,
    region_buffer_km: float = 15.0,
    wait: bool = False,
) -> Dict[str, Any]:
    """
    Export a historical Landsat MSS scene to Google Drive as GeoTIFF.

    Args:
        scene: A RealScene object (from search_real_scenes) or a GEE image ID string.
        folder: Google Drive folder name.
        scale: Export resolution in meters (60m is a good default for MSS).
        region_buffer_km: How far around the scene center to export.
        wait: If True, block until the export finishes (can take minutes).

    Returns:
        Dict with task info and status.
    """
    _ensure_ee()

    if isinstance(scene, str):
        image = ee.Image(f"LANDSAT/{scene}") if not scene.startswith("LANDSAT/") else ee.Image(scene)
        scene_id = scene
    else:
        image = ee.Image(f"{scene.collection}/{scene.id}")
        scene_id = scene.id

    try:
        geometry = image.geometry().buffer(region_buffer_km * 1000)
    except Exception:
        geometry = None

    task = ee.batch.Export.image.toDrive(
        image=image.select(["B4", "B5", "B6", "B7"]).toFloat(),
        description=f"chronosat_{scene_id.replace('/', '_')}",
        folder=folder,
        fileNamePrefix=f"chronosat_{scene_id.replace('/', '_')}",
        scale=scale,
        region=geometry,
        maxPixels=1e9,
        fileFormat="GeoTIFF",
    )

    task.start()

    result = {
        "task_id": task.id,
        "description": task.config.get("description"),
        "folder": folder,
        "status": "STARTED",
        "scene_id": scene_id,
    }

    if wait:
        print(f"[GEE] Export started. Waiting for completion (this can take several minutes)...")
        while True:
            status = task.status()
            state = status.get("state")
            if state in ("COMPLETED", "FAILED", "CANCELLED"):
                result["status"] = state
                result["details"] = status
                break
            time.sleep(15)

    return result


def print_scene_summary(scenes: List[RealScene]) -> None:
    """Pretty print a list of RealScene objects."""
    if not scenes:
        print("No real scenes found.")
        return

    print(f"\nFound {len(scenes)} real historical scenes (sorted by cloud cover):\n")
    print(f"{'Date':<12} {'Mission':<12} {'Cloud%':>7} {'Path/Row':>9} {'Collection'}")
    print("-" * 65)
    for s in scenes:
        print(
            f"{s.acquisition_date:<12} "
            f"{s.mission:<12} "
            f"{s.cloud_cover:>6.1f}% "
            f"{s.path:>3d}/{s.row:<3d}   "
            f"{s.collection}"
        )


# Convenience function for the CLI
def search_and_print_real(lat: float, lon: float, start: str, end: str, max_cloud: float = 40.0):
    scenes = search_real_scenes(lat, lon, start, end, max_cloud=max_cloud)
    print_scene_summary(scenes)
    return scenes