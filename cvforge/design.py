"""CVForge — INFINITE DESIGN ENGINE (procedural portfolio designs).

Every (seed, theme) pair produces a different STRUCTURAL design: layout
archetype, background treatment, typography, shape language, card style,
section accents. Same seed + same theme = identical design (shareable);
new seed = brand-new design. Deterministic (mulberry32) + identical in
Python and JS (landing page/offline playground use the JS port).
"""
from __future__ import annotations

import html as _html
import json as _json

# ---------------------------------------------------------------- RNG ----
def _h32(s: str) -> int:
    h = 0
    for ch in s:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h


def _mulberry32(seed: int):
    s = seed & 0xFFFFFFFF

    def rnd():
        nonlocal s
        s = (s + 0x6D2B79F5) & 0xFFFFFFFF
        t = s
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t = (t ^ (t + (((t ^ (t >> 7)) * (t | 61)) & 0xFFFFFFFF))) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296

    return rnd


# ------------------------------------------------------------ vocab ------
LAYOUTS = ["split", "hero", "bento", "editorial", "terminal", "glass", "white", "magazine"]
BGS = ["blobs", "mesh", "grid", "dots", "scan", "waves", "stripes", "plain"]
FONTS = ["display", "serif", "mono", "sans", "round"]
RADII = ["0px", "10px", "22px", "32px"]
CHIPS = ["999px", "8px", "22px", "6px"]
CARDS = ["fill", "outline", "glass", "hard"]
ACCENTS = ["bar", "underline", "num", "dot"]
HEROS = ["avatar", "initials", "split", "min"]
FONT_STACKS = {
    "display": "'Barlow Condensed','Arial Narrow','Inter',system-ui,sans-serif",
    "serif": "'Playfair Display',Georgia,'Times New Roman',serif",
    "mono": "'JetBrains Mono','Fira Code',ui-monospace,Menlo,Consolas,monospace",
    "sans": "'Inter','Segoe UI',system-ui,sans-serif",
    "round": "'Nunito','Segoe UI',system-ui,sans-serif",
}


def design_spec(theme_key: str | None, seed: int | None = None) -> dict:
    seed = _h32(theme_key or "cvforge") if seed is None else (int(seed) & 0xFFFFFFFF)
    r = _mulberry32(seed or 1)
    i = lambda n: int(r() * n)  # noqa: E731
    return {
        "seed": seed,
        "layout": LAYOUTS[i(len(LAYOUTS))],
        "bg": BGS[i(len(BGS))],
        "font": FONTS[i(len(FONTS))],
        "shape": i(len(RADII)),
        "chip": i(len(CHIPS)),
        "card": CARDS[i(len(CARDS))],
        "accent": ACCENTS[i(len(ACCENTS))],
        "hero": HEROS[i(len(HEROS))],
        "motion": r() < 0.85,
        "grain": r() < 0.35,
    }


def _esc(v) -> str:
    return _html.escape(str(v or ""))


def _initials(name: str) -> str:
    parts = [p for p in (name or "CV").replace("·", " ").split() if p]
    return "".join(p[0].upper() for p in parts[:2]) if parts else "CV"


