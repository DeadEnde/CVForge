<p align="center"><img src="assets/banner.png" alt="CVForge" width="100%"></p>

# CVForge — paste a CV, get a stunning portfolio (MCP + hosted API)

> CV (PDF/DOCX/Markdown/text) → modern **one-page portfolio** with a design theme
> matched to the person's domain. Glassmorphism, animated gradients, typing hero,
> **Arabic RTL support**, zero dependencies (single `index.html`).
> Ships as an **MCP server**, a **local web playground**, and a **Vercel-ready API**.

---

## Tools (4)

| Tool | What it does |
|---|---|
| `parse_cv_tool(source)` | CV → structured JSON (name, contacts, skills, experience, projects, domain) |
| `generate_portfolio_tool(cv, dir, theme, language)` | Writes a self-contained `index.html` |
| `portfolio_preview(cv, theme, language)` | Returns HTML inline (preview / embed) |
| `list_themes()` | All 11 design themes |

**11 domain-aware themes** — developer (Neon Code), designer (Studio Rose),
photographer (Golden Hour), marketer (Growth Green), data (Data Pulse),
manager (Executive), teacher (Scholar), finance (Fintech), health (Care),
engineer (Builder), generic (Aurora).

**RTL:** `language="ar"` → `lang="ar" dir="rtl"`, full direction-aware layout.

## 🚀 Quick start

```bash
./setup.sh            # deps for local MCP server + playground
./run.sh              # start CVForge MCP server (stdio)
python3 -m uvicorn playground.app:app --port 3500   # interactive web UI
```

MCP client config:
```json
{"mcpServers": { "cvforge": { "command": "python3", "args": ["-m", "cvforge"], "cwd": "/absolute/path/to/cvforge" } }}
```

**No-backend demo:** open `cvforge-offline-playground.html` in any browser —
the entire parse + render runs client-side (great for sharing/link-in-bio).

## ☁️ Deploy to Vercel (hosted public API + landing)

The repo is Vercel-ready: see [DEPLOY.md](DEPLOY.md).
- Landing + interactive demo → `index.html` (static)
- API → `api/main.py` (Python 3.12 serverless):
  - `GET  /api/health` · `GET /api/cv/themes`
  - `POST /api/cv/parse` · `POST /api/cv/parse_file` (PDF/DOCX upload)
  - `POST /api/cv/generate` (`language:"ar"` → RTL)
- BrainBridge is a **separate repo** (local/self-hosted, private memory) — not hosted here.

## 💰 Monetization

See [PRICING.md](PRICING.md) — freemium: free local runs → Pro themes/hosted → Agency white-label.

## 📦 License

MIT — see [LICENSE](LICENSE).

---

*Built by [@DeadEnde](https://github.com/DeadEnde) · 2026*
