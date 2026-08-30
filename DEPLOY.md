# 🚀 Deploy CVForge on Vercel

Vercel-ready: static landing (`index.html`) + Python serverless API (`api/main.py`).
BrainBridge is a **separate repo and stays local/self-hosted** (private memory).

## Option A — Vercel Dashboard (Git)
1. Push this repo to GitHub:
   ```bash
   git remote add origin https://github.com/DeadEnde/CVForge.git
   git push -u origin main
   ```
2. Vercel → **Add New → Project** → Import `DeadEnde/CVForge`.
3. Framework preset: **Other**. Root directory: `./`. No env vars needed.
4. **Deploy** — done. Every `git push` re-deploys.

## Option B — CLI
```bash
npx vercel deploy --yes        # preview
npx vercel --prod --yes        # production
```

## Config (already in repo)
- `vercel.json` → function `api/main.py` (python3.12, maxDuration 30s),
  rewrites `/api/*` → function, security headers.
- `api/requirements.txt` → fastapi, pypdf, python-docx (function-only deps).
- `.gitignore` → `.vercel/`, cache, secrets.

## After deploy — smoke test
```bash
curl https://<your-app>.vercel.app/api/health
curl -X POST https://<your-app>.vercel.app/api/cv/generate \
  -H 'Content-Type: application/json' \
  -d '{"text":"# Sara\nData Analyst\nsara@x.io\n## Skills\n- SQL","language":"ar"}'
# → {"ok":true,"html":"<!DOCTYPE html>…<html lang=\"ar\" dir=\"rtl\">…"}
```

## Local pre-check
```bash
uvicorn api.main:app --port 8799
```