# ------------------------------------------------------------ render -----
def render_portfolio_html(cv: dict, theme: dict, language: str = "en", seed: int | None = None) -> str:
    pal = dict(theme.get("pal", {}))
    g = theme.get("grad", ["#6366f1", "#22d3ee", "#a855f7"])
    spec = design_spec(theme.get("name", "cvforge") or "cvforge", seed)
    p = dict(pal)
    p.setdefault("line", "rgba(255,255,255,0.09)")
    p.setdefault("bt", "#fff")
    p.setdefault("bg2", p.get("bg", "#0a0c14"))
    bg_hex = p.get("bg", "#000000")
    dark = (bg_hex.startswith("#") and len(bg_hex) >= 7 and int(bg_hex[1:3], 16) < 200) or spec["layout"] == "terminal"

    # layout-forced bases
    if spec["layout"] == "terminal":
        p.update(bg="#0b0e13", bg2="#10141c", card="rgba(0,255,65,0.04)",
                 line="rgba(255,255,255,0.12)", text="#e9f5ec", muted="#7f9f8a", bt="#031408")
        dark = True
    if spec["layout"] == "white":
        p.update(bg="#ffffff", bg2="#f7f8fa", card="#ffffff", line="rgba(15,23,42,0.12)",
                 text="#0f172a", muted="#64748b", bt="#0f172a")
        dark = False

    # content -------------------------------------------------------------
    name = _esc(cv.get("name") or "Your Name")
    title = _esc(cv.get("title") or cv.get("domain_label") or "Professional")
    label = _esc(cv.get("domain_label") or "Professional")
    summary = _esc((cv.get("summary") or "").strip() or f"{name} — {label} committed to quality, impact, and continuous growth.")
    email = _esc(cv.get("email") or "")
    website = _esc(cv.get("website") or "")
    phone = _esc(cv.get("phone") or "")
    loc = _esc(cv.get("location") or "")
    href = (f"mailto:{email}" if email else
            (website if website.startswith("http") else f"https://{website}" if website else "#"))
    ini = _initials(cv.get("name"))
    skills = "".join(f'<span class="chip">{_esc(s)}</span>' for s in (cv.get("skills") or [])[:24]) or '<span class="chip">Core skills</span>'
    langs = "".join(f'<span class="chip ghost">{_esc(l)}</span>' for l in (cv.get("languages") or [])[:10])

    def tl(items):
        if not items:
            return ""
        return '<div class="timeline">' + "".join(
            '<div class="tl-item"><div class="tl-dot"></div><div class="tl-body">'
            f'<h3>{_esc(it.get("title") or it.get("role") or it.get("degree") or "")}</h3>'
            f'<p class="tl-meta">{_esc(it.get("period") or it.get("company") or it.get("school") or "")}</p>'
            + "".join(f"<p>{_esc(d)}</p>" for d in it.get("details", []) if d and d.strip())
            + "</div></div>" for it in items) + "</div>"

    exp = tl(cv.get("experience") or [])
    edu = tl(cv.get("education") or [])
    projs = "".join(
        '<article class="card cproj"><h3>' + _esc(x.get("title") or "") + "</h3>"
        + "".join(f"<p>{_esc(d)}</p>" for d in x.get("details", []) if d and d.strip()) + "</article>"
        for x in (cv.get("projects") or [])[:9]) or '<p class="muted">Contact for a walkthrough of selected work.</p>'
    words = [title, label, "Available for new opportunities"]

    def head(label_txt, idx):
        a = spec["accent"]
        if a == "bar":
            return f'<h2><span class="bar"></span>{label_txt}</h2>'
        if a == "underline":
            return f'<h2 class="ul">{label_txt}</h2>'
        if a == "num":
            return f'<h2 class="num"><b>{idx:02d}</b>{label_txt}</h2>'
        return f'<h2 class="dotac"><i></i>{label_txt}</h2>'

    sec_about = f'<section id="about" class="reveal">{head("About", 1)}<p class="sub">{label} · {summary}</p></section>'
    sec_skills = f'<section id="skills" class="reveal">{head("Skills", 2)}<div class="chips">{skills}</div>' + (f'<div class="chips" style="margin-top:14px">{langs}</div>' if langs else "") + "</section>"
    sec_exp = f'<section id="experience" class="reveal">{head("Experience", 3)}' + (exp or '<p class="sub">Detailed experience available on request.</p>') + "</section>"
    sec_edu = f'<section id="education" class="reveal">{head("Education", 4)}{edu}</section>' if edu else ""
    sec_proj = f'<section id="projects" class="reveal">{head("Projects", 5)}<div class="gridP">{projs}</div></section>'
    footer = ('<footer id="contact" class="reveal"><div class="big"><a class="big-a" href="' + href + '">'
              + (email or website or "Let’s work together") + "</a></div>"
              + (f'<div class="meta">📍 {loc} · ☎ {phone}</div>' if (loc or phone) else "")
              + f'<p class="tiny">Generated by <b>CVForge</b> · Design #{spec["seed"]} · {name} · {label}</p></footer>')

    hero_map = {
        "avatar": f'<header class="hero reveal"><div class="avatar">{ini}</div><h1>{name}<br><span class="g">{title}</span></h1>'
                  f'<div class="typed">{title}</div><p class="lead">{summary}</p><div class="cta-row">'
                  f'<a class="btn primary" href="{href}">Get in touch</a><a class="btn ghost" href="#projects">See work ↓</a></div></header>',
        "initials": f'<header class="hero reveal"><div class="avatar">{ini}</div><h1>{name}<br><span class="g">{title}</span></h1>'
                    f'<div class="typed">{title}</div><p class="lead">{summary}</p><div class="cta-row">'
                    f'<a class="btn primary" href="{href}">Get in touch</a><a class="btn ghost" href="#projects">See work ↓</a></div></header>',
        "split": f'<header class="hero reveal"><div class="avatar round">{ini}</div><div>'
                 f'<h1>{name}<br><span class="g">{title}</span></h1><div class="typed">{title}</div>'
                 f'<p class="lead">{summary}</p><div class="cta-row"><a class="btn primary" href="{href}">Get in touch</a>'
                 f'<a class="btn ghost" href="#projects">See work ↓</a></div></div></header>',
        "min": f'<header class="hero reveal"><h1>{name} <span class="g">— {title}</span></h1>'
               f'<p class="lead">{summary}</p><div class="cta-row"><a class="btn primary" href="{href}">Get in touch</a>'
               f'<a class="btn ghost" href="#projects">See work ↓</a></div></header>',
    }
    hero = hero_map[spec["hero"]]

    nav = ('<nav><div class="wrap"><a class="logo" href="#top">' + ini + "</a><div class=\"nav-links\">"
           '<a href="#about">About</a><a href="#skills">Skills</a><a href="#experience">Experience</a>'
           '<a href="#projects">Projects</a><a href="#contact">Contact</a></div></div></nav>')

    L = spec["layout"]
    if L == "split":
        side = ('<aside class="side-card"><div class="avatar">' + ini + '</div><h3 class="side-name">' + name
                + '</h3><p class="muted">' + title + '</p><div class="contact-mini">'
                + (f'<a href="mailto:{email}">✉ {email}</a>' if email else "")
                + (f'<span>☎ {phone}</span>' if phone else "")
                + (f'<span>📍 {loc}</span>' if loc else "") + "</div></aside>")
        inner = ('<div class="shell"><div class="side-col">' + side + '</div><main class="main-col">'
                 + hero + sec_about + sec_skills + sec_exp + sec_edu + sec_proj + footer + "</main></div>")
    elif L == "bento":
        inner = ('<div class="shell">'
                 f'<section class="bcard b-about reveal">{head("About", 1)}<p class="sub">{label} · {summary}</p></section>'
                 f'<section class="bcard b-skills reveal">{head("Skills", 2)}<div class="chips">{skills}</div></section>'
                 f'<section class="bcard b-exp reveal">{head("Experience", 3)}{exp or "<p class=\"sub\">On request.</p>"}</section>'
                 + (f'<section class="bcard b-edu reveal">{head("Education", 4)}{edu}</section>' if edu else "")
                 + f'<section class="bcard b-proj reveal">{head("Projects", 5)}<div class="gridP">{projs}</div></section>'
                 + '<footer class="bcard b-foot" id="contact"><div class="big"><a class="big-a" href="' + href + '">'
                 + (email or website or "Let’s work together") + '</a></div><p class="tiny">Generated by <b>CVForge</b> · Design #' + str(spec["seed"]) + '</p></footer>'
                 + "</div>")
    elif L == "magazine":
        band = ('<div class="mband"><div class="wrap"><div class="mband-left"><div class="mma">PORTFOLIO</div>'
                f'<h1 class="mh1">{name}</h1><p class="msub">{title}</p></div>'
                f'<div class="mband-right"><div class="avatar big">{ini}</div>'
                + (f'<div class="mm">{loc}</div>' if loc else "") + "</div></div></div>")
        inner = ('<div class="shell-mz">' + band + '<main class="wrap" id="top">' + sec_about + sec_skills
                 + sec_exp + sec_edu + sec_proj + footer.replace('class="big"', 'class="big"') + "</main></div>")
    else:
        inner = ('<main class="wrap" id="top">' + hero + sec_about + sec_skills + sec_exp + sec_edu
                 + sec_proj + footer + "</main>")

    # css present for editorial wrapper etc.
    if L == "editorial":
        inner = inner.replace('<main class="wrap" id="top">', '<main class="container-max" id="top">')

    # ------------------------------------------------------- css assembly
    grad = f"linear-gradient(135deg,{g[0]},{g[1]},{g[2]})"
    grad_len = f"linear-gradient(90deg,{g[0]},{g[1]},{g[2]})"
    fbody = FONT_STACKS["sans"] if spec["font"] in ("sans", "round", "display") else FONT_STACKS["serif"] if spec["font"] == "serif" else FONT_STACKS["mono"]
    pal_vars = (f"--bg:{p['bg']};--bg2:{p['bg2']};--card:{p['card']};--line:{p['line']};"
                f"--accent:{p['accent']};--accent2:{p['accent2']};--text:{p['text']};--muted:{p['muted']};--bt:{p['bt']};"
                f"--grad:{grad};--grad-len:{grad_len};--r:{RADII[spec['shape']]};--chipr:{CHIPS[spec['chip']]};"
                f"--fbody:{fbody};--fhead:{FONT_STACKS[spec['font']]};")
    css = (_CSS_TMPL
           + _LAYOUT_CSS[L] + _BG_CSS[spec["bg"]] + _FONT_CSS[spec["font"]]
           + _SHAPE_CSS[spec["shape"]] + _CARD_CSS[spec["card"]] + _HERO_CSS[spec["hero"]])
    css = (css.replace("@@PAL@@", pal_vars).replace("@@ACCENT@@", g[0])
              .replace("@@ACCENT2@@", g[1]).replace("@@C3@@", g[2] if len(g) > 2 else g[1]))

    rtl = (language or "en").lower().startswith("ar")
    langattr, dirattr = ("ar", ' dir="rtl"') if rtl else ("en", "")
    typed = ""
    if spec["motion"]:
        w = _json.dumps(words, ensure_ascii=False)
        typed = ("<script>(function(){var w=" + w
                 + ";var el=document.querySelector('.typed');if(!el)return;var wi=0,ci=0,del=false;"
                 "function t(){var s=w[wi]||'';el.textContent=s.slice(0,ci)+'▌';"
                 "if(!del&&ci<s.length){ci++;setTimeout(t,55);}else if(!del){del=true;setTimeout(t,1500);}"
                 "else if(ci>0){ci--;setTimeout(t,24);}else{del=false;wi=(wi+1)%w.length;setTimeout(t,300);}}t();"
                 "var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)"
                 "{e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.12});"
                 "document.querySelectorAll('.reveal').forEach(function(e){io.observe(e);});})();</script>")
    grain = '<div class="grain"></div>' if spec["grain"] else ""

    return ('<!DOCTYPE html><html lang="' + langattr + '"' + dirattr + '><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            f'<title>{name} — {title}</title><style>{css}</style></head>'
            f'<body class="ls-{L} {"dark" if dark else "light"} bgbg-{spec["bg"]}">'
            f'<div class="bg" aria-hidden="true">{_BG_HTML[spec["bg"]]}</div>{grain}{nav}{inner}{typed}</body></html>')


