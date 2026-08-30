"""CVForge API — Vercel serverless function (single self-contained file).

This file contains the parser, themes and portfolio renderer INLINE so the
function has ZERO local imports (no cvforge package, no fastmcp, no path
hacks) — the #1 cause of FUNCTION_INVOCATION_FAILED on Vercel.

It also acts as a catch-all: whatever path Vercel forwards
(/api/health, /health, /api/index, /, ...) is dispatched manually, so routing
ambiguity cannot break the function. GET / serves the landing page (bundled
as landing.html next to this file).

Endpoints:
  GET  /api/health | /health                    -> status
  GET  /api/cv/themes | /cv/themes              -> theme list
  POST /api/cv/parse | /cv/parse                -> CV text -> structured JSON
  POST /api/cv/parse_file | /cv/parse_file      -> upload PDF/DOCX/MD/TXT
  POST /api/cv/generate | /cv/generate          -> CV -> portfolio HTML (EN/AR-RTL)
  POST /api/brain/{tool}                        -> 501 (BrainBridge = separate local product)
  GET  / | /index.html                          -> landing page
"""

import json
import re
import uuid
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse, PlainTextResponse, Response

# ---------------------------------------------------------------------------
# MINI CV PARSER (ported from cvforge/cv_parser.py, self-contained)
# ---------------------------------------------------------------------------
DOMAIN_KEYWORDS = {
    "developer": ["developer", "software", "engineer", "programmer", "fullstack", "full stack",
                  "backend", "frontend", "front-end", "react", "vue", "angular", "python",
                  "javascript", "typescript", "node", "java", "php", "laravel", "flutter",
                  "react native", "mobile developer", "web developer", "api", "sql", "devops",
                  "cloud", "aws", "android", "ios", "data engineer", "machine learning"],
    "designer": ["designer", "design", "ui", "ux", "ui/ux", "figma", "photoshop", "illustrator",
                 "branding", "brand identity", "logo", "graphic", "visual", "creative",
                 "art director", "typography", "prototype", "wireframe", "interaction design"],
    "photographer": ["photograph", "photographer", "photo", "videographer", "camera", "lighting",
                     "editing", "lightroom", "retouch", "studio", "wedding", "cinematograph", "drone"],
    "marketer": ["marketing", "seo", "sem", "social media", "content", "growth", "sales",
                 "copywriter", "copywriting", "ads", "campaign", "brand manager",
                 "email marketing", "crm", "community manager", "affiliate", "e-commerce"],
    "data": ["data analyst", "data scientist", "bi ", "analytics", "power bi", "tableau",
             "statistic", "sql", "pandas", "excel", "dashboard", "etl", "data engineer",
             "machine learning", "nlp", "ai model"],
    "manager": ["manager", "director", "project manager", "product manager", "product owner",
                "chef de projet", "scrum", "agile", "leadership", "team lead", "startup",
                "consultant", "business", "operations", "ceo", "founder", "entrepreneur"],
    "teacher": ["teacher", "professor", "professeur", "trainer", "formation", "education",
                "coach", "tutor", "lecturer", "pedagog"],
    "finance": ["accountant", "comptable", "finance", "audit", "financial", "banking",
                "banque", "tax", "fiscal", "comptabilité", "accounting", "controller", "investor"],
    "health": ["doctor", "nurse", "infirmier", "medecin", "médecin", "pharmac", "dentist",
               "physiotherap", "therapist", "clinician", "caregiver"],
    "engineer": ["civil engineer", "mechanical engineer", "electrical engineer", "ingénieur",
                 "ingenieur", "construction", "architect", "architecture", "structural",
                 "mep", "site engineer", "project engineer"],
}
DOMAIN_LABELS = {
    "developer": "Software Developer", "designer": "Creative Designer",
    "photographer": "Photographer", "marketer": "Marketing & Growth",
    "data": "Data Professional", "manager": "Product / Project Manager",
    "teacher": "Educator", "finance": "Finance Professional",
    "health": "Healthcare Professional", "engineer": "Engineer", "generic": "Professional",
}

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:\+?\d[\d\s.\-()]{7,})")
URL_RE = re.compile(r"(?:https?://|www\.)[^\s\"'<>]+|github\.com/[\w-]+|linkedin\.com/in/[\w-]+")
SECTION_RE = {
    "experience": r"(experience|expérience|work history|parcours professionnel|employment)",
    "education": r"(education|formation|études|academic|diploma|degree)",
    "skills": r"(skills|compétences|technical skills|technologies|expertise)",
    "projects": r"(projects|projets|portfolio|réalisations|selected works)",
    "summary": r"(summary|profile|about|à propos|profil|objective|objectif)",
    "languages": r"(languages|langues)",
}
DATE_RANGE_RE = re.compile(
    r"\(\s*(?:19|20)\d{2}\s*[–—-]\s*(?:(?:19|20)\d{2}|present|présent|now|today|en\s+cours|aujourd)",
    re.IGNORECASE,
)
HEADER_RE = re.compile(r"^[A-ZÀ-Ý0-9][\w\s'’\-–—&/+,.()%£€:]{2,160}$")


