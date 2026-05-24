"""
chronosat.missions
Authoritative knowledge base for NASA Earth observation missions active 1970-1981.

Sources: NASA, USGS Landsat program history, CEOS, historical mission documentation.
"""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class Mission:
    name: str
    short_name: str
    launch: date
    end: date
    orbit_type: str          # "sun-synchronous", "low-earth", etc.
    repeat_cycle_days: Optional[int]
    sensors: List[str]
    resolution_m: Optional[int]   # nominal ground resolution (best band)
    notes: str


MISSIONS: List[Mission] = [
    Mission(
        name="Landsat 1 (ERTS-1)",
        short_name="Landsat 1",
        launch=date(1972, 7, 23),
        end=date(1978, 1, 6),
        orbit_type="sun-synchronous",
        repeat_cycle_days=18,
        sensors=["MSS (Multispectral Scanner)"],
        resolution_m=80,
        notes="First civilian Earth resources satellite. 4-band MSS (0.5-1.1 μm). "
              "Established the 18-day repeat cycle still used in spirit by the program."
    ),
    Mission(
        name="Skylab",
        short_name="Skylab",
        launch=date(1973, 5, 14),
        end=date(1979, 7, 11),
        orbit_type="low-earth (non sun-sync)",
        repeat_cycle_days=None,   # manned station, variable coverage during crewed periods
        sensors=["EREP (Earth Resources Experiment Package)", "Multispectral Camera", "S-190A/B"],
        resolution_m=30,          # S-190B high-res camera ~30-40m in some modes
        notes="First US space station. EREP included visible, IR, and microwave sensors. "
              "Crewed missions: 1973-1974 (3 crews). Earth photography + experimental sensors. "
              "Deorbited 1979."
    ),
    Mission(
        name="Landsat 2",
        short_name="Landsat 2",
        launch=date(1975, 1, 22),
        end=date(1982, 2, 25),
        orbit_type="sun-synchronous",
        repeat_cycle_days=18,
        sensors=["MSS (Multispectral Scanner)"],
        resolution_m=80,
        notes="Identical instrument complement to Landsat 1. Provided crucial continuity "
              "during the early program years."
    ),
    Mission(
        name="Landsat 3",
        short_name="Landsat 3",
        launch=date(1978, 3, 5),
        end=date(1983, 3, 31),
        orbit_type="sun-synchronous",
        repeat_cycle_days=18,
        sensors=["MSS (Multispectral Scanner)", "RBV (Return Beam Vidicon)", "thermal band (experimental)"],
        resolution_m=80,  # MSS; RBV attempted higher res in places
        notes="Added experimental thermal channel (failed early). RBV provided some higher "
              "resolution panchromatic-style imagery. Last of the first-generation MSS satellites."
    ),
]


def get_active_missions(on_date: date) -> List[Mission]:
    """Return all missions that were operational (launched and not yet ended) on the given date."""
    return [
        m for m in MISSIONS
        if m.launch <= on_date <= m.end
    ]


def get_missions_in_range(start: date, end: date) -> List[Mission]:
    """Return missions that had any overlap with the date range."""
    return [
        m for m in MISSIONS
        if not (m.end < start or m.launch > end)
    ]


def describe_mission(m: Mission) -> str:
    cycle = f"{m.repeat_cycle_days}-day repeat" if m.repeat_cycle_days else "no fixed repeat (manned)"
    res = f"{m.resolution_m}m" if m.resolution_m else "variable"
    return (
        f"{m.name} ({m.short_name})\n"
        f"  Launch: {m.launch}   End: {m.end}\n"
        f"  Orbit: {m.orbit_type}  |  Repeat: {cycle}\n"
        f"  Sensors: {', '.join(m.sensors)}\n"
        f"  Nominal resolution: {res}\n"
        f"  {m.notes}\n"
    )


def print_mission_timeline():
    print("NASA Earth Observation Missions 1970–1981\n")
    for m in sorted(MISSIONS, key=lambda x: x.launch):
        print(describe_mission(m))
        print("-" * 60)


if __name__ == "__main__":
    print_mission_timeline()
    print("\nExample: Active on 1976-09-14")
    for m in get_active_missions(date(1976, 9, 14)):
        print(f"  - {m.short_name}")