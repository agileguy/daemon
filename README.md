# Daemon

A personal API that represents you. A public, queryable interface to who you are and what you care about.

Inspired by [Daniel Miessler's Daemon](https://daemon.danielmiessler.com/).

## What is a Daemon?

A daemon is a live view into what you're doing and what you care about, designed for connecting with others who share similar interests. It serves as:

- **For Humans**: A beautiful website showing who you are
- **For AI**: A structured, queryable API that AI systems can access

## Quick Start

### Using Docker (Recommended)

```bash
# Build and run
docker compose up -d

# View at http://localhost:7200
```

### Local Development

```bash
# Install dependencies with uv
uv pip install -e .

# Run the server
uvicorn app.main:app --reload

# View at http://localhost:7200
```

## Customization

Edit `data/daemon.md` to customize your daemon. The file uses a simple section-based format:

```markdown
[ABOUT]
name: Your Name
title: Your Title
location: Your Location
bio: |
  Your multi-line bio goes here.
  It can span multiple lines.

[INTERESTS]
- Interest 1
- Interest 2
- Interest 3

[PREFERENCES]
key1: value1
key2: value2
```

### Available Sections

| Section | Description |
|---------|-------------|
| `[ABOUT]` | Name, title, location, bio |
| `[MISSION]` | Your personal mission statement |
| `[CURRENT_FOCUS]` | What you're working on now |
| `[INTERESTS]` | Topics you care about |
| `[FAVORITE_BOOKS]` | Books you recommend |
| `[FAVORITE_PODCASTS]` | Podcasts you listen to |
| `[TOOLS_I_USE]` | Your tech stack |
| `[DAILY_ROUTINE]` | How you structure your day |
| `[PREFERENCES]` | Communication, work style, etc. |
| `[PREDICTIONS]` | Your views on the future |
| `[CONTACT]` | How to reach you |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Human-readable website |
| `GET /api/daemon` | Full daemon data as JSON |
| `GET /api/daemon/{section}` | Specific section |
| `GET /api/sections` | List available sections |
| `GET /api/docs` | OpenAPI documentation |
| `GET /health` | Health check |

## Example API Response

```bash
curl http://localhost:8000/api/daemon/about
```

```json
{
  "about": {
    "name": "Dan",
    "title": "Technology Leader & AI Enthusiast",
    "location": "San Francisco Bay Area",
    "bio": "Engineering leader passionate about AI..."
  }
}
```

## Project Structure

```
daemon/
├── app/
│   ├── __init__.py
│   ├── main.py        # FastAPI application
│   └── parser.py      # daemon.md parser
├── data/
│   └── daemon.md      # Your daemon data (source of truth)
├── templates/
│   └── index.html     # Website template
├── static/            # Static assets (optional)
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## Deployment

### Docker

```bash
docker build -t daemon .
docker run -p 8000:8000 daemon
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: daemon
spec:
  replicas: 1
  selector:
    matchLabels:
      app: daemon
  template:
    metadata:
      labels:
        app: daemon
    spec:
      containers:
      - name: daemon
        image: daemon:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
```

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Jinja2** - Template engine
- **uvicorn** - ASGI server
- **uv** - Fast Python package manager

## License

MIT