# ----------------------------------------------------------------- CSS ---
_CSS_TMPL = """:root{@@PAL@@}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:var(--fbody);line-height:1.65;overflow-x:hidden;position:relative;min-height:100vh}
a{color:inherit;text-decoration:none}
::selection{background:var(--accent);color:var(--bt)}
.wrap{max-width:1040px;margin:0 auto;padding:0 22px}
.container-max{max-width:860px;margin:0 auto;padding:0 22px}
.muted{color:var(--muted)}
.grain{position:fixed;inset:0;z-index:90;pointer-events:none;opacity:.05;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='2'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='0.6'/%3E%3C/svg%3E")}
.bg{position:fixed;inset:0;z-index:-2;overflow:hidden}
nav{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--bg) 92%,transparent);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
nav .wrap{display:flex;align-items:center;justify-content:space-between;padding:14px 22px}
.logo{font-weight:900;font-size:1.1rem;letter-spacing:.5px;background:var(--grad-len);-webkit-background-clip:text;background-clip:text;color:transparent}
.nav-links{display:flex;gap:4px;flex-wrap:wrap}
.nav-links a{font-size:.82rem;padding:7px 13px;border-radius:999px;color:var(--muted);font-weight:600}
.nav-links a:hover{color:var(--text);background:var(--card)}
.avatar{width:92px;height:92px;border-radius:26px;background:var(--grad);display:grid;place-items:center;font-weight:900;font-size:1.9rem;color:var(--bt);box-shadow:0 16px 44px @@ACCENT@@44}
.hero{margin-top:34px;padding:46px 0 40px}
.hero h1{font-family:var(--fhead);font-size:clamp(2.4rem,7vw,4.4rem);line-height:1.02;letter-spacing:-.02em;font-weight:800}
.hero h1 .g{background:var(--grad-len);-webkit-background-clip:text;background-clip:text;color:transparent}
.typed{font-family:var(--fhead);font-size:clamp(1rem,2.6vw,1.3rem);color:var(--accent2);min-height:1.6em;font-weight:700}
.lead{color:var(--muted);margin-top:14px;max-width:660px}
.cta-row{display:flex;gap:12px;margin-top:26px;flex-wrap:wrap}
.btn{padding:13px 26px;font-weight:800;font-size:.92rem;border:1px solid var(--line);border-radius:999px;display:inline-block;transition:.25s}
.btn.primary{background:var(--grad);color:var(--bt);box-shadow:0 10px 30px @@ACCENT@@44}
.btn.primary:hover{transform:translateY(-3px)}
.btn.ghost:hover{background:var(--card)}
section{margin-top:52px}
h2{font-family:var(--fhead);font-size:clamp(1.4rem,4vw,2rem);margin-bottom:14px;letter-spacing:-.01em}
h2 .bar{display:inline-block;width:44px;height:5px;border-radius:99px;background:var(--grad-len);margin-inline-start:8px;vertical-align:middle}
h2.ul{border-bottom:2px solid var(--line);padding-bottom:8px}
h2.num{border:1px solid var(--line);padding:10px 16px;border-radius:var(--r);background:var(--card);font-weight:900}
h2.num b{color:var(--accent);margin-inline-end:10px;font-family:var(--fbody)}
h2.dotac{display:flex;align-items:center;gap:10px}
h2.dotac i{width:12px;height:12px;border-radius:50%;background:var(--grad);box-shadow:0 0 12px @@ACCENT@@}
.sub{color:var(--muted);margin-bottom:22px}
.chips{display:flex;flex-wrap:wrap;gap:9px}
.chip{padding:8px 16px;border-radius:var(--chipr);font-size:.84rem;background:var(--card);border:1px solid var(--line);font-weight:600}
.chip.ghost{background:transparent}
.timeline{position:relative;padding-inline-start:26px}
.timeline::before{content:"";position:absolute;inset-block:4px;inset-inline-start:9px;width:2px;background:linear-gradient(var(--accent),transparent);opacity:.5}
.tl-item{position:relative;margin-bottom:18px}
.tl-dot{position:absolute;inset-inline-start:-26px;top:2px;width:18px;height:18px;border-radius:50%;background:var(--bg);border:2px solid var(--accent);display:grid;place-items:center}
.tl-body{padding:16px 18px;background:var(--card);border:1px solid var(--line);border-radius:var(--r)}
.tl-body h3{font-size:1.02rem}
.tl-meta{color:var(--accent2);font-size:.8rem;font-weight:700;margin-top:2px}
.tl-body p{color:var(--muted);font-size:.88rem;margin-top:5px}
.gridP{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}
.cproj{padding:20px;transition:.25s}
.cproj:hover{transform:translateY(-5px);border-color:@@ACCENT@@66}
.cproj h3{font-size:1.04rem;margin-bottom:8px}
.cproj p{color:var(--muted);font-size:.88rem}
.card{background:var(--card);border:1px solid var(--line);border-radius:var(--r)}
footer{margin:60px 0 34px;text-align:center;padding:30px;background:var(--card);border:1px solid var(--line);border-radius:var(--r)}
.big{font-size:clamp(1.2rem,4vw,1.8rem);font-weight:900}
.big-a{background:var(--grad-len);-webkit-background-clip:text;background-clip:text;color:transparent}
.meta{color:var(--muted);margin-top:8px;font-size:.88rem}
.tiny{color:var(--muted);font-size:.72rem;margin-top:16px;opacity:.75}
.contact-mini{display:flex;flex-direction:column;gap:7px;margin-top:16px;font-size:.84rem;color:var(--muted);word-break:break-word}
.contact-mini a:hover{color:var(--accent2)}
.reveal{opacity:0;transform:translateY(22px);transition:opacity .6s ease,transform .6s ease}
.reveal.in{opacity:1;transform:none}
@media(max-width:700px){.shell{grid-template-columns:1fr!important}.side-col{display:none}.mband .wrap{grid-template-columns:1fr}.wrap,.container-max{padding:0 16px}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}.reveal{opacity:1;transform:none}}
"""