def detect_domain(text: str) -> str:
    t = text.lower()
    best, best_score = "generic", 0
    for domain, kws in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in kws if kw in t)
        if score > best_score:
            best, best_score = domain, score
    return best


def _split_sections(text: str) -> dict:
    sections, current = {}, None
    for raw in text.splitlines():
        s = re.sub(r"^#{1,6}\s*", "", raw.strip()).strip()
        if not s:
            continue
        matched = None
        for key, pattern in SECTION_RE.items():
            if re.match(rf"^{pattern}\s*:?\s*$", s, re.IGNORECASE):
                matched = key
                break
        if matched:
            current = matched
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append(s)
    for k in sections:
        sections[k] = "\n".join(sections[k])
    return sections


def _simple_parse(lines: list[str], joined: str) -> dict:
    name, title = "", ""
    for line in lines[:6]:
        if (re.fullmatch(r"[A-ZÀ-Ýa-zà-ÿ'’\-–]+(?:\s+[A-ZÀ-Ýa-zà-ÿ'’\-–]+){0,3}", line)
                and len(line) < 60 and not EMAIL_RE.search(line)):
            name = line
            break
    for line in lines[1:9]:
        if (line != name and len(line) < 80 and not EMAIL_RE.search(line)
                and not PHONE_RE.search(line)
                and not re.match(r"^(summary|profile|experience|skills|education|projects|about)", line, re.I)):
            title = line
            break
    email = EMAIL_RE.search(joined)
    phone = PHONE_RE.search(joined)
    urls = URL_RE.findall(joined)
    location = ""
    loc_re = re.compile(r"^[A-ZÀ-Ý][\w'’\- ]+,\s*[A-ZÀ-Ý][\w'’\- ]+$")
    for line in lines[:10]:
        for seg in [x.strip() for x in line.split("|")]:
            if loc_re.match(seg) and not EMAIL_RE.search(seg) and "http" not in seg:
                location = seg
                break
        if location:
            break
    return {"name": name, "title": title,
            "email": email.group(0) if email else "",
            "phone": phone.group(0).strip() if phone else "",
            "website": urls[0] if urls else "", "location": location}


