"""BrainForge Playground — interactive web UI to test both MCP servers in the sandbox.

Endpoints:
  GET  /                    -> web UI (inline HTML/CSS/JS, no external deps)
  POST /api/brain/{tool}    -> call a BrainBridge tool (JSON body = tool params)
  POST /api/cv/parse        -> parse CV text -> structured data
  POST /api/cv/parse_file   -> upload CV (pdf/docx/md/txt) -> structured data
  POST /api/cv/generate     -> generate portfolio (text or file_id) -> HTML
"""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI(title="BrainForge Playground")

INDEX = Path(__file__).parent / "index.html"
OUT_DIR = Path("/home/user/brainforge/playground_output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# server-side store for uploaded CVs (id -> parsed cv dict)
CV_STORE: dict[str, dict] = {}

BRAIN_TOOLS = {
    "brain_status", "brain_list", "brain_ask", "brain_login", "brain_login_silent",
    "brain_logout", "memory_sources", "memory_read", "memory_context", "memory_save",
}


async def call_brain(tool: str, params: dict) -> str:
    """BrainBridge is a separate product/repo — not available in this build."""
    try:
        from brainbridge.server import mcp  # noqa: F401
        res = await mcp.call_tool(tool, params or {})
        parts = []
        for c in res.content:
            parts.append(getattr(c, "text", None) or str(c))
        return "".join(parts)
    except ImportError:
        return json.dumps({
            "ok": False,
            "error": "BrainBridge is not included in the CVForge repo (separate product).",
            "hint": "Get it at github.com/DeadEnde/BrainBridge — local/self-hosted memory MCP.",
        }, ensure_ascii=False)


@app.get("/")
async def index():
    return FileResponse(INDEX, media_type="text/html")


@app.post("/api/brain/{tool}")
async def brain(tool: str, body: dict):
    if tool not in BRAIN_TOOLS:
        return JSONResponse({"error": f"unknown tool {tool}"}, status_code=404)
    try:
        text = await call_brain(tool, body)
        return {"ok": True, "text": text}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/cv/parse")
async def cv_parse(body: dict):
    from cvforge.cv_parser import parse_cv
    try:
        cv = parse_cv(body.get("text", "")).to_dict()
        return {"ok": True, "cv": cv}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/cv/parse_file")
async def cv_parse_file(file: UploadFile = File(...)):
    from cvforge.cv_parser import parse_cv
    suffix = Path(file.filename or "cv.txt").suffix.lower()
    tmp = OUT_DIR / f"upload_{uuid.uuid4().hex[:8]}{suffix}"
    tmp.write_bytes(await file.read())
    try:
        cv = parse_cv(str(tmp)).to_dict()
        fid = uuid.uuid4().hex[:10]
        CV_STORE[fid] = cv
        # keep the file too
        CV_STORE[fid + "_file"] = str(tmp)
        return {"ok": True, "cv": cv, "file_id": fid}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@app.post("/api/cv/generate")
async def cv_generate(body: dict):
    from cvforge.cv_parser import parse_cv
    from cvforge.portfolio import generate_portfolio_html

    theme = body.get("theme") or None
    language = body.get("language") or "en"

    if body.get("file_id") and body["file_id"] in CV_STORE:
        cv = CV_STORE[body["file_id"]]
    else:
        text = body.get("text", "")
        if not text:
            return JSONResponse({"ok": False, "error": "no CV text or file_id"}, status_code=400)
        cv = parse_cv(text).to_dict()

    try:
        html_content = generate_portfolio_html(cv, theme, language)
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    sid = f"gen_{int(time.time())}_{uuid.uuid4().hex[:6]}"
    out = OUT_DIR / sid / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_content, encoding="utf-8")

    return {
        "ok": True,
        "html": html_content,
        "chars": len(html_content),
        "domain": cv.get("domain", "generic"),
        "domain_label": cv.get("domain_label"),
        "path": str(out),
    }


@app.get("/playground_output/{sid}/index.html")
async def output_file(sid: str):
    p = OUT_DIR / sid / "index.html"
    if not p.exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    return FileResponse(p, media_type="text/html")
