"""
Chronosat Real-Time Dashboard
FastAPI application with role-based access (basic / admin) and live WebSocket features.

Run with:
    cd dashboard
    uvicorn app:app --reload --port 8000
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import secrets
import asyncio
from datetime import datetime, date
from typing import List
import json

from .database import (
    init_db, authenticate_user, get_user_by_id, create_user,
    list_all_users, log_query, get_user_query_history, get_all_query_logs
)
from chronosat.missions import get_active_missions, MISSIONS
from chronosat.orbits import estimate_landsat_passes, get_coverage_summary
from chronosat.gee import search_real_scenes, print_scene_summary

# --- App Setup ---
app = FastAPI(title="Chronosat Control Center", version="0.2.0")
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

templates = Jinja2Templates(directory="templates")

# In-memory WebSocket connections for real-time updates
active_connections: List[WebSocket] = []


# --- Startup ---
@app.on_event("startup")
def startup():
    init_db()
    print("[Chronosat Dashboard] Database initialized. Default admin: admin / admin123")


# --- Helper Functions ---
def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return get_user_by_id(user_id)


def require_login(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=303, detail="Login required")
    return user


def require_admin(request: Request):
    user = require_login(request)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse("/dashboard")
    return RedirectResponse("/login")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if user:
        request.session["user_id"] = user["id"]
        request.session["username"] = user["username"]
        request.session["role"] = user["role"]
        return RedirectResponse("/dashboard", status_code=303)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = require_login(request)
    is_admin = user["role"] == "admin"

    # Get recent personal activity
    history = get_user_query_history(user["id"], limit=8)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "is_admin": is_admin,
        "history": history,
        "active_missions": [m.short_name for m in get_active_missions(date.today())]
    })


# --- Real-time WebSocket for Live Satellite Simulator ---
@app.websocket("/ws/simulator")
async def simulator_ws(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Send live simulation data every few seconds
            now = datetime.utcnow()
            # Use current time as "simulated historical time" offset for demo
            sim_date = date(1975, 6, (now.day % 28) + 1)   # cycles through June 1975

            # Example locations for live demo
            demo_locations = [
                {"lat": 44.55, "lon": -69.63, "name": "Waterville, ME"},
                {"lat": 40.71, "lon": -74.01, "name": "New York"},
                {"lat": 51.51, "lon": -0.13, "name": "London"},
            ]

            updates = []
            for loc in demo_locations:
                passes = estimate_landsat_passes(loc["lat"], loc["lon"], sim_date)
                updates.append({
                    "location": loc,
                    "date": sim_date.isoformat(),
                    "passes": [{"mission": p.mission, "time": p.approx_utc} for p in passes]
                })

            await websocket.send_json({
                "type": "live_update",
                "timestamp": now.isoformat(),
                "simulated_date": sim_date.isoformat(),
                "updates": updates
            })
            await asyncio.sleep(4)   # Update every 4 seconds

    except WebSocketDisconnect:
        active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


# --- API Endpoints (used by dashboard JS) ---

@app.post("/api/query/coverage")
async def api_coverage(request: Request, lat: float = Form(...), lon: float = Form(...), query_date: str = Form(...)):
    user = require_login(request)
    d = datetime.strptime(query_date, "%Y-%m-%d").date()

    summary = get_coverage_summary(lat, lon, d)
    log_query(user["id"], "coverage", f"{lat},{lon}", query_date, query_date, summary[:200])

    return JSONResponse({"summary": summary, "date": query_date})


@app.post("/api/query/real_gee")
async def api_real_gee(request: Request, lat: float = Form(...), lon: float = Form(...),
                       start: str = Form(...), end: str = Form(...)):
    user = require_login(request)
    try:
        scenes = search_real_scenes(lat, lon, start, end, max_cloud=50, limit=10)
        summary = f"Found {len(scenes)} real scenes"
        log_query(user["id"], "gee_search", f"{lat},{lon}", start, end, summary)
        return JSONResponse({
            "success": True,
            "count": len(scenes),
            "scenes": [s.__dict__ for s in scenes]
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})


@app.get("/api/admin/users")
async def api_admin_users(request: Request):
    require_admin(request)
    users = list_all_users()
    return JSONResponse(users)


@app.post("/api/admin/create_user")
async def api_create_user(request: Request, username: str = Form(...), password: str = Form(...), role: str = Form("basic")):
    require_admin(request)
    success = create_user(username, password, role)
    return JSONResponse({"success": success})


@app.get("/api/admin/activity")
async def api_admin_activity(request: Request):
    require_admin(request)
    logs = get_all_query_logs(limit=30)
    return JSONResponse(logs)


# --- Simple health check ---
@app.get("/health")
async def health():
    return {"status": "ok", "service": "chronosat-dashboard"}