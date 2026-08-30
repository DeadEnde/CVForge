"""BrainForge — Vercel serverless entrypoint (CVForge public API).

Serves:
  GET  /                  -> landing (static, repo root index.html)
  GET  /api/health        -> health check
  POST /api/cv/parse      -> CV text -> structured JSON
  POST /api/cv/parse_file -> upload PDF/DOCX/MD/TXT -> structured JSON
  POST /api/cv/generate   -> CV -> portfolio HTML (EN/AR-RTL, 11 themes)

NOTE: BrainBridge endpoints are intentionally NOT hosted here — the owner's
NotebookLM memory is private. BrainBridge runs locally (./run.sh brain).
"""

import os
import sys
import uuid
from pathlib import Path

# Make the repo root importable so `cvforge` package resolves on Vercel.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402

from cvforge.cv_parser import parse_cv  # noqa: E402
from cvforge.portfolio import generate_portfolio_html  # noqa: E402
from cvforge.themes import THEMES  # noqa: E402

app = FastAPI(title="BrainForge API", version="0.1.0")

_OUT = Path("/tmp/brainforge_deploy")
_OUT.mkdir(parents=True, exist_ok=True)


@app.get("/api/health")
async def health():
    return {"ok": True, "name": "brainforge-api", "parts": ["cvforge"]}


@app.get("/api/cv/themes")
async def cv_themes():
    return {"ok": True, "themes": {k: v["name"] for k, v in THEMES.items()}}


@app.post("/api/cv/parse")
async def cv_parse(body: dict):
    try:
        cv = parse_cv(body.get("text", "")).to_dict()
        return {"ok": True, "cv": cv}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/cv/parse_file")
async def cv_parse_file(file: UploadFile = File(...)):
    suffix = Path(file.filename or "cv.txt").suffix.lower()
    tmp = _OUT / f"upload_{uuid.uuid4().hex[:8]}{suffix}"
    tmp.write_bytes(await file.read())
    try:
        cv = parse_cv(str(tmp)).to_dict()
        return {"ok": True, "cv": cv, "file_id": tmp.stem}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
    finally:
        tmp.unlink(missing_ok=True)


@app.post("/api/cv/generate")
async def cv_generate(body: dict):
    theme = body.get("theme") or None
    language = body.get("language") or "en"
    text = body.get("text", "")
    if not text.strip():
        return JSONResponse({"ok": False, "error": "no CV text"}, status_code=400)
    try:
        cv = parse_cv(text).to_dict()
        html_content = generate_portfolio_html(cv, theme, language)
        return {
            "ok": True,
            "html": html_content,
            "chars": len(html_content),
            "domain": cv.get("domain", "generic"),
            "domain_label": cv.get("domain_label"),
        }
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.api_route("/api/brain/{tool}", methods=["GET", "POST"])
async def brain_private(tool: str):
    """BrainBridge is not hosted: the owner's NotebookLM memory stays private."""
    return JSONResponse({
        "ok": False,
        "error": "BrainBridge is not available on the hosted demo (memory is private).",
        "hint": "Run BrainBridge locally: ./run.sh brain (see README).",
    }, status_code=501)
