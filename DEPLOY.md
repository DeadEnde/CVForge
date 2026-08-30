# 🚀 Deploy CVForge on Vercel

**Design (1.0):** the function is ONE self-contained file — `api/index.py`
(inline parser + themes + portfolio renderer). Zero local imports, zero
`fastmcp`, zero path hacks → no more FUNCTION_INVOCATION_FAILED.
Routes are registered with AND without the `/api` prefix (Vercel-mount-safe).

## Steps
1. `git push origin main` (this repo) — Vercel auto-deploys on push (Git integration).
2. Or manual: Vercel → Project → Deployments → **Redeploy** on the latest commit.

## Files
- `api/index.py` → FastAPI `app` (routes: health, cv/themes, cv/parse,
  cv/parse_file, cv/generate, brain/{tool} → 501 private)
- `api/requirements.txt` → fastapi, pypdf, python-docx (that's all)
- `vercel.json` → rewrite `/api/(.*)` → `/api/index` + security headers
- `index.html` → static landing (same origin, calls the API)

## Smoke test after deploy
```bash
curl https://<app>.vercel.app/api/health
curl -X POST https://<app>.vercel.app/api/cv/generate \
  -H 'Content-Type: application/json' \
  -d '{"text":"# Sara\nData Analyst\nsara@x.io\n## Skills\n- SQL","language":"ar"}'
# → {"ok":true,"html":"<!DOCTYPE html>…<html lang=\"ar\" dir=\"rtl\">…"}
```

## IF IT STILL FAILS (unlikely — verified with exact simulation)
Open Vercel → Deployments → latest → **Function Logs** and paste the traceback.
Most likely cause at this point: a stale deployment → press **Redeploy**.
