"""CVForge — local playground server (FastAPI).

CVForge is a standalone CV → portfolio product. This tiny server proxies the
same endpoints as the hosted Vercel API so the web UI (index.html) works
locally too:

    GET  /api/health                 -> status
    POST /api/cv/parse               -> CV text -> structured JSON
    POST /api/cv/parse_file          -> upload PDF/DOCX/MD/TXT -> structured JSON
    POST /api/cv/generate            -> CV -> portfolio HTML (EN / AR-RTL)

Run:  python3 -m uvicorn playground.app:app --port 3500
Then  open http://localhost:3500  (serves index.html)
"""
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response

from cvforge.cv_parser import parse_cv
from cvforge.themes import THEMES
from cvforge.portfolio import generate_portfolio_html

ROOT = Path(__file__).resolve().parent.parent  # repo root
OUT_DIR = ROOT / "playground_output"

app = FastAPI(title="CVForge Playground", docs_url="/docs")


@app.get("/")
async def index():
    """Serve the web UI."""
    return FileResponse(ROOT / "index.html", media_type="text/html")


@app.get("/api/health")
async def health():
    return {"ok": True, "name": "cvforge-api", "parts": ["cvforge"]}


@app.get("/api/cv/themes")
async def themes():
    return {"ok": True, "themes": {k: v["name"] for k, v in THEMES.items()}}


@app.post("/api/cv/parse")
async def cv_parse(body: dict):
    if not body.get("text", "").strip():
        return {"ok": False, "error": "no CV text"}
    try:
        return {"ok": True, "cv": parse_cv(body["text"])}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


@app.post("/api/cv/parse_file")
async def cv_parse_file(file: UploadFile = File(...)):
    suffix = Path(file.filename or "cv.txt").suffix.lower()
    tmp = OUT_DIR / f"upload_{uuid.uuid4().hex[:8]}{suffix}"
    tmp.write_bytes(await file.read())
    try:
        if suffix == ".pdf":
            from pypdf import PdfReader
            text = "\n".join((page.extract_text() or "") for page in PdfReader(str(tmp)).pages)
        elif suffix in (".docx", ".doc"):
            import docx
            text = "\n".join(p.text for p in docx.Document(str(tmp)).paragraphs)
        else:
            text = tmp.read_text(encoding="utf-8", errors="ignore")
        return {"ok": True, "cv": parse_cv(text)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"could not read {suffix}: {e}"}
    finally:
        tmp.unlink(missing_ok=True)


@app.post("/api/cv/generate")
async def cv_generate(body: dict):
    text = (body.get("text") or "").strip()
    if not text:
        return {"ok": False, "error": "no CV text"}
    try:
        cv = parse_cv(text)
        html = generate_portfolio_html(cv, body.get("theme"), body.get("language", "en"), body.get("seed"))
        from cvforge.design import design_spec as _ds
        t = THEMES.get(body.get("theme") or cv.get("domain") or "generic", THEMES["generic"])
        sp = _ds(t["name"], body.get("seed"))
        return {"ok": True, "html": html, "chars": len(html),
                "domain": cv.get("domain", "generic"), "domain_label": cv.get("domain_label"),
                "design": {"seed": sp["seed"], "layout": sp["layout"], "bg": sp["bg"], "font": sp["font"]}}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}
