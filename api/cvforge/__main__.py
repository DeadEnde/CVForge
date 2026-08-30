"""`python -m cvforge` — run the CVForge MCP server (stdio by default)."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
