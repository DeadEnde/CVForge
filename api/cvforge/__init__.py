"""CVForge — CV → Modern Portfolio MCP server.

Lazy mcp accessor: importing this package must NOT import fastmcp/mcp,
so the hosted API (Vercel) can use cv_parser/portfolio/themes without the
MCP stack installed.
"""

__version__ = "0.1.0"


def __getattr__(name):
    if name == "mcp":
        from .server import mcp
        return mcp
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["mcp", "__version__"]