_LAYOUT_CSS = {
 "split": ".shell{display:grid;grid-template-columns:320px 1fr;gap:30px;max-width:1120px;margin:0 auto;padding:0 22px}.side-col{padding-top:30px}.side-card{position:sticky;top:82px;background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:26px;text-align:center}.side-card .avatar{margin:0 auto 18px}.side-name{font-family:var(--fhead);font-size:1.5rem}.main-col{padding-top:30px;min-width:0}",
 "hero": ".hero{text-align:center;padding:72px 0 48px}.hero .avatar{margin:0 auto 20px}.hero h1{font-size:clamp(2.8rem,9vw,5.6rem)}.lead{margin:16px auto 0}.cta-row{justify-content:center}section{max-width:820px;margin-inline:auto}",
 "bento": ".shell{max-width:1080px;margin:0 auto;padding:0 22px;display:grid;grid-template-columns:repeat(12,1fr);gap:16px}.bcard{background:var(--card);border:1px solid var(--line);border-radius:var(--r);padding:24px;grid-column:span 6;margin-top:52px}.b-about{grid-column:span 12;margin-top:34px;background:var(--grad);color:var(--bt);border:none}.b-about h2{color:var(--bt)}.b-about h2 .bar{background:#fff}.b-about .sub{color:color-mix(in srgb,var(--bt) 78%,transparent)}.b-skills{grid-column:span 5}.b-exp{grid-column:span 7}.b-edu{grid-column:span 5}.b-proj{grid-column:span 7}.b-foot{grid-column:span 12}.b-about h2.num,.b-about h2.dotac i{color:var(--bt)}@media(max-width:800px){.bcard{grid-column:span 12!important}}",
 "editorial": ".hero{padding:60px 0 30px}.hero h1{font-family:var(--fhead);font-size:clamp(2.6rem,8vw,4.6rem)}section{border-top:1px solid var(--line);padding-top:26px}",
 "terminal": "nav{background:rgba(11,14,19,.92)}.hero{border:1px solid var(--line);border-radius:var(--r);padding:34px;background:rgba(255,255,255,0.02);font-family:var(--fbody)}.hero h1{text-transform:uppercase;letter-spacing:.04em;font-size:clamp(2rem,6vw,3.2rem)}.typed{color:var(--accent)}.chip,.tl-body,.cproj,footer{border-radius:4px}.term{display:none}",
 "glass": ".hero .avatar{border-radius:50%}.tl-body,.cproj,footer{background:color-mix(in srgb,var(--card) 60%,transparent);backdrop-filter:blur(18px)}",
 "white": "body{background:#fff}nav{background:rgba(255,255,255,.9)}h2{color:#0f172a}.lead{color:#64748b}.avatar{box-shadow:0 16px 40px rgba(15,23,42,.14)}",
 "magazine": ".shell-mz .mband{background:var(--grad);color:var(--bt);padding:56px 0 46px}.mband .wrap{display:grid;grid-template-columns:1fr auto;gap:26px;align-items:center}.mband-left .mma{font-size:.72rem;letter-spacing:4px;font-weight:900;opacity:.85}.mh1{font-family:var(--fhead);font-size:clamp(2.4rem,7vw,4.2rem);line-height:1;color:var(--bt)}.msub{color:color-mix(in srgb,var(--bt) 80%,transparent);font-weight:700;margin-top:8px}.mband-right .mm{font-size:.85rem;color:color-mix(in srgb,var(--bt) 80%,transparent);margin-top:10px;text-align:end}.mband .avatar{border-radius:50%;border:3px solid color-mix(in srgb,var(--bt) 60%,transparent)}#top{margin-top:6px}",
}
_BG_CSS = {
 "blobs": ".bgbg-blobs .blob{position:absolute;border-radius:50%;filter:blur(90px);opacity:.3;animation:drift 22s ease-in-out infinite alternate}.bgbg-blobs .b1{width:42vmax;height:42vmax;background:@@ACCENT@@;top:-14vmax;left:-10vmax}.bgbg-blobs .b2{width:34vmax;height:34vmax;background:@@ACCENT2@@;bottom:-12vmax;right:-8vmax;animation-delay:-8s}.bgbg-blobs .b3{width:20vmax;height:20vmax;background:@@C3@@;top:38%;left:55%;animation-delay:-15s;opacity:.2}@keyframes drift{to{transform:translate(6vmax,4vmax) scale(1.12)}}",
 "mesh": ".bgbg-mesh .bg{background:radial-gradient(at 18% 12%,@@ACCENT@@33,transparent 46%),radial-gradient(at 85% 18%,@@ACCENT2@@2e,transparent 42%),radial-gradient(at 70% 85%,@@ACCENT@@26,transparent 45%)}",
 "grid": ".bgbg-grid .bg{background-image:linear-gradient(var(--line) 1px,transparent 1px),linear-gradient(90deg,var(--line) 1px,transparent 1px);background-size:44px 44px;opacity:.55}",
 "dots": ".bgbg-dots .bg{background-image:radial-gradient(var(--accent) 1.2px,transparent 1.3px);background-size:26px 26px;opacity:.22}",
 "scan": ".bgbg-scan .bg{background-image:repeating-linear-gradient(0deg,rgba(255,255,255,0.025) 0 1px,transparent 1px 4px)}.bgbg-scan.light .bg{background-image:repeating-linear-gradient(0deg,rgba(15,23,42,.05) 0 1px,transparent 1px 4px)}",
 "waves": ".bgbg-waves .bg{background:repeating-radial-gradient(circle at 110% -10%,transparent 0 48px,@@ACCENT@@14 48px 50px),repeating-radial-gradient(circle at -10% 110%,transparent 0 60px,@@ACCENT2@@12 60px 62px)}",
 "stripes": ".bgbg-stripes .bg{background-image:repeating-linear-gradient(45deg,transparent 0 26px,@@ACCENT@@0d 26px 28px)}",
 "plain": "",
}
_BG_HTML = {
 "blobs": '<div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div>',
 "mesh": "", "grid": "", "dots": "", "scan": "", "waves": "", "stripes": "", "plain": "",
}
_FONT_CSS = {
 "display": "h1{text-transform:uppercase;letter-spacing:.5px}h2{letter-spacing:.02em}",
 "serif": ".hero h1 span,.big-a,.mh1{font-style:italic}",
 "mono": "h1,h2{letter-spacing:.02em}",
 "sans": "",
 "round": "body{letter-spacing:.1px}h2{font-weight:800}",
}
_SHAPE_CSS = ["", "", "", ""]
_SHAPE_CSS[0] = ".avatar{border-radius:50%}.chip{border-radius:999px}"
_SHAPE_CSS[1] = ".avatar{border-radius:12px}"
_SHAPE_CSS[2] = ".avatar{border-radius:30px}"
_SHAPE_CSS[3] = ".avatar{border-radius:6px}"
_CARD_CSS = {
 "fill": "",
 "outline": ".tl-body,.cproj,footer{background:transparent;border:1px solid var(--line)}",
 "glass": ".tl-body,.cproj,footer{background:color-mix(in srgb,var(--card) 55%,transparent);backdrop-filter:blur(16px)}",
 "hard": ".tl-body,.cproj,footer{box-shadow:6px 6px 0 var(--accent)}",
}
_HERO_CSS = {
 "avatar": "",
 "initials": ".hero .avatar{width:120px;height:120px;border-radius:34px;font-size:2.6rem}",
 "split": ".hero{display:grid;grid-template-columns:1fr auto;gap:30px;align-items:center}.hero .avatar{grid-column:2;grid-row:1/3;width:130px;height:130px}",
 "min": ".hero{padding:40px 0 26px}.hero .lead{max-width:520px}.cta-row{margin-top:18px}",
}
