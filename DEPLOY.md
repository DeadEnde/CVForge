# 🚀 Deploy CVForge on Vercel

**Design (2.0 — verified live):** the API is ONE self-contained serverless
function — `api/index.py` (inline CV parser + 11 themes + portfolio renderer).
Zero local imports, zero `fastmcp`, zero path hacks → no
`FUNCTION_INVOCATION_FAILED`.

**Routing (the part that was hard-won):** Vercel auto-routes every request
under `/api/*` to `api/index.py` **with the full original path** — this is the
official FastAPI-on-Vercel pattern. The dispatcher inside `api/index.py`
normalizes prefixes (`api/`, `api/index`, `index`) and dispatches manually.
**Do NOT add a rewrite like `/api/(.*)` → `/api/index`** — it strips the
subpath and every route collapses into one. `vercel.json` = security headers
only.

**Dependencies (the other gotcha):** Vercel's Python runtime installs
dependencies from the **project-root** `requirements.txt` (or
`pyproject.toml`). It MUST contain `fastapi` (plus `pypdf`, `python-docx`
for uploads). `api/requirements.txt` mirrors it.

## Files
- `api/index.py` → FastAPI `app` (catch-all dispatcher):
  - `GET  /api/health` → `{"ok":true,"name":"cvforge-api",...}`
  - `GET  /api/cv/themes` → 11 themes
  - `POST /api/cv/parse` → CV text → structured JSON
  - `POST /api/cv/parse_file` → multipart `file` (PDF/DOCX/MD/TXT) → structured JSON
  - `POST /api/cv/generate` → `{theme, language: "en"|"ar"}` → portfolio HTML (`lang="ar" dir="rtl"`)
  - `POST /api/brain/*` → 501 (BrainBridge is a separate local product)
- `api/landing.html` → bundled copy of the landing page
- `requirements.txt` (root!) → fastapi, pypdf, python-docx (+ local MCP extras)
- `api/requirements.txt` → same minimal set
- `vercel.json` → security headers only (no rewrites)
- `index.html` → static landing served at `/`

## Smoke test after deploy
```bash
curl https://<app>.vercel.app/api/health
curl https://<app>.vercel.app/api/cv/themes
curl -X POST https://<app>.vercel.app/api/cv/generate \
  -H 'Content-Type: application/json' \
  -d '{"text":"# Sara\nData Analyst\nsara@x.io\n## Skills\n- SQL","language":"ar"}'
# → {"ok":true,"html":"<!DOCTYPE html>…<html lang=\"ar\" dir=\"rtl\">…"}
curl -X POST https://<app>.vercel.app/api/cv/parse_file -F file=@cv.pdf
```

## Live production notes
- Prod: `https://cv-forge-brown.vercel.app` (GitHub integration,
  `DeadEnde/CVForge` → auto-deploy on push to `main`).
- If a push doesn't show up after ~2 min: Vercel → Deployments → **Redeploy**.

## Troubleshooting log (for future projects)
1. `"runtime": "python3.12"` in vercel.json → invalid, build fails. Remove it.
2. Importing the local `cvforge` package from the function → `fastmcp`
   missing in Vercel → 500. Keep the function self-contained.
3. Root `requirements.txt` missing `fastapi` → runtime crash at import.
4. Rewrite `/api/(.*)` → `/api/index` → subpath stripped → all routes
   collapse. No rewrites; let Vercel's auto-routing pass the full path.
