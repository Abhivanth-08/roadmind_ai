"""
app.py — RoadMind-X Strategist AI
──────────────────────────────────
Entry point only. This file does exactly three things:
    1. CONFIGURE  — page settings, CSS, environment
    2. LOAD       — data with graceful error handling
    3. WIRE       — assemble sidebar + tab layout by calling components

Architecture Rule:
    No business logic, no AI calls, no data processing here.
    All logic lives in core/, services/, and components/.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from config.settings import (
    PAGE_TITLE,
    PAGE_ICON,
    PAGE_LAYOUT,
    CSS_PATH,
    COLORS,
    get_health_label,
    get_severity_color,
)
from core.data_loader import (
    load_ai_context,
    load_causality_graph,
    get_system_status,
    get_hotspots,
    get_severity_counts,
    get_graph_nodes,
    get_graph_links,
)
from components.hotspot_cards  import render_dashboard
from components.chat_interface import render_chat_interface
from components.forecast_chart import render_forecast_charts
from components.causality_graph import render_causality_graph
from core.prompt_builder        import build_system_prompt

# ── 1. Environment ────────────────────────────────────────────────────────────
load_dotenv()

# ── 2. Page Configuration (must be the first Streamlit call) ──────────────────
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state="expanded",
)

# ── 3. Inject Global CSS ──────────────────────────────────────────────────────
def _inject_css() -> None:
    """Read style.css from disk and inject into the Streamlit app."""
    try:
        css_content = CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found — using default Streamlit styling.")

_inject_css()

# ── 4. Session State Defaults ─────────────────────────────────────────────────
if "messages"     not in st.session_state: st.session_state.messages     = []
if "show_welcome" not in st.session_state: st.session_state.show_welcome = True
if "report"       not in st.session_state: st.session_state.report       = None
if "uploaded_img" not in st.session_state: st.session_state.uploaded_img = None

# ── 5. Load Data (with graceful error handling) ───────────────────────────────
try:
    ai_ctx     = load_ai_context()
    cg         = load_causality_graph()
    status     = get_system_status()
    hotspots   = get_hotspots()
    sev_counts = get_severity_counts()
    graph_nodes = get_graph_nodes()
    graph_links = get_graph_links()
except FileNotFoundError as exc:
    st.error(f"**Data file not found.** {exc}")
    st.info("Make sure `ai_context.json` and `causality_graph.json` are inside the `data/` folder.")
    st.stop()
except ValueError as exc:
    st.error(f"**Invalid data file.** {exc}")
    st.stop()

# ── 6. Derived values ─────────────────────────────────────────────────────────
health_score = status["overall_city_health_score"]
health_label, health_color = get_health_label(health_score)

# ── 7. Build system prompt (once per session, with injected JSON) ─────────────
# Cache in session state so we don't rebuild on every Streamlit rerun
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = build_system_prompt()

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Brand header
    st.markdown(f"""
    <div class="rmx-brand">
        <div class="rmx-brand-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18"
                 viewBox="0 0 24 24" fill="none" stroke="#2F81F7"
                 stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="4" y="4" width="16" height="16" rx="2"/>
                <rect x="9" y="9" width="6" height="6"/>
                <line x1="9" y1="1" x2="9" y2="4"/>
                <line x1="15" y1="1" x2="15" y2="4"/>
                <line x1="9" y1="20" x2="9" y2="23"/>
                <line x1="15" y1="20" x2="15" y2="23"/>
                <line x1="20" y1="9" x2="23" y2="9"/>
                <line x1="20" y1="14" x2="23" y2="14"/>
                <line x1="1" y1="9" x2="4" y2="9"/>
                <line x1="1" y1="14" x2="4" y2="14"/>
            </svg>
        </div>
        <div>
            <div class="rmx-brand-name">RoadMind-X</div>
            <div class="rmx-brand-tagline">Strategist AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── City Health Score ─────────────────────────────────────────────────────
    st.markdown('<div class="rmx-section-label">City Health Score</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="rmx-health-card">
        <div>
            <div class="rmx-health-score" style="color:{health_color};">{health_score}</div>
            <div style="font-size:0.65rem; color:{COLORS['text_muted']}; margin-top:2px;">/100</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:0.68rem; font-weight:700; color:{health_color};
                        text-transform:uppercase; letter-spacing:0.8px;">{health_label}</div>
            <div style="font-size:0.65rem; color:{COLORS['text_muted']}; margin-top:3px;">
                {status['last_updated'][11:16]} UTC
            </div>
        </div>
    </div>
    <div class="rmx-health-bar-bg">
        <div class="rmx-health-bar-fill"
             style="width:{health_score}%; background:{health_color};"></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Active Alerts ─────────────────────────────────────────────────────────
    st.markdown('<div class="rmx-section-label">System Alerts</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="margin-bottom:14px;">
        <span class="rmx-alert-pill">
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12"
                 viewBox="0 0 24 24" fill="none" stroke="currentColor"
                 stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94
                         a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            {status['active_alerts']} Active Alert{"s" if status["active_alerts"] != 1 else ""}
        </span>
        &nbsp;
        <span style="font-size:0.7rem; color:{COLORS['text_muted']};">
            C:{sev_counts['Critical']} &nbsp;H:{sev_counts['High']} &nbsp;M:{sev_counts['Medium']}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Live Hotspots ─────────────────────────────────────────────────────────
    st.markdown('<div class="rmx-section-label">Live Hotspots</div>', unsafe_allow_html=True)
    for h in hotspots:
        sev       = h["severity"]
        sev_color = get_severity_color(sev)
        sev_cls   = f"rmx-severity-{sev.lower()}"
        conf_pct  = int(h["root_cause_analysis"]["causality_confidence"] * 100)
        inc_pct   = h["violation_increase_percentage"]

        st.markdown(f"""
        <div class="rmx-hotspot-card" style="border-left:3px solid {sev_color};">
            <div class="rmx-hotspot-header">
                <span class="rmx-hotspot-location">{h['location']}</span>
                <span class="rmx-severity-badge {sev_cls}">{sev}</span>
            </div>
            <div class="rmx-hotspot-issue">{h['current_issue']}</div>
            <div class="rmx-hotspot-footer">
                <span class="rmx-violation-increase" style="color:{sev_color};">
                    +{inc_pct}% violations
                </span>
                <span class="rmx-confidence">conf {conf_pct}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="rmx-divider">', unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:0.67rem; color:{COLORS["text_muted"]}; line-height:1.8;">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;">llama-3.3-70b</span><br>'
        f'<span style="font-family:\'JetBrains Mono\',monospace; font-size:0.62rem; color:{COLORS["text_muted"]}">vision: llama-4-scout</span><br>'
        f'RoadMind-X TSA Node v1.0</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN AREA — Header
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="rmx-page-header">
    <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
        <h1 class="rmx-page-title">Traffic Strategist AI</h1>
        <span class="rmx-tsa-badge">
            <span class="rmx-status-dot online"></span>
            TSA Node Active
        </span>
    </div>
    <p class="rmx-page-subtitle">
        RoadMind-X Cognitive Intelligence Layer &mdash;
        Converting traffic data into actionable city intelligence.
    </p>
    <div>
        <span class="rmx-output-chip">O1 Violation Report</span>
        <span class="rmx-output-chip">O2 Hotspot Detection</span>
        <span class="rmx-output-chip">O3 Root Cause</span>
        <span class="rmx-output-chip">O4 Forecast</span>
        <span class="rmx-output-chip">O5 Policy</span>
        <span class="rmx-output-chip">O6 Dyn. Management</span>
        <span class="rmx-output-chip">O7 Exec. Summary</span>
    </div>
</div>
<hr class="rmx-divider" style="margin:14px 0 0;">
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════
TAB_DASHBOARD  = "  Dashboard  "
TAB_STRATEGIST = "  Strategist AI  "
TAB_GRAPH      = "  Causality Graph  "

tab_dash, tab_ai, tab_graph = st.tabs([TAB_DASHBOARD, TAB_STRATEGIST, TAB_GRAPH])

# ── Tab 1: Dashboard ──────────────────────────────────────────────────────────
with tab_dash:
    render_dashboard(
        status=status,
        hotspots=hotspots,
        sev_counts=sev_counts,
        health_color=health_color,
    )
    render_forecast_charts(hotspots, sev_counts)

# ── Tab 2: Strategist AI ──────────────────────────────────────────────────────
with tab_ai:
    render_chat_interface(st.session_state.system_prompt)

# ── Tab 3: Causality Graph ──────────────────────────────────────────────────────
with tab_graph:
    render_causality_graph(graph_nodes, graph_links)