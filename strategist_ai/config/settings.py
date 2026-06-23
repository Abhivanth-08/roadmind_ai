"""
config/settings.py
──────────────────
Single source of truth for all configuration constants.

Architecture Rule: No magic strings or numbers anywhere else in the codebase.
If a value is used in more than one place, it belongs here.
"""

import os
from pathlib import Path

# ── Project Root ──────────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent

# ── Data File Paths ───────────────────────────────────────────────────────────
DATA_DIR              = ROOT_DIR / "data"
AI_CONTEXT_PATH       = DATA_DIR / "ai_context.json"
CAUSALITY_GRAPH_PATH  = DATA_DIR / "causality_graph.json"

# ── Assets ────────────────────────────────────────────────────────────────────
ASSETS_DIR    = ROOT_DIR / "assets"
CSS_PATH      = ASSETS_DIR / "style.css"

# ── PyVis output (written at runtime, served inline) ─────────────────────────
GRAPH_OUTPUT_PATH = ROOT_DIR / "components" / "causality_output.html"

# ── Groq Model Configuration ──────────────────────────────────────────────────────
GROQ_TEXT_MODEL   = "llama-3.3-70b-versatile"              # text-only queries
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # image + text
GROQ_TEMPERATURE  = 0.3    # lower = more factual
GROQ_MAX_TOKENS   = 8192

# Aliases used by service layer (single import point)
GEMINI_TEXT_MODEL   = GROQ_TEXT_MODEL    # kept for backward compat
GEMINI_TEMPERATURE  = GROQ_TEMPERATURE
GEMINI_MAX_TOKENS   = GROQ_MAX_TOKENS

# ── UI — Page Configuration ───────────────────────────────────────────────────
PAGE_TITLE  = "RoadMind-X | Traffic Strategist AI"
PAGE_ICON   = "🧠"
PAGE_LAYOUT = "wide"

# ── UI — Dark Theme Color Tokens ──────────────────────────────────────────────
# These are the canonical colors for the entire UI layer.
# All components import from here; no hardcoded hex values in component files.

COLORS = {
    # Backgrounds
    "bg_primary":    "#0D1117",   # App background
    "bg_secondary":  "#161B22",   # Cards, panels
    "bg_tertiary":   "#21262D",   # Inputs, nested surfaces

    # Borders
    "border":        "#30363D",   # Default border
    "border_active": "#2F81F7",   # Focused / active state

    # Typography
    "text_primary":  "#E6EDF3",   # Main text
    "text_muted":    "#7D8590",   # Labels, captions
    "text_accent":   "#2F81F7",   # Links, highlights

    # Semantic
    "success":       "#3FB950",   # Good / green
    "warning":       "#D29922",   # Medium / amber
    "danger":        "#F85149",   # Critical / red
    "info":          "#2F81F7",   # Blue accent

    # Severity mapping
    "sev_critical":  "#F85149",
    "sev_high":      "#D29922",
    "sev_medium":    "#E3B341",
    "sev_low":       "#3FB950",

    # Sidebar
    "sidebar_bg":    "#010409",

    # Chart colors
    "chart_blue":    "#2F81F7",
    "chart_orange":  "#D29922",
    "chart_red":     "#F85149",
    "chart_green":   "#3FB950",
    "chart_purple":  "#8957E5",
}

# ── Severity Color Lookup ─────────────────────────────────────────────────────
def get_severity_color(severity: str) -> str:
    """Return the hex color for a given severity string."""
    mapping = {
        "Critical": COLORS["sev_critical"],
        "High":     COLORS["sev_high"],
        "Medium":   COLORS["sev_medium"],
        "Low":      COLORS["sev_low"],
    }
    return mapping.get(severity, COLORS["text_muted"])

# ── Causality Graph — Node Group Colors ──────────────────────────────────────
GRAPH_NODE_COLORS = {
    "Location":  COLORS["info"],
    "Violation": COLORS["danger"],
    "Context":   COLORS["warning"],
}

# ── Health Score Thresholds ───────────────────────────────────────────────────
HEALTH_THRESHOLDS = {
    "good":     80,   # score >= 80 → green
    "moderate": 60,   # score >= 60 → amber
    # below 60  → red / critical
}

def get_health_label(score: int) -> tuple[str, str]:
    """
    Returns (label, color_hex) for a given city health score.

    Usage:
        label, color = get_health_label(72)
    """
    if score >= HEALTH_THRESHOLDS["good"]:
        return "Operational", COLORS["success"]
    elif score >= HEALTH_THRESHOLDS["moderate"]:
        return "Degraded", COLORS["warning"]
    else:
        return "Critical", COLORS["danger"]

# ── Report Section Keys ───────────────────────────────────────────────────────
# Used to parse and render AI report sections consistently.
REPORT_SECTIONS = [
    "Violation Report",
    "Hotspot Detection",
    "Root Cause Analysis",
    "Future Violation Forecast",
    "Policy Recommendations",
    "Dynamic Traffic Management",
    "Executive Summary",
]

# ── Accepted Image MIME Types ─────────────────────────────────────────────────
ACCEPTED_IMAGE_TYPES = ["jpg", "jpeg", "png", "webp"]

# ── Streamlit Cache TTL ───────────────────────────────────────────────────────
CACHE_TTL_SECONDS = 300   # 5 minutes — how long to cache loaded JSON data
