FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN uv pip install -e .

# Copy application code
COPY . .

# Expose port for web API
EXPOSE 7200

# Health check (using Python since curl not in slim image)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7200/health')" || exit 1

# Default: run web API server
# Override with: docker run danataka/daemon python -m app.mcp_server
# for MCP stdio mode
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7200"]
