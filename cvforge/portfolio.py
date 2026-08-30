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


def generate_portfolio_html(cv: dict, theme_key: str | None = None, language: str = "en") -> str:
    """Build the full portfolio HTML string from parsed CV data."""
    theme = get_theme(cv.get("domain", "generic"), theme_key)
    p = theme["palette"]
    grad = theme["gradient"]
    font = FONTS.get(theme["font_style"], FONTS["modern"])
    rtl = language.lower().startswith("ar")
    dir_attr = ' dir="rtl"' if rtl else ""
    lang_attr = _esc(language)

    name = _esc(cv.get("name") or "Your Name")
    title = _esc(cv.get("title") or cv.get("domain_label", "Professional"))
    skills = _safe_list(cv.get("skills"))
    experience = cv.get("experience") or []
    education = cv.get("education") or []
    projects = cv.get("projects") or []
    languages = cv.get("languages") or []
    email, phone, website = _esc(cv.get("email", "")), _esc(cv.get("phone", "")), _esc(cv.get("website", ""))
    initials = _esc(_initials(cv.get("name", "")))

    # filter out empty heuristic entries
    experience = [e for e in experience if e.get("title")]
    projects = [pj for pj in projects if pj.get("title")]
    education = [e for e in education if e.get("title")]

    skill_chips = "".join(f'<span class="chip">{_esc(s)}</span>' for s in skills)
    lang_chips = "".join(f'<span class="chip chip-ghost">{_esc(l)}</span>' for l in languages)

    def timeline(items, icon):
        if not items:
            return ""
        rows = []
        for it in items:
            t = _esc(it.get("title", ""))
            details = [d for d in it.get("details", []) if d.strip()]
            rows.append(
                f'<div class="tl-item"><div class="tl-dot">{icon}</div>'
                f'<div class="tl-body"><h3>{t}</h3>'
                + "".join(f"<p>{_esc(d)}</p>" for d in details)
                + "</div></div>"
            )
        return f'<div class="timeline">{"".join(rows)}</div>'

    exp_html = timeline(experience, "💼")
    edu_html = timeline(education, "🎓")

    proj_cards = ""
    for pj in projects:
        t = _esc(pj.get("title", ""))
        details = [d for d in pj.get("details", []) if d.strip()]
        proj_cards += (
            '<article class="card project">'
            f'<h3>{t}</h3>'
            + "".join(f"<p>{_esc(d)}</p>" for d in details)
            + "</article>"
        )
    if not proj_cards:
        proj_cards = '<p class="muted">Contact for a walkthrough of selected work.</p>'

    contact_email = email or website or phone
    contact_href = f"mailto:{email}" if email else (website if website.startswith("http") else f"https://{website}" if website else "#")

    gradient_css = (f"linear-gradient(135deg, {grad[0]}, {grad[1]}, {grad[2]})")
    gradient_css_len = (f"linear-gradient(90deg, {grad[0]}, {grad[1]}, {grad[2]})")

    return f"""<!DOCTYPE html>
<html lang="{lang_attr}"{dir_attr}>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} — {title}</title>
<meta name="description" content="Portfolio of {name}, {title}.">
<style>
:root {{
  --bg:{p['bg']}; --bg2:{p['bg2']}; --card:{p['card']};
  --accent:{p['accent']}; --accent2:{p['accent2']}; --text:{p['text']}; --muted:{p['muted']};
  --line:{p.get('line','rgba(255,255,255,0.09)')}; --bt:{p.get('bt','#fff')};
  --line:{p.get('line','rgba(255,255,255,0.09)')}; --bt:{p.get('bt','#fff')};
  --grad:{gradient_css}; --grad-len:{gradient_css_len};
  --radius:{theme['radius']}; --font:{font};
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ background:var(--bg); color:var(--text); font-family:var(--font); line-height:1.65; overflow-x:hidden; }}
::selection {{ background:var(--accent); color:#fff; }}
a {{ color:inherit; text-decoration:none; }}

/* Animated background */
.bg-blobs {{ position:fixed; inset:0; z-index:-2; overflow:hidden; }}
.blob {{ position:absolute; border-radius:50%; filter:blur(90px); opacity:.32; animation:drift 22s ease-in-out infinite alternate; }}
.blob.b1 {{ width:42vmax; height:42vmax; background:{grad[0]}; top:-14vmax; inset-inline-start:-10vmax; }}
.blob.b2 {{ width:34vmax; height:34vmax; background:{grad[1]}; bottom:-12vmax; inset-inline-end:-8vmax; animation-delay:-8s; }}
.blob.b3 {{ width:20vmax; height:20vmax; background:{grad[2]}; top:38%; inset-inline-start:55%; animation-delay:-15s; opacity:.22; }}
@keyframes drift {{ to {{ transform:translate(6vmax,4vmax) scale(1.12); }} }}

/* Glass card */
.card, nav, .hero, footer {{ background:var(--card); backdrop-filter:blur(18px); -webkit-backdrop-filter:blur(18px); border:1px solid var(--line); border-radius:var(--radius); }}
.wrap {{ max-width:960px; margin:0 auto; padding:0 20px; }}

/* Nav */
nav {{ position:sticky; top:12px; z-index:50; margin:12px auto 0; max-width:960px; }}
nav .wrap {{ display:flex; align-items:center; justify-content:space-between; padding:12px 20px; }}
.logo {{ font-weight:800; font-size:1.05rem; background:var(--grad-len); -webkit-background-clip:text; background-clip:text; color:transparent; }}
.nav-links {{ display:flex; gap:6px; flex-wrap:wrap; }}
.nav-links a {{ padding:8px 13px; border-radius:999px; font-size:.85rem; color:var(--muted); transition:.25s; }}
.nav-links a:hover {{ color:var(--text); background:var(--card); }}

/* Hero */
.hero {{ margin-top:26px; padding:52px 34px 46px; position:relative; overflow:hidden; }}
.hero::after {{ content:""; position:absolute; inset:-40%; background:radial-gradient(circle at 30% 20%, {grad[0]}22, transparent 45%),radial-gradient(circle at 80% 60%, {grad[1]}1e, transparent 40%); animation:pulse 9s ease-in-out infinite alternate; z-index:-1; }}
@keyframes pulse {{ to {{ transform:scale(1.15) rotate(8deg); }} }}
.avatar {{ width:86px; height:86px; border-radius:26px; display:grid; place-items:center; font-size:1.9rem; font-weight:800; color:var(--bt); background:var(--grad); margin-bottom:18px; box-shadow:0 14px 40px {grad[0]}55; }}
.hero h1 {{ font-size:clamp(2rem,6vw,3.2rem); line-height:1.12; letter-spacing:-.02em; }}
.hero h1 span {{ background:var(--grad-len); -webkit-background-clip:text; background-clip:text; color:transparent; }}
.typed {{ font-size:clamp(1rem,2.6vw,1.3rem); color:var(--accent2); min-height:1.6em; font-weight:600; }}
.hero p.lead {{ margin-top:14px; color:var(--muted); max-width:640px; }}
.cta-row {{ display:flex; gap:12px; margin-top:26px; flex-wrap:wrap; }}
.btn {{ padding:13px 24px; border-radius:999px; font-weight:700; font-size:.92rem; transition:.25s; border:1px solid var(--line); }}
.btn.primary {{ background:var(--grad); color:var(--bt); box-shadow:0 10px 30px {grad[0]}44; }}
.btn.primary:hover {{ transform:translateY(-3px); box-shadow:0 16px 40px {grad[0]}66; }}
.btn.ghost:hover {{ background:var(--card); transform:translateY(-3px); }}

/* Sections */
section {{ margin-top:56px; }}
h2 {{ font-size:clamp(1.4rem,4vw,2rem); margin-bottom:6px; }}
h2 .bar {{ display:inline-block; width:46px; height:5px; border-radius:99px; background:var(--grad-len); margin-inline-start:6px; vertical-align:middle; }}
.sub {{ color:var(--muted); margin-bottom:24px; font-size:.95rem; }}

/* Chips */
.chips {{ display:flex; flex-wrap:wrap; gap:9px; }}
.chip {{ padding:8px 15px; border-radius:999px; font-size:.84rem; background:var(--card); border:1px solid var(--line); transition:.25s; cursor:default; }}
.chip:hover {{ transform:translateY(-2px); border-color:var(--accent); color:var(--accent2); }}
.chip-ghost {{ background:transparent; color:var(--muted); }}

/* Timeline */
.timeline {{ position:relative; padding-inline-start:26px; }}
.timeline::before {{ content:""; position:absolute; inset-block:6px; inset-inline-start:9px; width:2px; background:linear-gradient(var(--accent),transparent); opacity:.5; }}
.tl-item {{ position:relative; margin-bottom:20px; }}
.tl-dot {{ position:absolute; inset-inline-start:-26px; top:2px; width:18px; height:18px; border-radius:50%; background:var(--bg); border:2px solid var(--accent); display:grid; place-items:center; font-size:.55rem; }}
.tl-body {{ padding:14px 18px; background:var(--card); border:1px solid var(--line); border-radius:var(--radius); }}
.tl-body h3 {{ font-size:1.02rem; }}
.tl-body p {{ color:var(--muted); font-size:.88rem; margin-top:5px; }}

/* Projects */
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; }}
.card.project {{ padding:22px; transition:.3s; }}
.card.project:hover {{ transform:translateY(-5px); border-color:{grad[0]}66; box-shadow:0 18px 50px rgba(0,0,0,.35); }}
.card.project h3 {{ font-size:1.05rem; margin-bottom:8px; }}
.card.project p {{ color:var(--muted); font-size:.88rem; }}

/* Contact */
footer {{ margin:64px 0 30px; padding:36px 30px; text-align:center; }}
footer .big {{ font-size:clamp(1.3rem,4.6vw,2rem); font-weight:800; }}
footer .big a {{ background:var(--grad-len); -webkit-background-clip:text; background-clip:text; color:transparent; }}
footer .meta {{ color:var(--muted); margin-top:10px; font-size:.9rem; }}
.tiny {{ color:var(--muted); font-size:.76rem; margin-top:22px; opacity:.7; }}

/* Scroll reveal */
.reveal {{ opacity:0; transform:translateY(26px); transition:opacity .7s ease, transform .7s ease; }}
.reveal.in {{ opacity:1; transform:none; }}

@media (prefers-reduced-motion: reduce) {{
  * {{ animation:none !important; transition:none !important; }}
  .reveal {{ opacity:1; transform:none; }}
}}
@media (max-width:600px) {{
  .hero {{ padding:36px 20px; }}
  nav .wrap {{ flex-direction:column; gap:10px; }}
  .wrap {{ padding:0 14px; }}
}}
</style>
</head>
<body>
<div class="bg-blobs" aria-hidden="true"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div></div>

<nav><div class="wrap">
  <a class="logo" href="#top">{initials}</a>
  <div class="nav-links">
    <a href="#about">About</a><a href="#skills">Skills</a><a href="#experience">Experience</a><a href="#projects">Projects</a><a href="#contact">Contact</a>
  </div>
</div></nav>

<main class="wrap" id="top">
  <header class="hero reveal in">
    <div class="avatar">{initials}</div>
    <h1>{name}<br><span>{title}</span></h1>
    <div class="typed" data-words='{json.dumps([title, cv.get("domain_label", "Professional"), "Available for new opportunities"], ensure_ascii=False)}'></div>
    <p class="lead">{_summary_text(cv)}</p>
    <div class="cta-row">
      <a class="btn primary" href="{contact_href}">Get in touch</a>
      <a class="btn ghost" href="#projects">See work ↓</a>
    </div>
  </header>

  <section id="about" class="reveal">
    <h2>About <span class="bar"></span></h2>
    <p class="sub">{cv.get('domain_label','')} · Focused on real impact.</p>
  </section>

  <section id="skills" class="reveal">
    <h2>Skills <span class="bar"></span></h2>
    <div class="chips">{skill_chips or '<span class="chip">Core skills</span>'}</div>
    {f'<div style="margin-top:16px" class="chips">{lang_chips}</div>' if lang_chips else ''}
  </section>

  <section id="experience" class="reveal">
    <h2>Experience <span class="bar"></span></h2>
    {exp_html or '<p class="sub">Detailed experience available on request.</p>'}
  </section>

  <section id="education" class="reveal">
    <h2>Education <span class="bar"></span></h2>
    {edu_html or ''}
  </section>

  <section id="projects" class="reveal">
    <h2>Projects <span class="bar"></span></h2>
    <div class="grid">{proj_cards}</div>
  </section>

  <footer id="contact" class="reveal">
    <div class="big">{'<a href="mailto:{0}">{0}</a>'.format(email) if email else ('<a href="{0}">{0}</a>'.format(website) if website else 'Let’s work together')}</div>
    <div class="meta">
      {'<span>📍 {0}</span>'.format(_esc(cv.get('location',''))) if cv.get('location') else ''}
      {'<span> · 📞 {0}</span>'.format(phone) if phone else ''}
    </div>
    <p class="tiny">Generated by <b>CVForge</b> · {name} · {_esc(cv.get('domain_label',''))}</p>
  </footer>
</main>

<script>
// Typing effect
const typedEl = document.querySelector('.typed');
if (typedEl) {{
  const words = JSON.parse(typedEl.dataset.words || '[]');
  let wi = 0, ci = 0, del = false;
  function tick() {{
    const w = words[wi] || '';
    typedEl.textContent = w.slice(0, ci) + '▌';
    if (!del && ci < w.length) {{ ci++; setTimeout(tick, 55); }}
    else if (!del) {{ del = true; setTimeout(tick, 1600); }}
    else if (ci > 0) {{ ci--; setTimeout(tick, 26); }}
    else {{ del = false; wi = (wi + 1) % words.length; setTimeout(tick, 350); }}
  }}
  tick();
}}
// Scroll reveal
const io = new IntersectionObserver(es => es.forEach(e => {{ if (e.isIntersecting) {{ e.target.classList.add('in'); io.unobserve(e.target); }} }}), {{ threshold: .12 }});
document.querySelectorAll('.reveal').forEach(el => io.observe(el));
// Parallax blobs on pointer move (desktop only)
if (matchMedia('(pointer:fine)').matches) {{
  document.addEventListener('pointermove', e => {{
    const x = (e.clientX / innerWidth - .5), y = (e.clientY / innerHeight - .5);
    document.querySelectorAll('.blob').forEach((b, i) => {{
      b.style.translate = `${{x * (14 + i * 10)}}px ${{y * (14 + i * 10)}}px`;
    }});
  }});
}}
</script>
</body>
</html>"""


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
