"""
MCP Server for Daemon API.

Exposes the daemon's personal API data as MCP tools for AI assistants.
Fetches data from the remote API at daemon.agileguy.ca.

Run with: python -m app.mcp_server

Configure in Claude Code (~/.claude/settings.json):
{
  "mcpServers": {
    "daemon": {
      "command": "python",
      "args": ["-m", "app.mcp_server"],
      "cwd": "/path/to/daemon"
    }
  }
}
"""

import asyncio
import json
from urllib.request import urlopen, Request
from urllib.error import URLError

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

API_BASE = "https://daemon.agileguy.ca"

server = Server("daemon")


def _fetch_json(path: str) -> dict:
    """Fetch JSON from the remote daemon API."""
    url = f"{API_BASE}{path}"
    req = Request(url, headers={"Accept": "application/json"})
    with urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="get_daemon_data",
            description="Get all personal daemon data including identity, bio, skills, and more",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="get_daemon_section",
            description="Get a specific section of daemon data (e.g., identity, skills, interests)",
            inputSchema={
                "type": "object",
                "properties": {
                    "section": {
                        "type": "string",
                        "description": "The section name to retrieve (case-insensitive)",
                    }
                },
                "required": ["section"],
            },
        ),
        Tool(
            name="list_daemon_sections",
            description="List all available sections in the daemon data",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle MCP tool calls."""
    try:
        if name == "get_daemon_data":
            data = _fetch_json("/api/daemon")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]

        elif name == "get_daemon_section":
            section = arguments.get("section", "")
            data = _fetch_json(f"/api/daemon/{section}")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]

        elif name == "list_daemon_sections":
            data = _fetch_json("/api/sections")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except URLError as e:
        return [TextContent(type="text", text=f"Failed to reach daemon API: {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {e}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
