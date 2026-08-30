"""CVForge — generate a modern, self-contained portfolio site from a CV.

Output: single `index.html` (inline CSS/JS/SVG, zero external deps) —
works offline, in any preview, and deploys anywhere (Netlify/Vercel/GitHub Pages).
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from .themes import get_theme

FONTS = {
    "mono-touch": "'JetBrains Mono','Fira Code',ui-monospace,'Cascadia Code',Menlo,Consolas,monospace",
    "serif-touch": "'Playfair Display',Georgia,'Times New Roman',serif",
    "serif": "Georgia,'Times New Roman',serif",
    "elegant": "'Cormorant Garamond',Georgia,serif",
    "modern": "'Inter','Segoe UI',system-ui,-apple-system,sans-serif",
    "minimal": "'Inter','Segoe UI',system-ui,-apple-system,sans-serif",
    "industrial": "'Barlow Condensed','Arial Narrow',system-ui,sans-serif",
}


def _esc(v: str) -> str:
    return html.escape(str(v or ""))


def _safe_list(skills: list[str], limit: int = 24) -> list[str]:
    return [s.strip() for s in (skills or []) if s.strip()][:limit]


def _initials(name: str) -> str:
    parts = [p for p in name.replace("·", " ").split() if p]
    if not parts:
        return "CV"
    return "".join(p[0].upper() for p in parts[:2])


def _summary_text(cv) -> str:
    s = (cv.get("summary") or "").strip()
    if s:
        return s
    return f"{_esc(cv.get('name') or 'Professional')} — {cv.get('domain_label', 'Professional')} committed to quality, impact, and continuous growth."


def generate_portfolio_html(cv: dict, theme_key: str | None = None, language: str = "en", seed: int | None = None) -> str:
    """Render a procedural portfolio design for the given CV.

    seed=None -> deterministic 'signature' design for the theme;
    any other seed -> a brand-new design (infinite designs).
    """
    from .design import render_portfolio_html as _design_render
    theme = get_theme(cv.get("domain", "generic") if isinstance(cv, dict) else "generic", theme_key)
    pal = dict(theme["palette"])
    pal.setdefault("line", "rgba(255,255,255,0.09)")
    pal.setdefault("bt", "#fff")
    t = {"name": theme["name"], "pal": pal,
         "grad": theme["gradient"],
         "font": FONTS.get(theme["font_style"], FONTS["modern"]),
         "radius": theme["radius"]}
    return _design_render(cv, t, language, seed)



def generate_portfolio(cv: dict, output_dir: str, theme: str | None = None,
                       language: str = "en", filename: str = "index.html") -> dict:
    """Write the portfolio HTML to output_dir and return metadata."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    html_content = generate_portfolio_html(cv, theme, language)
    path = out / filename
    path.write_text(html_content, encoding="utf-8")
    return {
        "path": str(path),
        "bytes": len(html_content.encode("utf-8")),
        "domain": cv.get("domain", "generic"),
        "domain_label": cv.get("domain_label", "Professional"),
        "theme": (theme or cv.get("domain", "generic")),
        "preview_hint": "Open index.html in any browser — fully self-contained.",
    }