def _bullets(block: str, each_bullet_is_entry: bool = False) -> list[dict]:
    items, current = [], None
    for raw in (block or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        is_bullet = bool(re.match(r"^[-•*·◦▪]\s", line))
        content = re.sub(r"^[-•*·◦▪]\s*", "", line).strip()
        if not content:
            continue
        if each_bullet_is_entry and is_bullet:
            items.append({"title": content, "details": []})
            continue
        is_header = bool(DATE_RANGE_RE.search(content)) or (
            not is_bullet and len(content) < 120 and HEADER_RE.match(content)
            and not content.endswith("."))
        if is_header:
            if current is not None and (current["title"] or current["details"]):
                items.append(current)
            current = {"title": content, "details": []}
            continue
        if is_bullet:
            if current is None:
                current = {"title": content, "details": []}
            else:
                current["details"].append(content)
            continue
        if current is None:
            current = {"title": content[:80], "details": []}
        else:
            current["details"].append(content)
    if current is not None and (current["title"] or current["details"]):
        items.append(current)
    return items


def parse_cv(text: str) -> dict:
    if len(text) < 400 and Path(text).exists():
        path = Path(text)
        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                from pypdf import PdfReader
                text = "\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
            elif suffix == ".docx":
                import docx
                text = "\n".join(p.text for p in docx.Document(str(path)).paragraphs)
            else:
                text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return parse_cv(path.read_text(encoding="utf-8", errors="ignore"))

    lines = [re.sub(r"^#{1,6}\s*", "", l.strip()).strip() for l in text.splitlines() if l.strip()]
    joined = "\n".join(lines)
    base = _simple_parse(lines, joined)
    sections = _split_sections(text)
    domain = detect_domain(text)

    skills = []
    for line in (sections.get("skills") or "").splitlines():
        line = line.lstrip("-•*·,;").strip()
        if not line:
            continue
        if line.count(",") >= 1 and not line.startswith(("C++", "C#")):
            skills.extend([p for p in (s.strip() for s in line.split(",")) if p][:8])
        else:
            skills.append(line)
    skills = skills[:24]

    languages = [l.strip().lstrip("-•*·,").strip()
                 for l in (sections.get("languages") or "").splitlines() if l.strip()]
    if len(languages) == 1 and "," in languages[0]:
        languages = [x.strip() for x in languages[0].split(",") if x.strip()]

    return {
        "name": base["name"], "title": base["title"], "email": base["email"],
        "phone": base["phone"], "location": base["location"], "website": base["website"],
        "summary": (sections.get("summary") or "")[:600],
        "skills": skills,
        "experience": _bullets(sections.get("experience") or "", False)[:8],
        "education": _bullets(sections.get("education") or "", False)[:6],
        "projects": _bullets(sections.get("projects") or "", True)[:8],
        "languages": languages[:8],
        "domain": domain, "domain_label": DOMAIN_LABELS.get(domain, "Professional"),
    }


# ---------------------------------------------------------------------------
# THEMES (ported from cvforge/themes.py)
# ---------------------------------------------------------------------------
THEMES = {
    "developer": {"name": "Neon Code", "pal": {"bg": "#070b14", "bg2": "#0b1220", "card": "rgba(255,255,255,0.05)", "accent": "#6366f1", "accent2": "#22d3ee", "text": "#e7ecf6", "muted": "#8b93a7"}, "grad": ["#6366f1", "#22d3ee", "#a855f7"], "font": "'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace", "radius": "18px"},
    "designer": {"name": "Studio Rose", "pal": {"bg": "#140a12", "bg2": "#1b0e18", "card": "rgba(255,255,255,0.06)", "accent": "#f472b6", "accent2": "#fb923c", "text": "#f8edf4", "muted": "#a3909e"}, "grad": ["#f472b6", "#fb923c", "#facc15"], "font": "'Playfair Display',Georgia,'Times New Roman',serif", "radius": "28px"},
    "photographer": {"name": "Golden Hour", "pal": {"bg": "#0d0b09", "bg2": "#14110c", "card": "rgba(255,255,255,0.05)", "accent": "#f59e0b", "accent2": "#fde68a", "text": "#f5efe4", "muted": "#9c9284"}, "grad": ["#f59e0b", "#fbbf24", "#78716c"], "font": "'Cormorant Garamond',Georgia,serif", "radius": "12px"},
    "marketer": {"name": "Growth Green", "pal": {"bg": "#06120e", "bg2": "#0a1a14", "card": "rgba(255,255,255,0.05)", "accent": "#34d399", "accent2": "#4ade80", "text": "#eaf6ef", "muted": "#8aa79a"}, "grad": ["#34d399", "#4ade80", "#a3e635"], "font": "'Inter','Segoe UI',system-ui,sans-serif", "radius": "20px"},
    "data": {"name": "Data Pulse", "pal": {"bg": "#080a12", "bg2": "#0c101e", "card": "rgba(255,255,255,0.05)", "accent": "#818cf8", "accent2": "#2dd4bf", "text": "#e8ecf7", "muted": "#8a92a8"}, "grad": ["#6366f1", "#2dd4bf", "#0ea5e9"], "font": "'JetBrains Mono',ui-monospace,Menlo,monospace", "radius": "16px"},
    "manager": {"name": "Executive", "pal": {"bg": "#0c0d10", "bg2": "#12141a", "card": "rgba(255,255,255,0.05)", "accent": "#f8fafc", "accent2": "#94a3b8", "text": "#f1f5f9", "muted": "#94a3b8"}, "grad": ["#e2e8f0", "#94a3b8", "#475569"], "font": "'Inter','Segoe UI',system-ui,sans-serif", "radius": "10px"},
    "teacher": {"name": "Scholar", "pal": {"bg": "#0d1014", "bg2": "#131820", "card": "rgba(255,255,255,0.05)", "accent": "#60a5fa", "accent2": "#fbbf24", "text": "#eef2f7", "muted": "#8f9aad"}, "grad": ["#60a5fa", "#fbbf24", "#34d399"], "font": "Georgia,'Times New Roman',serif", "radius": "14px"},
    "finance": {"name": "Fintech", "pal": {"bg": "#0a0f0c", "bg2": "#101712", "card": "rgba(255,255,255,0.05)", "accent": "#10b981", "accent2": "#facc15", "text": "#ecf5ef", "muted": "#8fa295"}, "grad": ["#10b981", "#facc15", "#34d399"], "font": "'Inter','Segoe UI',system-ui,sans-serif", "radius": "12px"},
    "health": {"name": "Care", "pal": {"bg": "#0a0f12", "bg2": "#0f161b", "card": "rgba(255,255,255,0.05)", "accent": "#38bdf8", "accent2": "#f472b6", "text": "#eaf3f8", "muted": "#8aa0ad"}, "grad": ["#38bdf8", "#f472b6", "#a5b4fc"], "font": "'Inter','Segoe UI',system-ui,sans-serif", "radius": "18px"},
    "engineer": {"name": "Builder", "pal": {"bg": "#0b0e10", "bg2": "#121619", "card": "rgba(255,255,255,0.05)", "accent": "#f97316", "accent2": "#fbbf24", "text": "#f2f4f6", "muted": "#96a0a8"}, "grad": ["#f97316", "#fbbf24", "#ef4444"], "font": "'Barlow Condensed','Arial Narrow',system-ui,sans-serif", "radius": "10px"},
    "generic": {"name": "Aurora", "pal": {"bg": "#0a0c14", "bg2": "#10131f", "card": "rgba(255,255,255,0.05)", "accent": "#a78bfa", "accent2": "#f472b6", "text": "#eef0f8", "muted": "#8d93a8"}, "grad": ["#a78bfa", "#f472b6", "#38bdf8"], "font": "'Inter','Segoe UI',system-ui,sans-serif", "radius": "20px"},
}


# ---------------------------------------------------------------------------
# PORTFOLIO RENDERER (ported from cvforge/portfolio.py, self-contained)
# ---------------------------------------------------------------------------
def _esc(v) -> str:
    return str(v if v is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _initials(name: str) -> str:
    parts = [p for p in (name or "CV").replace("·", " ").split() if p]
    return "".join(p[0].upper() for p in parts[:2]) or "CV"


def generate_portfolio_html(cv: dict, theme_key: str | None = None, language: str = "en") -> str:
    theme = THEMES.get(theme_key or cv.get("domain") or "generic", THEMES["generic"])
    p, g = theme["pal"], theme["grad"]
    rtl = str(language).lower().startswith("ar")
    name = _esc(cv.get("name") or "Your Name")
    title = _esc(cv.get("title") or cv.get("domain_label") or "Professional")
    skills = [s.strip() for s in (cv.get("skills") or []) if s.strip()][:24]
    experience = [e for e in (cv.get("experience") or []) if e.get("title")]
    projects = [x for x in (cv.get("projects") or []) if x.get("title")]
    education = [e for e in (cv.get("education") or []) if e.get("title")]
    languages = cv.get("languages") or []
    email, phone, website = _esc(cv.get("email", "")), _esc(cv.get("phone", "")), _esc(cv.get("website", ""))
    summary = _esc((cv.get("summary") or "").strip() or f"{name} — {_esc(cv.get('domain_label') or 'Professional')} committed to quality, impact, and continuous growth.")
    grad = f"linear-gradient(135deg, {g[0]}, {g[1]}, {g[2]})"
    grad_len = f"linear-gradient(90deg, {g[0]}, {g[1]}, {g[2]})"
    direction = ' dir="rtl"' if rtl else ""
    lang_attr = "ar" if rtl else "en"

    chips = "".join(f'<span class="chip">{_esc(s)}</span>' for s in skills)
    lang_chips = "".join(f'<span class="chip chip-ghost">{_esc(l)}</span>' for l in languages)

    def timeline(items, icon):
        if not items:
            return ""
        rows = []
        for it in items:
            t = _esc(it.get("title", ""))
            dets = "".join(f"<p>{_esc(d)}</p>" for d in it.get("details", []) if d and d.strip())
            rows.append(f'<div class="tl-item"><div class="tl-dot">{icon}</div><div class="tl-body"><h3>{t}</h3>{dets}</div></div>')
        return f'<div class="timeline">{"".join(rows)}</div>'

    exp_h = timeline(experience, "💼")
    edu_h = timeline(education, "🎓")
    proj_cards = "".join(
        f'<article class="cproj"><h3>{_esc(x.get("title",""))}</h3>'
        + "".join(f"<p>{_esc(d)}</p>" for d in x.get("details", []) if d and d.strip())
        + "</article>" for x in projects
    ) or '<p class="muted">Contact for a walkthrough of selected work.</p>'

    contact_href = (f"mailto:{email}" if email
                    else (website if website.startswith("http") else f"https://{website}" if website else "#"))

    css = f"""
:root{{--bg:{p['bg']};--card:{p['card']};--accent:{p['accent']};--accent2:{p['accent2']};--text:{p['text']};--muted:{p['muted']};--grad:{grad};--grad-len:{grad_len};--radius:{theme['radius']};--font:{theme['font']};}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:var(--text);font-family:var(--font);line-height:1.65;overflow-x:hidden}}
a{{color:inherit;text-decoration:none}}
::selection{{background:var(--accent);color:#fff}}
.blob{{position:absolute;border-radius:50%;filter:blur(90px);opacity:.3;animation:drift 22s ease-in-out infinite alternate}}
.b1{{width:42vmax;height:42vmax;background:{g[0]};top:-14vmax;inset-inline-start:-10vmax}}
.b2{{width:34vmax;height:34vmax;background:{g[1]};bottom:-12vmax;inset-inline-end:-8vmax;animation-delay:-8s}}
.b3{{width:20vmax;height:20vmax;background:{g[2]};top:38%;inset-inline-start:55%;animation-delay:-15s;opacity:.22}}
@keyframes drift{{to{{transform:translate(6vmax,4vmax) scale(1.12)}}}}
.bg{{position:fixed;inset:0;z-index:-2;overflow:hidden}}
.card,nav,.hero,footer{{background:var(--card);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:1px solid rgba(255,255,255,.09);border-radius:var(--radius)}}
.wrap{{max-width:960px;margin:0 auto;padding:0 20px}}
nav{{position:sticky;top:12px;z-index:50;margin:12px auto 0;max-width:960px}}
nav .wrap{{display:flex;align-items:center;justify-content:space-between;padding:12px 20px}}
.logo{{font-weight:800;font-size:1.05rem;background:var(--grad-len);-webkit-background-clip:text;background-clip:text;color:transparent}}
.nav-links{{display:flex;gap:6px;flex-wrap:wrap}}
.nav-links a{{padding:8px 13px;border-radius:999px;font-size:.85rem;color:var(--muted)}}
.nav-links a:hover{{color:var(--text);background:rgba(255,255,255,.08)}}
.hero{{margin-top:26px;padding:52px 34px 46px;position:relative;overflow:hidden}}
.avatar{{width:86px;height:86px;border-radius:26px;display:grid;place-items:center;font-size:1.9rem;font-weight:800;color:#fff;background:var(--grad);margin-bottom:18px;box-shadow:0 14px 40px {g[0]}55}}
.hero h1{{font-size:clamp(2rem,6vw,3.2rem);line-height:1.12;letter-spacing:-.02em}}
.hero h1 span{{background:var(--grad-len);-webkit-background-clip:text;background-clip:text;color:transparent}}
.typed{{font-size:clamp(1rem,2.6vw,1.3rem);color:var(--accent2);min-height:1.6em;font-weight:600}}
.hero p.lead{{margin-top:14px;color:var(--muted);max-width:640px}}
.cta-row{{display:flex;gap:12px;margin-top:26px;flex-wrap:wrap}}
.btn{{padding:13px 24px;border-radius:999px;font-weight:700;font-size:.92rem;transition:.25s;border:1px solid rgba(255,255,255,.14);display:inline-block}}
.btn.primary{{background:var(--grad);color:#fff;box-shadow:0 10px 30px {g[0]}44}}
.btn.primary:hover{{transform:translateY(-3px)}}
.btn.ghost:hover{{background:rgba(255,255,255,.08)}}
section{{margin-top:56px}}
h2{{font-size:clamp(1.4rem,4vw,2rem);margin-bottom:6px}}
h2 .bar{{display:inline-block;width:46px;height:5px;border-radius:99px;background:var(--grad-len);margin-inline-start:6px;vertical-align:middle}}
.sub{{color:var(--muted);margin-bottom:24px;font-size:.95rem}}
.chips{{display:flex;flex-wrap:wrap;gap:9px}}
.chip{{padding:8px 15px;border-radius:999px;font-size:.84rem;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1)}}
.chip-ghost{{background:transparent;color:var(--muted)}}
.timeline{{position:relative;padding-inline-start:26px}}
.timeline::before{{content:"";position:absolute;inset-block:6px;inset-inline-start:9px;width:2px;background:linear-gradient(var(--accent),transparent);opacity:.5}}
.tl-item{{position:relative;margin-bottom:20px}}
.tl-dot{{position:absolute;inset-inline-start:-26px;top:2px;width:18px;height:18px;border-radius:50%;background:var(--bg);border:2px solid var(--accent);display:grid;place-items:center;font-size:.55rem}}
.tl-body{{padding:14px 18px;background:var(--card);border:1px solid rgba(255,255,255,.08);border-radius:var(--radius)}}
.tl-body h3{{font-size:1.02rem}}
.tl-body p{{color:var(--muted);font-size:.88rem;margin-top:5px}}
.gridP{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}}
.cproj{{padding:22px;background:var(--card);border:1px solid rgba(255,255,255,.08);border-radius:var(--radius);transition:.3s}}
.cproj:hover{{transform:translateY(-5px);border-color:{g[0]}66}}
.cproj h3{{font-size:1.05rem;margin-bottom:8px}}
.cproj p{{color:var(--muted);font-size:.88rem}}
.muted{{color:var(--muted)}}
footer{{margin:64px 0 30px;padding:36px 30px;text-align:center}}
.footer-big{{font-size:clamp(1.3rem,4.6vw,2rem);font-weight:800}}
.footer-big a{{background:var(--grad-len);-webkit-background-clip:text;background-clip:text;color:transparent}}
.meta{{color:var(--muted);margin-top:10px;font-size:.9rem}}
.tiny{{color:var(--muted);font-size:.76rem;margin-top:22px;opacity:.7}}
.reveal{{opacity:0;transform:translateY(26px);transition:opacity .7s ease,transform .7s ease}}
.reveal.in{{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}.reveal{{opacity:1;transform:none}}}}
@media(max-width:600px){{.hero{{padding:36px 20px}}.wrap{{padding:0 14px}}}}
"""

    words = json.dumps([title, cv.get("domain_label") or "Professional", "Available for new opportunities"], ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="{lang_attr}"{direction}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {title}</title>
<style>{css}</style>
</head>
<body>
<div class="bg" aria-hidden="true"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div></div>
<nav><div class="wrap">
  <a class="logo" href="#top">{_initials(cv.get('name'))}</a>
  <div class="nav-links"><a href="#about">About</a><a href="#skills">Skills</a><a href="#experience">Experience</a><a href="#projects">Projects</a><a href="#contact">Contact</a></div>
</div></nav>
<main class="wrap" id="top">
  <header class="hero">
    <div class="avatar">{_initials(cv.get('name'))}</div>
    <h1>{name}<br><span>{title}</span></h1>
    <div class="typed" id="typed">{title}</div>
    <p class="lead">{summary}</p>
    <div class="cta-row">
      <a class="btn primary" href="{contact_href}">Get in touch</a>
      <a class="btn ghost" href="#projects">See work ↓</a>
    </div>
  </header>
  <section id="about"><h2>About <span class="bar"></span></h2><p class="sub">{_esc(cv.get('domain_label',''))} · Focused on real impact.</p></section>
  <section id="skills"><h2>Skills <span class="bar"></span></h2><div class="chips">{chips or '<span class="chip">Core skills</span>'}{f'<div class="chips" style="margin-top:16px">{lang_chips}</div>' if lang_chips else ''}</section>
  <section id="experience"><h2>Experience <span class="bar"></span></h2>{exp_h or '<p class="sub">Detailed experience available on request.</p>'}</section>
  {f'<section id="education"><h2>Education <span class="bar"></span></h2>{edu_h}</section>' if edu_h else ''}
  <section id="projects"><h2>Projects <span class="bar"></span></h2><div class="gridP">{proj_cards}</div></section>
  <footer id="contact">
    <div class="footer-big">{f'<a href="mailto:{email}">{email}</a>' if email else (f'<a href="{website if website.startswith("http") else "https://" + website}">{website}</a>' if website else "Let's work together")}</div>
    <div class="meta">{f'<span>📍 {_esc(cv.get("location",""))}</span>' if cv.get('location') else ''}{f' <span>· 📞 {phone}</span>' if phone else ''}</div>
    <p class="tiny">Generated by <b>CVForge</b> · {name} · {_esc(cv.get('domain_label',''))}</p>
  </footer>
</main>
<script>
(function(){{var w={words};var el=document.getElementById("typed");var wi=0,ci=0,del=false;
function t(){{var s=w[wi]||"";el.textContent=s.slice(0,ci)+"▌";
if(!del&&ci<s.length){{ci++;setTimeout(t,55);}}else if(!del){{del=true;setTimeout(t,1500);}}
else if(ci>0){{ci--;setTimeout(t,24);}}else{{del=false;wi=(wi+1)%w.length;setTimeout(t,300);}}}}
if(el)t();
var io=new IntersectionObserver(function(es){{es.forEach(function(e){{if(e.isIntersecting){{e.target.classList.add("in");io.unobserve(e.target);}}}});}},{{threshold:.12}});
document.querySelectorAll(".hero,section,footer").forEach(function(e){{e.classList.add("reveal");io.observe(e);}});
}})();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# FASTAPI APP — single catch-all dispatcher (no FastAPI injection pitfalls,
# works with ANY path Vercel forwards: /api/health, /health, /api/index, /)
# ---------------------------------------------------------------------------
app = FastAPI(title="CVForge API", version="1.1.0")

_OUT = Path("/tmp/cvforge_api")
_OUT.mkdir(parents=True, exist_ok=True)
_LANDING = Path(__file__).parent / "landing.html"


def _health():
    return {"ok": True, "name": "cvforge-api", "parts": ["cvforge"]}


def _themes():
    return {"ok": True, "themes": {k: v["name"] for k, v in THEMES.items()}}


def _parse(text: str):
    try:
        return {"ok": True, "cv": parse_cv(text)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


def _generate(text: str, theme: str | None, language: str):
    if not text.strip():
        return {"ok": False, "error": "no CV text"}
    try:
        cv = parse_cv(text)
        html_content = generate_portfolio_html(cv, theme, language)
        return {"ok": True, "html": html_content, "chars": len(html_content),
                "domain": cv.get("domain", "generic"), "domain_label": cv.get("domain_label")}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e)}


def _brain_private():
    return {"ok": False,
            "error": "BrainBridge is not available on the hosted demo (memory is private).",
            "hint": "Run BrainBridge locally: github.com/DeadEnde/BrainBridge"}


def _landing():
    try:
        return Response(content=_LANDING.read_text(encoding="utf-8"), media_type="text/html")
    except Exception:
        return PlainTextResponse("CVForge API — see /api/health", media_type="text/plain")


async def _dispatch(full_path: str, request: Request):
    """Catch-all: whatever path Vercel forwards, dispatch manually."""
    orig = full_path.strip("/")
    path = orig

    # normalize: strip leading api/index, api, or index prefixes
    for prefix in ("api/index", "api", "index"):
        if path == prefix or path.startswith(prefix + "/"):
            path = path[len(prefix):].strip("/")
            break

    if request.method == "GET":
        if path == "health":
            return Response(content=json.dumps(_health()), media_type="application/json")
        if path == "cv/themes":
            return Response(content=json.dumps(_themes()), media_type="application/json")
        if orig in ("", "index.html", "playground", "offline", "demo"):
            return _landing()
        if path == "":  # came from /api or /api/index
            return Response(content=json.dumps(_health()), media_type="application/json")
        return JSONResponse({"ok": False, "error": f"unknown route: /{orig}"}, status_code=404)

    if request.method == "POST":
        if path.startswith("brain/"):
            return Response(content=json.dumps(_brain_private()),
                            media_type="application/json", status_code=501)

        # read body manually (JSON or multipart/file)
        ct = request.headers.get("content-type", "")
        text = ""
        theme = None
        language = "en"
        try:
            if "multipart" in ct or "application/x-www-form-urlencoded" in ct:
                form = await request.form()
                f = form.get("file")
                if f is not None and hasattr(f, "filename"):
                    tmp = _OUT / f"upload_{uuid.uuid4().hex[:8]}{Path(f.filename or 'cv.txt').suffix.lower()}"
                    tmp.write_bytes(await f.read())
                    try:
                        text = tmp.read_text(encoding="utf-8", errors="ignore")
                    finally:
                        tmp.unlink(missing_ok=True)
                else:
                    text = str(form.get("text", "") or "")
            else:
                raw = await request.body()
                data = json.loads(raw.decode("utf-8") or "{}") if raw else {}
                text = data.get("text", "")
                theme = data.get("theme")
                language = data.get("language", "en")
        except Exception:
            text = text or ""

        if path == "cv/parse":
            return Response(content=json.dumps(_parse(text)), media_type="application/json")
        if path == "cv/generate":
            res = _generate(text, theme, language)
            return Response(content=json.dumps(res, ensure_ascii=False), media_type="application/json")
        if path == "":
            return _landing()
        return JSONResponse({"ok": False, "error": f"unknown POST route: /{orig}"}, status_code=404)

    return JSONResponse({"ok": False, "error": "method not allowed"}, status_code=405)


app.add_api_route("/{full_path:path}", _dispatch, methods=["GET", "POST"])
