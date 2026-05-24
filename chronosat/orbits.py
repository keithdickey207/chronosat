"""
chronosat.orbits
Simple historical orbit / coverage prediction for early Landsat-era satellites.

Early Landsat (1-3) flew in sun-synchronous orbits with an 18-day repeat cycle.
This module provides lightweight date + location pass estimation without needing
full TLE propagation (use skyfield/sgp4 for higher fidelity later).

For true historical reconstruction, feed actual TLEs from the era into skyfield.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from math import fmod
from typing import List, Tuple

from .missions import Mission, get_active_missions


# Approximate orbital parameters for first-generation Landsat
LANDSAT_ORBIT = {
    "altitude_km": 917,
    "inclination_deg": 99.1,      # near-polar sun-synchronous
    "period_minutes": 103.0,      # ~103 min per orbit
    "descending_node_local_time": "09:30-10:00",  # morning descending node
}


@dataclass
class PassWindow:
    mission: str
    date: date
    approx_utc: str          # rough time of closest approach (UTC)
    direction: str           # "descending" or "ascending"
    quality_note: str


def estimate_landsat_passes(
    target_lat: float,
    target_lon: float,
    on_date: date,
    missions: List[Mission] | None = None,
) -> List[PassWindow]:
    """
    Very rough estimate of when a Landsat 1-3 class satellite might have been
    over (or near) a target location on a given date.

    This uses the known 18-day repeat cycle + simplified orbital geometry.
    It is **not** precise ephemeris — good for "was there coverage possible?"
    and for timeline visualization.

    Real historical passes require archived TLEs + propagator (skyfield + de421).
    """
    if missions is None:
        missions = get_active_missions(on_date)

    landsat_missions = [m for m in missions if "Landsat" in m.name]
    results: List[PassWindow] = []

    # The 18-day repeat cycle means the ground track repeats every 18 days.
    # We compute a pseudo "phase" of the cycle using a fixed epoch.
    # Landsat 1 epoch for this simulation: 1972-07-23 (launch)
    epoch = date(1972, 7, 23)
    days_since_epoch = (on_date - epoch).days
    cycle_day = int(fmod(days_since_epoch, 18))
    if cycle_day < 0:
        cycle_day += 18

    for m in landsat_missions:
        # Very crude longitude-based time-of-day offset for descending node
        # (morning pass roughly 9:30-10:00 local at equator, shifts with latitude)
        # For demonstration we synthesize a plausible UTC window.
        base_hour = 14 + (target_lon / 15.0)   # rough UTC conversion from local solar
        base_hour = (base_hour + 24) % 24

        # Adjust slightly by cycle phase (different path on different cycle days)
        offset_minutes = (cycle_day * 7) % 60   # spreads passes across the day window
        hour = int(base_hour)
        minute = int(offset_minutes)

        approx_time = f"{hour:02d}:{minute:02d} UTC (approx)"

        # Quality heuristic
        if abs(target_lat) > 70:
            quality = "polar region — limited or oblique coverage likely"
        elif cycle_day in (0, 1, 8, 9, 17):
            quality = "good chance of near-nadir pass on this cycle day"
        else:
            quality = "possible side-lap or adjacent path coverage"

        results.append(
            PassWindow(
                mission=m.short_name,
                date=on_date,
                approx_utc=approx_time,
                direction="descending (typical morning pass)",
                quality_note=quality,
            )
        )

    # Skylab was not sun-synchronous and had limited crewed periods
    sk = next((m for m in missions if m.short_name == "Skylab"), None)
    if sk:
        results.append(
            PassWindow(
                mission="Skylab (EREP)",
                date=on_date,
                approx_utc="variable (manned periods only)",
                direction="non sun-sync",
                quality_note="Skylab passes were not systematic. Earth photography "
                             "occurred during crewed missions (primarily 1973-1974). "
                             "Coverage was opportunistic rather than global repeat.",
            )
        )

    return results


def get_coverage_summary(lat: float, lon: float, on_date: date) -> str:
    """Human-readable summary for a location + date."""
    passes = estimate_landsat_passes(lat, lon, on_date)
    active = get_active_missions(on_date)

    lines = [
        f"Location: {lat:.4f}, {lon:.4f}",
        f"Date: {on_date.isoformat()}",
        f"Active NASA EO assets that day: {', '.join(m.short_name for m in active) or 'None'}",
        "",
        "Estimated overpass opportunities:",
    ]
    for p in passes:
        lines.append(
            f"  • {p.mission}: ~{p.approx_utc}  [{p.direction}] — {p.quality_note}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    # Waterville, Maine example (matches user's existing pipelines)
    print(get_coverage_summary(44.55, -69.63, date(1975, 6, 14)))
    print()
    print(get_coverage_summary(44.55, -69.63, date(1979, 8, 20)))