#!/usr/bin/env python3
"""
chronosat CLI — Query NASA Earth observation history 1970-1981

Usage examples:
    python cli.py missions
    python cli.py coverage --lat 44.55 --lon -69.63 --date 1975-06-14
    python cli.py search --lat 44.55 --lon -69.63 --start 1974-01-01 --end 1974-12-31
    python cli.py search --lat 44.55 --lon -69.63 --start 1974-01-01 --end 1974-12-31 --real
"""

import argparse
from datetime import datetime
from chronosat.missions import print_mission_timeline, get_active_missions
from chronosat.orbits import get_coverage_summary
from chronosat.catalog import get_catalog


def cmd_missions(_args):
    print_mission_timeline()


def cmd_coverage(args):
    d = datetime.strptime(args.date, "%Y-%m-%d").date()
    print(get_coverage_summary(args.lat, args.lon, d))


def cmd_search(args):
    start = datetime.strptime(args.start, "%Y-%m-%d").date()
    end = datetime.strptime(args.end, "%Y-%m-%d").date()

    mode = "gee" if args.real else "simulation"
    cat = get_catalog(mode)

    print(f"Searching {mode.upper()} catalog for {args.lat}, {args.lon}")
    print(f"Window: {start} → {end}  (max cloud {args.max_cloud}%)")
    print()

    scenes = cat.search(args.lat, args.lon, start, end, max_cloud=args.max_cloud)

    if not scenes:
        print("No scenes returned (simulation mode may be sparse, or GEE returned empty).")
        return

    for s in scenes[:20]:   # limit output
        print(f"{s.acquisition_date}  {s.mission:12s}  p/s {s.path:03d}/{s.row:03d}  "
              f"cloud~{s.cloud_cover or '?'}%   {s.sensor}  {s.notes[:40]}")

    print(f"\nTotal scenes found: {len(scenes)}")


def main():
    parser = argparse.ArgumentParser(
        description="chronosat — NASA 1970-1981 Earth observation history and mapping tools"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # missions
    p = sub.add_parser("missions", help="Print full mission timeline and sensor details")
    p.set_defaults(func=cmd_missions)

    # coverage
    p = sub.add_parser("coverage", help="Show estimated satellite passes for a location + date")
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--date", required=True, help="YYYY-MM-DD")
    p.set_defaults(func=cmd_coverage)

    # search
    p = sub.add_parser("search", help="Search for historical scenes (simulation or real GEE)")
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--start", required=True, help="YYYY-MM-DD")
    p.add_argument("--end", required=True, help="YYYY-MM-DD")
    p.add_argument("--max-cloud", type=float, default=30.0)
    p.add_argument("--real", action="store_true",
                   help="Use real Google Earth Engine (requires prior 'earthengine authenticate')")
    p.set_defaults(func=cmd_search)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()