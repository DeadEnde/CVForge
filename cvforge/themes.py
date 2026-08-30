"""CVForge — design themes per domain (modern, glassmorphism, mobile-first)."""

THEMES: dict[str, dict] = {
    "developer": {
        "name": "Neon Code",
        "palette": {
            "bg": "#070b14", "bg2": "#0b1220", "card": "rgba(255,255,255,0.05)",
            "accent": "#6366f1", "accent2": "#22d3ee", "text": "#e7ecf6", "muted": "#8b93a7",
        },
        "gradient": ["#6366f1", "#22d3ee", "#a855f7"],
        "font_style": "mono-touch", "radius": "18px",
    },
    "designer": {
        "name": "Studio Rose",
        "palette": {
            "bg": "#140a12", "bg2": "#1b0e18", "card": "rgba(255,255,255,0.06)",
            "accent": "#f472b6", "accent2": "#fb923c", "text": "#f8edf4", "muted": "#a3909e",
        },
        "gradient": ["#f472b6", "#fb923c", "#facc15"],
        "font_style": "serif-touch", "radius": "28px",
    },
    "photographer": {
        "name": "Golden Hour",
        "palette": {
            "bg": "#0d0b09", "bg2": "#14110c", "card": "rgba(255,255,255,0.05)",
            "accent": "#f59e0b", "accent2": "#fde68a", "text": "#f5efe4", "muted": "#9c9284",
        },
        "gradient": ["#f59e0b", "#fbbf24", "#78716c"],
        "font_style": "elegant", "radius": "12px",
    },
    "marketer": {
        "name": "Growth Green",
        "palette": {
            "bg": "#06120e", "bg2": "#0a1a14", "card": "rgba(255,255,255,0.05)",
            "accent": "#34d399", "accent2": "#4ade80", "text": "#eaf6ef", "muted": "#8aa79a",
        },
        "gradient": ["#34d399", "#4ade80", "#a3e635"],
        "font_style": "modern", "radius": "20px",
    },
    "data": {
        "name": "Data Pulse",
        "palette": {
            "bg": "#080a12", "bg2": "#0c101e", "card": "rgba(255,255,255,0.05)",
            "accent": "#818cf8", "accent2": "#2dd4bf", "text": "#e8ecf7", "muted": "#8a92a8",
        },
        "gradient": ["#6366f1", "#2dd4bf", "#0ea5e9"],
        "font_style": "mono-touch", "radius": "16px",
    },
    "manager": {
        "name": "Executive",
        "palette": {
            "bg": "#0c0d10", "bg2": "#12141a", "card": "rgba(255,255,255,0.05)",
            "accent": "#f8fafc", "accent2": "#94a3b8", "text": "#f1f5f9", "muted": "#94a3b8",
        },
        "gradient": ["#e2e8f0", "#94a3b8", "#475569"],
        "font_style": "minimal", "radius": "10px",
    },
    "teacher": {
        "name": "Scholar",
        "palette": {
            "bg": "#0d1014", "bg2": "#131820", "card": "rgba(255,255,255,0.05)",
            "accent": "#60a5fa", "accent2": "#fbbf24", "text": "#eef2f7", "muted": "#8f9aad",
        },
        "gradient": ["#60a5fa", "#fbbf24", "#34d399"],
        "font_style": "serif", "radius": "14px",
    },
    "finance": {
        "name": "Fintech",
        "palette": {
            "bg": "#0a0f0c", "bg2": "#101712", "card": "rgba(255,255,255,0.05)",
            "accent": "#10b981", "accent2": "#facc15", "text": "#ecf5ef", "muted": "#8fa295",
        },
        "gradient": ["#10b981", "#facc15", "#34d399"],
        "font_style": "modern", "radius": "12px",
    },
    "health": {
        "name": "Care",
        "palette": {
            "bg": "#0a0f12", "bg2": "#0f161b", "card": "rgba(255,255,255,0.05)",
            "accent": "#38bdf8", "accent2": "#f472b6", "text": "#eaf3f8", "muted": "#8aa0ad",
        },
        "gradient": ["#38bdf8", "#f472b6", "#a5b4fc"],
        "font_style": "modern", "radius": "18px",
    },
    "engineer": {
        "name": "Builder",
        "palette": {
            "bg": "#0b0e10", "bg2": "#121619", "card": "rgba(255,255,255,0.05)",
            "accent": "#f97316", "accent2": "#fbbf24", "text": "#f2f4f6", "muted": "#96a0a8",
        },
        "gradient": ["#f97316", "#fbbf24", "#ef4444"],
        "font_style": "industrial", "radius": "10px",
    },
    "generic": {
        "name": "Aurora",
        "palette": {
            "bg": "#0a0c14", "bg2": "#10131f", "card": "rgba(255,255,255,0.05)",
            "accent": "#a78bfa", "accent2": "#f472b6", "text": "#eef0f8", "muted": "#8d93a8",
        },
        "gradient": ["#a78bfa", "#f472b6", "#38bdf8"],
        "font_style": "modern", "radius": "20px",
    },
}

EXTRA_THEMES = {
    "midnight": "Dark navy + electric blue",
    "emerald": "Deep green + mint",
    "sunset": "Dark + warm orange/pink",
}


def get_theme(domain: str, custom: str | None = None) -> dict:
    if custom and custom in THEMES:
        return THEMES[custom]
    return THEMES.get(domain, THEMES["generic"])
