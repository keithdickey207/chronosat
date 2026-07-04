#!/usr/bin/env python3
"""
WQSH Chronosat Orbital Daemon v0.1-alpha

Hardware-aware, zero-dependency orbital layer.
Circuit-compressed Keplerian catalog (~100x smaller than full ephemeris state).
Full SGP4 / high-fidelity propagation can load on demand later.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# WGS-84 / standard gravitational parameter (m^3/s^2)
MU_EARTH = 3.986004418e14
EARTH_RADIUS_M = 6_378_137.0
TWO_PI = 2.0 * math.pi
DEG = math.pi / 180.0


@dataclass(frozen=True)
class KeplerCircuit:
    """Minimal propagation circuit: six elements + mean motion + epoch."""

    norad_id: int
    name: str
    constellation: str
    a_m: float
    e: float
    i_deg: float
    raan_deg: float
    argp_deg: float
    M0_deg: float
    n_rev_per_day: float
    epoch_unix: float


# Curated demonstration catalog — compressed Keplerian parameters, not full TLE state.
CIRCUIT_CATALOG: tuple[KeplerCircuit, ...] = (
    KeplerCircuit(
        25544, "ISS (ZARYA)", "crewed", 6_791_000.0, 0.000183,
        51.64, 247.8, 130.5, 42.1, 15.49, 1_700_000_000.0,
    ),
    KeplerCircuit(
        20580, "HUBBLE", "science", 6_918_000.0, 0.00028,
        28.47, 120.3, 64.2, 198.4, 14.97, 1_700_000_000.0,
    ),
    KeplerCircuit(
        43013, "STARLINK-1007", "starlink", 6_925_000.0, 0.00012,
        53.0, 312.4, 88.1, 15.6, 14.95, 1_700_000_000.0,
    ),
    KeplerCircuit(
        44713, "STARLINK-2360", "starlink", 6_930_000.0, 0.00011,
        53.05, 18.7, 92.3, 201.2, 14.94, 1_700_000_000.0,
    ),
    KeplerCircuit(
        28474, "NOAA-18", "weather", 7_210_000.0, 0.0012,
        99.2, 45.6, 12.8, 88.4, 14.35, 1_700_000_000.0,
    ),
    KeplerCircuit(
        25994, "TERRA", "earth_obs", 7_073_000.0, 0.00015,
        98.2, 102.1, 78.4, 12.5, 14.57, 1_700_000_000.0,
    ),
    KeplerCircuit(
        28654, "AQUA", "earth_obs", 7_075_000.0, 0.00014,
        98.2, 88.3, 80.1, 44.2, 14.57, 1_700_000_000.0,
    ),
    KeplerCircuit(
        37849, "SUOMI NPP", "weather", 7_208_000.0, 0.00011,
        98.7, 210.4, 55.2, 130.8, 14.36, 1_700_000_000.0,
    ),
    KeplerCircuit(
        41866, "GOES-16", "geostationary", 42_164_000.0, 0.00008,
        0.05, 75.2, 180.0, 0.0, 1.0027, 1_700_000_000.0,
    ),
    KeplerCircuit(
        41891, "GOES-17", "geostationary", 42_165_000.0, 0.00007,
        0.04, 137.8, 180.0, 0.0, 1.0027, 1_700_000_000.0,
    ),
    KeplerCircuit(
        43001, "GPS III SV01", "navigation", 26_560_000.0, 0.005,
        55.0, 312.0, 45.0, 120.0, 2.0056, 1_700_000_000.0,
    ),
    KeplerCircuit(
        43873, "GPS III SV02", "navigation", 26_562_000.0, 0.0048,
        55.0, 88.0, 48.0, 200.0, 2.0055, 1_700_000_000.0,
    ),
)


def _solve_kepler(M: float, e: float, tol: float = 1e-10) -> float:
    """Newton-Raphson eccentric anomaly solver."""
    E = M if e < 0.8 else math.pi
    for _ in range(30):
        f = E - e * math.sin(E) - M
        fp = 1.0 - e * math.cos(E)
        dE = -f / fp
        E += dE
        if abs(dE) < tol:
            break
    return E


def _eci_position(circuit: KeplerCircuit, t_unix: float) -> tuple[float, float, float]:
    """Propagate Kepler circuit to ECI position (meters)."""
    dt = t_unix - circuit.epoch_unix
    n = circuit.n_rev_per_day * TWO_PI / 86400.0
    M = math.radians(circuit.M0_deg) + n * dt
    M = M % TWO_PI

    E = _solve_kepler(M, circuit.e)
    nu = 2.0 * math.atan2(
        math.sqrt(1.0 + circuit.e) * math.sin(E / 2.0),
        math.sqrt(1.0 - circuit.e) * math.cos(E / 2.0),
    )

    r = circuit.a_m * (1.0 - circuit.e * math.cos(E))
    x_p = r * math.cos(nu)
    y_p = r * math.sin(nu)

    i = circuit.i_deg * DEG
    raan = circuit.raan_deg * DEG
    argp = circuit.argp_deg * DEG

    cos_raan, sin_raan = math.cos(raan), math.sin(raan)
    cos_i, sin_i = math.cos(i), math.sin(i)
    cos_argp, sin_argp = math.cos(argp), math.sin(argp)

    # Perifocal -> ECI rotation (3-1-3 Euler)
    px = (cos_raan * cos_argp - sin_raan * sin_argp * cos_i) * x_p
    py = (sin_raan * cos_argp + cos_raan * sin_argp * cos_i) * x_p
    pz = (sin_argp * sin_i) * x_p

    qx = (-cos_raan * sin_argp - sin_raan * cos_argp * cos_i) * y_p
    qy = (-sin_raan * sin_argp + cos_raan * cos_argp * cos_i) * y_p
    qz = (cos_argp * sin_i) * y_p

    return px + qx, py + qy, pz + qz


def _eci_velocity(circuit: KeplerCircuit, t_unix: float) -> tuple[float, float, float]:
    """Finite-difference velocity estimate (m/s) — adequate for visualization."""
    dt = 1.0
    x0, y0, z0 = _eci_position(circuit, t_unix - dt)
    x1, y1, z1 = _eci_position(circuit, t_unix + dt)
    return (x1 - x0) / (2 * dt), (y1 - y0) / (2 * dt), (z1 - z0) / (2 * dt)


def propagate_catalog(
    catalog: Iterable[KeplerCircuit],
    t_unix: float | None = None,
) -> dict:
    """Build compressed JSON export for the orbital layer."""
    t_unix = t_unix or time.time()
    ts = datetime.fromtimestamp(t_unix, tz=timezone.utc).isoformat()

    satellites = []
    for c in catalog:
        x, y, z = _eci_position(c, t_unix)
        vx, vy, vz = _eci_velocity(c, t_unix)
        r = math.sqrt(x * x + y * y + z * z)
        alt_km = (r - EARTH_RADIUS_M) / 1000.0
        v = math.sqrt(vx * vx + vy * vy + vz * vz)

        satellites.append({
            "norad_id": c.norad_id,
            "name": c.name,
            "constellation": c.constellation,
            "circuit": {
                "a_m": c.a_m,
                "e": c.e,
                "i_deg": c.i_deg,
                "raan_deg": c.raan_deg,
                "argp_deg": c.argp_deg,
                "M0_deg": c.M0_deg,
                "n_rev_per_day": c.n_rev_per_day,
            },
            "eci_m": {"x": round(x, 1), "y": round(y, 1), "z": round(z, 1)},
            "eci_km": {
                "x": round(x / 1000, 3),
                "y": round(y / 1000, 3),
                "z": round(z / 1000, 3),
            },
            "velocity_m_s": round(v, 1),
            "altitude_km": round(alt_km, 2),
        })

    return {
        "schema": "chronosat.v0.1",
        "generated_at": ts,
        "generated_unix": t_unix,
        "frame": "ECI",
        "earth_radius_km": EARTH_RADIUS_M / 1000.0,
        "satellite_count": len(satellites),
        "compression": "keplerian_circuit",
        "satellites": satellites,
    }


def write_export(payload: dict, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return output_path


def run_once(output: Path) -> Path:
    payload = propagate_catalog(CIRCUIT_CATALOG)
    return write_export(payload, output)


def run_watch(output: Path, interval_s: float) -> None:
    print(f"Chronosat v0.1-alpha watching — writing {output} every {interval_s}s")
    try:
        while True:
            path = run_once(output)
            print(f"[{datetime.now(timezone.utc).isoformat()}] {path} ({path.stat().st_size} bytes)")
            time.sleep(interval_s)
    except KeyboardInterrupt:
        print("\nStopped.")


def main() -> None:
    parser = argparse.ArgumentParser(description="WQSH Chronosat Orbital Daemon v0.1-alpha")
    parser.add_argument(
        "-o", "--output",
        default="output/orbital_positions.json",
        help="JSON export path (default: output/orbital_positions.json)",
    )
    parser.add_argument(
        "-w", "--watch",
        type=float,
        metavar="SECONDS",
        help="Continuous mode: refresh export every N seconds",
    )
    parser.add_argument(
        "--list-circuits",
        action="store_true",
        help="Print compressed circuit catalog and exit",
    )
    args = parser.parse_args()

    if args.list_circuits:
        for c in CIRCUIT_CATALOG:
            print(json.dumps(asdict(c)))
        return

    output = Path(args.output)
    if args.watch:
        run_watch(output, args.watch)
    else:
        path = run_once(output)
        print(f"Exported {path} ({path.stat().st_size} bytes, {len(CIRCUIT_CATALOG)} satellites)")


if __name__ == "__main__":
    main()
