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
from fastapi.openapi.docs import get_swagger_ui_html
from mcp.server.sse import SseServerTransport
from starlette.responses import Response

from .parser import get_daemon_data
from .mcp_server import server as mcp_server

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Custom Swagger UI dark theme CSS
SWAGGER_DARK_CSS = """
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg-primary: #0a0a0a;
    --bg-secondary: #111111;
    --bg-tertiary: #1a1a1a;
    --text-primary: #fafafa;
    --text-secondary: #a1a1aa;
    --accent: #22c55e;
}

body {
    background: var(--bg-primary) !important;
}

.swagger-ui {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.swagger-ui .topbar {
    background: var(--bg-secondary) !important;
    border-bottom: 1px solid #27272a;
}

.swagger-ui .topbar .download-url-wrapper .download-url-button {
    background: var(--accent) !important;
    color: #000 !important;
}

.swagger-ui .info {
    margin: 30px 0 !important;
}

.swagger-ui .info .title {
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--text-primary) !important;
}

.swagger-ui .info .description p,
.swagger-ui .info .description {
    color: var(--text-secondary) !important;
}

.swagger-ui .scheme-container {
    background: var(--bg-secondary) !important;
    box-shadow: none !important;
    border: 1px solid #27272a !important;
}

.swagger-ui .opblock-tag {
    color: var(--text-primary) !important;
    border-bottom: 1px solid #27272a !important;
}

.swagger-ui .opblock {
    background: var(--bg-secondary) !important;
    border: 1px solid #27272a !important;
    box-shadow: none !important;
}

.swagger-ui .opblock .opblock-summary {
    border-bottom: 1px solid #27272a !important;
}

.swagger-ui .opblock .opblock-summary-method {
    font-family: 'JetBrains Mono', monospace !important;
}

.swagger-ui .opblock.opblock-get {
    background: rgba(34, 197, 94, 0.1) !important;
    border-color: rgba(34, 197, 94, 0.3) !important;
}

.swagger-ui .opblock.opblock-get .opblock-summary-method {
    background: var(--accent) !important;
}

.swagger-ui .opblock.opblock-post {
    background: rgba(59, 130, 246, 0.1) !important;
    border-color: rgba(59, 130, 246, 0.3) !important;
}

.swagger-ui .opblock.opblock-put {
    background: rgba(249, 115, 22, 0.1) !important;
    border-color: rgba(249, 115, 22, 0.3) !important;
}

.swagger-ui .opblock.opblock-delete {
    background: rgba(239, 68, 68, 0.1) !important;
    border-color: rgba(239, 68, 68, 0.3) !important;
}

.swagger-ui .opblock .opblock-summary-path,
.swagger-ui .opblock .opblock-summary-description {
    color: var(--text-primary) !important;
}

.swagger-ui .opblock-description-wrapper p,
.swagger-ui .opblock-body pre,
.swagger-ui .response-col_description {
    color: var(--text-secondary) !important;
}

.swagger-ui .opblock-section-header {
    background: var(--bg-tertiary) !important;
    box-shadow: none !important;
}

.swagger-ui .opblock-section-header h4 {
    color: var(--text-primary) !important;
}

.swagger-ui table thead tr td,
.swagger-ui table thead tr th {
    color: var(--text-primary) !important;
    border-bottom: 1px solid #27272a !important;
}

.swagger-ui .parameter__name,
.swagger-ui .parameter__type,
.swagger-ui .response-col_status {
    color: var(--text-primary) !important;
}

.swagger-ui .model-title {
    color: var(--text-primary) !important;
}

.swagger-ui .model {
    color: var(--text-secondary) !important;
}

.swagger-ui section.models {
    border: 1px solid #27272a !important;
}

.swagger-ui section.models.is-open h4 {
    border-bottom: 1px solid #27272a !important;
}

.swagger-ui .model-box {
    background: var(--bg-secondary) !important;
}

.swagger-ui .highlight-code,
.swagger-ui .microlight {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
}

.swagger-ui .btn {
    border: 1px solid #27272a !important;
    color: var(--text-primary) !important;
    background: var(--bg-tertiary) !important;
}

.swagger-ui .btn:hover {
    background: var(--bg-secondary) !important;
}

.swagger-ui select {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
    border: 1px solid #27272a !important;
}

.swagger-ui input[type=text] {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
    border: 1px solid #27272a !important;
}

.swagger-ui .servers-title,
.swagger-ui .servers label {
    color: var(--text-primary) !important;
}

.swagger-ui .response-col_links {
    color: var(--text-secondary) !important;
}

/* Hide the default topbar logo */
.swagger-ui .topbar-wrapper img {
    display: none;
}

.swagger-ui .topbar-wrapper::before {
    content: 'DAEMON';
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--text-primary);
}
"""

# FastAPI app (disable default docs to use custom)
app = FastAPI(
    title="Daemon",
    description="Personal API - A public API that represents you",
    version="0.1.0",
    docs_url=None,
    redoc_url="/api/redoc",
)


@app.get("/api/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with dark theme."""
    return HTMLResponse(
        content=f"""
<!DOCTYPE html>
<html>
<head>
    <title>Daemon - API Docs</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
    <style>{SWAGGER_DARK_CSS}</style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({{
            url: '/openapi.json',
            dom_id: '#swagger-ui',
            presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
            layout: "BaseLayout",
            deepLinking: true,
            showExtensions: true,
            showCommonExtensions: true
        }});
    </script>
</body>
</html>
""",
        media_type="text/html",
    )

# MCP SSE transport
sse_transport = SseServerTransport("/mcp/messages/")


@app.get("/mcp/sse")
async def handle_sse(request: Request):
    """SSE endpoint for MCP clients."""
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0], streams[1], mcp_server.create_initialization_options()
        )
    return Response()


app.mount("/mcp/messages/", app=sse_transport.handle_post_message)

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
