"""
Daemon - Personal API Server

A FastAPI application that serves your personal daemon data
as both a human-readable website and a machine-readable API.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .parser import get_daemon_data

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# FastAPI app
app = FastAPI(
    title="Daemon",
    description="Personal API - A public API that represents you",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Static files (if directory exists)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the daemon website."""
    daemon_data = get_daemon_data(DATA_DIR)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "daemon": daemon_data}
    )


@app.get("/api/daemon", response_class=JSONResponse)
async def get_daemon():
    """Get all daemon data as JSON."""
    return get_daemon_data(DATA_DIR)


@app.get("/api/daemon/{section}", response_class=JSONResponse)
async def get_daemon_section(section: str):
    """Get a specific section of daemon data."""
    daemon_data = get_daemon_data(DATA_DIR)
    section_key = section.lower()

    if section_key not in daemon_data:
        return JSONResponse(
            status_code=404,
            content={"error": f"Section '{section}' not found"}
        )

    return {section_key: daemon_data[section_key]}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "daemon"}


@app.get("/api/sections")
async def list_sections():
    """List all available sections in the daemon data."""
    daemon_data = get_daemon_data(DATA_DIR)
    return {"sections": list(daemon_data.keys())}
