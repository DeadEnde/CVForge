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
    "minimal": {
        "name": "Snow Minimal",
        "palette": {
            "bg": "#f5f7fb",
            "bg2": "#ffffff",
            "card": "rgba(255,255,255,0.8)",
            "line": "rgba(15,23,42,0.08)",
            "accent": "#0ea5e9",
            "accent2": "#6366f1",
            "text": "#0f172a",
            "muted": "#64748b",
            "bt": "#ffffff"
        },
        "gradient": ["#0ea5e9", "#6366f1", "#8b5cf6"],
        "font_style": "modern", "radius": "14px",
    },
    "classic": {
        "name": "Paper & Ink",
        "palette": {
            "bg": "#f6f1e7",
            "bg2": "#fdfaf3",
            "card": "rgba(255,253,247,0.8)",
            "line": "rgba(41,37,36,0.12)",
            "accent": "#b45309",
            "accent2": "#57534e",
            "text": "#292524",
            "muted": "#78716c",
            "bt": "#ffffff"
        },
        "gradient": ["#c2410c", "#b45309", "#78716c"],
        "font_style": "elegant", "radius": "6px",
    },
    "corporate": {
        "name": "Corporate Pro",
        "palette": {
            "bg": "#f8fafc",
            "bg2": "#ffffff",
            "card": "rgba(255,255,255,0.85)",
            "line": "rgba(15,23,42,0.08)",
            "accent": "#1d4ed8",
            "accent2": "#0ea5e9",
            "text": "#0f172a",
            "muted": "#64748b",
            "bt": "#ffffff"
        },
        "gradient": ["#1d4ed8", "#3b82f6", "#0ea5e9"],
        "font_style": "modern", "radius": "10px",
    },
    "pastel": {
        "name": "Playful Pastel",
        "palette": {
            "bg": "#fdf2f8",
            "bg2": "#fefce8",
            "card": "rgba(255,255,255,0.75)",
            "line": "rgba(76,29,149,0.10)",
            "accent": "#ec4899",
            "accent2": "#8b5cf6",
            "text": "#3d3a5c",
            "muted": "#8d84a8",
            "bt": "#ffffff"
        },
        "gradient": ["#f472b6", "#a78bfa", "#60a5fa"],
        "font_style": "modern", "radius": "24px",
    },
    "cyber": {
        "name": "Neon Cyber",
        "palette": {
            "bg": "#050014",
            "bg2": "#0a0220",
            "card": "rgba(255,79,216,0.06)",
            "line": "rgba(255,79,216,0.22)",
            "accent": "#ff2fd6",
            "accent2": "#00f0ff",
            "text": "#f2eaff",
            "muted": "#9d8fd0"
        },
        "gradient": ["#ff2fd6", "#00f0ff", "#7c3aed"],
        "font_style": "mono-touch", "radius": "6px",
    },
    "retro": {
        "name": "Retro Terminal",
        "palette": {
            "bg": "#0a0f0a",
            "bg2": "#0d140d",
            "card": "rgba(0,255,65,0.05)",
            "line": "rgba(0,255,65,0.20)",
            "accent": "#00ff41",
            "accent2": "#39ff14",
            "text": "#d9ffdd",
            "muted": "#6da372"
        },
        "gradient": ["#00ff41", "#39ff14", "#4ade80"],
        "font_style": "mono-touch", "radius": "4px",
    },
    "gold": {
        "name": "Luxury Gold",
        "palette": {
            "bg": "#0c0a07",
            "bg2": "#14110a",
            "card": "rgba(255,255,255,0.04)",
            "line": "rgba(234,179,8,0.25)",
            "accent": "#eab308",
            "accent2": "#fef3c7",
            "text": "#faf6ea",
            "muted": "#a89b84",
            "bt": "#1a1206"
        },
        "gradient": ["#b8860b", "#eab308", "#fef3c7"],
        "font_style": "elegant", "radius": "4px",
    },
    "glass": {
        "name": "Liquid Glass",
        "palette": {
            "bg": "#070b1e",
            "bg2": "#0b1030",
            "card": "rgba(255,255,255,0.09)",
            "line": "rgba(255,255,255,0.16)",
            "accent": "#5eead4",
            "accent2": "#a5b4fc",
            "text": "#f0f4ff",
            "muted": "#9aa7d8"
        },
        "gradient": ["#22d3ee", "#818cf8", "#f472b6"],
        "font_style": "modern", "radius": "26px",
    },
    "noir": {
        "name": "Noir Mono",
        "palette": {
            "bg": "#0a0a0a",
            "bg2": "#121212",
            "card": "rgba(255,255,255,0.06)",
            "line": "rgba(255,255,255,0.14)",
            "accent": "#ffffff",
            "accent2": "#a3a3a3",
            "text": "#f5f5f5",
            "muted": "#9ca3af"
        },
        "gradient": ["#525252", "#737373", "#a3a3a3"],
        "font_style": "modern", "radius": "2px",
    },
    "ocean": {
        "name": "Deep Ocean",
        "palette": {
            "bg": "#041220",
            "bg2": "#07223a",
            "card": "rgba(255,255,255,0.05)",
            "line": "rgba(34,211,238,0.22)",
            "accent": "#22d3ee",
            "accent2": "#60a5fa",
            "text": "#e8f6ff",
            "muted": "#8fb0cc"
        },
        "gradient": ["#0ea5e9", "#22d3ee", "#3b82f6"],
        "font_style": "modern", "radius": "22px",
    },
    "forest": {
        "name": "Deep Forest",
        "palette": {
            "bg": "#07130c",
            "bg2": "#0c1e13",
            "card": "rgba(255,255,255,0.05)",
            "line": "rgba(74,222,128,0.20)",
            "accent": "#34d399",
            "accent2": "#a3e635",
            "text": "#eaf7ee",
            "muted": "#93b5a0"
        },
        "gradient": ["#10b981", "#84cc16", "#22c55e"],
        "font_style": "modern", "radius": "18px",
    },
    "royal": {
        "name": "Royal Violet",
        "palette": {
            "bg": "#0d0718",
            "bg2": "#170b2e",
            "card": "rgba(255,255,255,0.05)",
            "line": "rgba(167,139,250,0.25)",
            "accent": "#a78bfa",
            "accent2": "#f0abfc",
            "text": "#f4efff",
            "muted": "#ab9bd8"
        },
        "gradient": ["#7c3aed", "#a78bfa", "#f0abfc"],
        "font_style": "serif-touch", "radius": "22px",
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
