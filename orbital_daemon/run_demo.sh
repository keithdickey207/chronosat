#!/usr/bin/env bash
# Tonight's demo — one command on Red HP or any house node
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "=== Chronosat v0.1-alpha demo ==="
python3 chronosat_daemon.py -o output/orbital_positions.json
echo ""
echo "JSON ready: $ROOT/output/orbital_positions.json"
echo ""
echo "Next steps:"
echo "  1. Open godot/chronosat_viewer/ in Godot 4.3+ and press Play"
echo "  2. Or: python3 chronosat_daemon.py -w 2   (live refresh)"
echo "  3. Record 60–90s of the running twin — outputs only, no source"
