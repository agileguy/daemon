"""
MCP Server for Daemon API.

Exposes the daemon's personal API data as MCP tools for AI assistants.
Run with: python -m app.mcp_server
"""

import asyncio
import json
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .parser import get_daemon_data

# Path to data directory
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# Create MCP server
server = Server("daemon")


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
    daemon_data = get_daemon_data(DATA_DIR)

    if name == "get_daemon_data":
        return [TextContent(type="text", text=json.dumps(daemon_data, indent=2))]

    elif name == "get_daemon_section":
        section = arguments.get("section", "").lower()
        if section not in daemon_data:
            available = ", ".join(daemon_data.keys())
            return [
                TextContent(
                    type="text",
                    text=f"Section '{section}' not found. Available sections: {available}",
                )
            ]
        return [
            TextContent(
                type="text", text=json.dumps({section: daemon_data[section]}, indent=2)
            )
        ]

    elif name == "list_daemon_sections":
        sections = list(daemon_data.keys())
        return [TextContent(type="text", text=json.dumps({"sections": sections}, indent=2))]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
