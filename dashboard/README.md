""# Chronosat Dashboard

Real-time web dashboard for the Chronosat project with role-based access control.

## Features

- **Basic Users**: Interactive historical queries, live 1970s satellite simulator, personal activity history, real GEE data search
- **Admin Users**: All basic features + user management, system-wide activity logs, ability to create new accounts
- **Real-time**: WebSocket-powered live satellite pass simulator (updates every few seconds)

## Running the Dashboard

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn python-multipart
   ```

2. (Optional but recommended) Install the full chronosat package:
   ```bash
   pip install -e .
   ```

3. Start the server:
   ```bash
   cd dashboard
   uvicorn app:app --reload --port 8000
   ```

4. Open http://localhost:8000

**Default login**:
- Username: `admin`
- Password: `admin123`

**Important**: Change the default admin password in production.

## Architecture

- `app.py` — FastAPI backend + WebSocket real-time simulator
- `database.py` — SQLite user management + query logging
- `templates/dashboard.html` — Rich single-page dashboard (Tailwind + Leaflet + vanilla JS)

The live simulator uses the existing `chronosat.orbits` logic to show plausible 1970s passes in real time.

## Next Improvements

- Persistent GEE export task monitoring
- Better historical orbit propagation with Skyfield
- Godot embedding / 3D viewer links
- Rate limiting + proper password hashing

This dashboard was built as a direct extension of the core chronosat library.""