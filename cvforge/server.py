"""CVForge — MCP server: turn any CV into a modern portfolio website."""

from __future__ import annotations

import json
from pathlib import Path

from fastmcp import FastMCP

from .cv_parser import parse_cv, detect_domain
from .portfolio import generate_portfolio, generate_portfolio_html
from .themes import THEMES, get_theme

mcp = FastMCP(
    "cvforge",
    instructions=(
        "CVForge: parse a CV (PDF/DOCX/Markdown/text) into structured data and "
        "generate a modern, self-contained portfolio website (single index.html, "
        "zero external dependencies, glassmorphism design adapted to the person's "
        "domain). Use parse_cv first, then generate_portfolio. "
        "Languages: 'en' (LTR) or 'ar' (RTL)."
    ),
)


@mcp.tool()
def parse_cv_tool(source: str) -> dict:
    """Parse a CV from a file path (PDF/DOCX/MD/TXT) or raw text into structured data.

    Args:
        source: Path to the CV file, or the raw CV text.
    """
    data = parse_cv(source)
    return data.to_dict()


@mcp.tool()
def list_themes() -> dict:
    """List available design themes (auto-chosen by domain if not specified)."""
    return {
        "auto_by_domain": list(THEMES.keys()),
        "themes": {k: v["name"] for k, v in THEMES.items()},
    }


@mcp.tool()
def generate_portfolio_tool(cv_data: dict | str, output_dir: str = "portfolio_output",
                            theme: str | None = None, language: str = "en") -> dict:
    """Generate a modern portfolio site from parsed CV data (or re-parse from path/text).

    Args:
        cv_data: Either a parsed CV object (from parse_cv) or a CV file path / raw text.
        output_dir: Where to write index.html.
        theme: Optional theme key (e.g. 'developer', 'designer', 'photographer', ...).
        language: 'en' (LTR) or 'ar' (Arabic RTL).
    """
    if isinstance(cv_data, str):
        cv = parse_cv(cv_data).to_dict()
    else:
        cv = cv_data
    return generate_portfolio(cv, output_dir, theme, language)


@mcp.tool()
def portfolio_preview(cv_data: dict | str, theme: str | None = None,
                      language: str = "en") -> dict:
    """Generate the portfolio HTML and return it inline (for preview/embed).

    Args:
        cv_data: Parsed CV object or CV file path / raw text.
        theme: Optional theme key.
        language: 'en' or 'ar'.
    """
    if isinstance(cv_data, str):
        cv = parse_cv(cv_data).to_dict()
    else:
        cv = cv_data
    html_content = generate_portfolio_html(cv, theme, language)
    return {
        "html": html_content,
        "chars": len(html_content),
        "domain": cv.get("domain", "generic"),
    }


if __name__ == "__main__":
    mcp.run()
