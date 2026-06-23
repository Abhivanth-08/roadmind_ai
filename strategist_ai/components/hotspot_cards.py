"""
components/hotspot_cards.py
────────────────────────────
Renders the entire Dashboard tab.

Public API (called from app.py):
    render_dashboard(status, hotspots, sev_counts, health_color)

Architecture Rule:
    This module only renders UI. It does not load data or call APIs.
    All data is passed in as arguments from app.py.
"""

import streamlit as st
from config.settings import COLORS, get_severity_color


# ── Private Helpers ───────────────────────────────────────────────────────────

def _severity_badge_html(severity: str) -> str:
    """Return a styled HTML severity badge string."""
    color = get_severity_color(severity)
    css_class = f"rmx-severity-{severity.lower()}"
    return f'<span class="rmx-severity-badge {css_class}">{severity}</span>'


def _simulation_table_html(simulations: list[dict]) -> str:
    """
    Build an HTML table for the digital twin simulation results.

    Args:
        simulations: List of dicts with keys:
            intervention_tested, forecasted_impact, cost_estimate, recommended (optional)
    """
    rows_html = ""
    for sim in simulations:
        is_rec   = sim.get("recommended", False)
        rec_mark = (
            f'<span style="color:{COLORS["success"]}; font-size:0.7rem; '
            f'font-weight:700;"> &#10003; Recommended</span>'
            if is_rec else ""
        )
        impact     = sim["forecasted_impact"]
        cost       = sim["cost_estimate"]
        intervention = sim["intervention_tested"]

        # Color the impact value
        if impact.startswith("-"):
            impact_color = COLORS["success"]
        else:
            impact_color = COLORS["danger"]

        rows_html += f"""
        <tr>
            <td style="color:{COLORS['text_primary']}; font-size:0.78rem; padding:7px 12px;">
                {intervention}{rec_mark}
            </td>
            <td style="color:{impact_color}; font-weight:600; font-size:0.78rem;
                       padding:7px 12px; font-variant-numeric:tabular-nums;">
                {impact}
            </td>
            <td style="color:{COLORS['text_muted']}; font-size:0.78rem; padding:7px 12px;">
                {cost}
            </td>
        </tr>
        """

    return f"""
    <table style="width:100%; border-collapse:collapse; margin-top:10px;">
        <thead>
            <tr style="border-bottom:1px solid {COLORS['border']};">
                <th style="text-align:left; font-size:0.67rem; font-weight:600;
                           color:{COLORS['text_muted']}; text-transform:uppercase;
                           letter-spacing:0.6px; padding:5px 12px 6px;">
                    Intervention
                </th>
                <th style="text-align:left; font-size:0.67rem; font-weight:600;
                           color:{COLORS['text_muted']}; text-transform:uppercase;
                           letter-spacing:0.6px; padding:5px 12px 6px;">
                    Impact
                </th>
                <th style="text-align:left; font-size:0.67rem; font-weight:600;
                           color:{COLORS['text_muted']}; text-transform:uppercase;
                           letter-spacing:0.6px; padding:5px 12px 6px;">
                    Cost
                </th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    """


def _render_single_card(hotspot: dict) -> None:
    """
    Render one hotspot detail card using st.markdown.

    Args:
        hotspot: A single hotspot dict from ai_context.json
    """
    sev        = hotspot["severity"]
    sev_color  = get_severity_color(sev)
    sev_badge  = _severity_badge_html(sev)
    location   = hotspot["location"]
    issue      = hotspot["current_issue"]
    inc_pct    = hotspot["violation_increase_percentage"]
    rca        = hotspot["root_cause_analysis"]
    primary    = rca.get("primary_cause", "Unknown")
    confidence = int(rca.get("causality_confidence", 0) * 100)
    sims       = hotspot.get("digital_twin_simulations", [])

    # Build simulation table (or placeholder)
    sim_html = _simulation_table_html(sims) if sims else (
        f'<p style="color:{COLORS["text_muted"]}; font-size:0.78rem; '
        f'padding:8px 0;">No simulation data available.</p>'
    )

    # Card HTML — built in sections to avoid complex nested f-strings
    card_header = f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-start;
                margin-bottom:10px;">
        <div>
            <div style="font-size:0.95rem; font-weight:700;
                        color:{COLORS['text_primary']}; margin-bottom:3px;">
                {location}
            </div>
            <div style="font-size:0.78rem; color:{COLORS['text_muted']};">{issue}</div>
        </div>
        {sev_badge}
    </div>
    """

    violation_bar = f"""
    <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
        <div style="font-size:1.6rem; font-weight:800; color:{sev_color};
                    font-variant-numeric:tabular-nums; line-height:1;">
            +{inc_pct}%
        </div>
        <div style="font-size:0.72rem; color:{COLORS['text_muted']}; line-height:1.4;">
            violation<br>increase
        </div>
        <div style="flex:1; height:5px; background:{COLORS['bg_tertiary']};
                    border-radius:3px; overflow:hidden; margin-left:6px;">
            <div style="height:100%; background:{sev_color}; border-radius:3px;
                        width:{min(inc_pct * 2, 100)}%;"></div>
        </div>
    </div>
    """

    rca_block = f"""
    <div style="background:{COLORS['bg_tertiary']}; border-radius:8px;
                padding:12px 14px; margin-bottom:12px;">
        <div style="font-size:0.67rem; font-weight:600; color:{COLORS['text_accent']};
                    text-transform:uppercase; letter-spacing:0.7px; margin-bottom:8px;">
            Root Cause Analysis
        </div>
        <div style="font-size:0.8rem; color:{COLORS['text_primary']};
                    font-weight:500; margin-bottom:6px; line-height:1.4;">
            {primary}
        </div>
        <div style="display:flex; align-items:center; gap:8px;">
            <div style="font-size:0.68rem; color:{COLORS['text_muted']};">Confidence</div>
            <div style="flex:1; height:4px; background:{COLORS['border']};
                        border-radius:2px; overflow:hidden;">
                <div style="height:100%; background:{COLORS['text_accent']};
                            border-radius:2px; width:{confidence}%;"></div>
            </div>
            <div style="font-size:0.68rem; font-weight:600;
                        color:{COLORS['text_accent']};
                        font-family:'JetBrains Mono',monospace;">{confidence}%</div>
        </div>
    </div>
    """

    sim_block = f"""
    <div>
        <div style="font-size:0.67rem; font-weight:600; color:{COLORS['text_muted']};
                    text-transform:uppercase; letter-spacing:0.7px;">
            Digital Twin Simulations
        </div>
        {sim_html}
    </div>
    """

    full_card = f"""
    <div style="background:{COLORS['bg_secondary']}; border:1px solid {COLORS['border']};
                border-top:3px solid {sev_color}; border-radius:10px;
                padding:18px 18px 14px; height:100%;">
        {card_header}
        {violation_bar}
        {rca_block}
        {sim_block}
    </div>
    """

    st.html(full_card)


# ── Public API ────────────────────────────────────────────────────────────────

def render_kpi_row(
    status: dict,
    hotspots: list,
    sev_counts: dict,
    health_color: str,
) -> None:
    """
    Render the 4-metric KPI row at the top of the Dashboard tab.

    Metrics:
        1. City Health Score
        2. Active Alerts
        3. Critical / High Zones
        4. Highest Violation Spike location
    """
    k1, k2, k3, k4 = st.columns(4)

    score = status["overall_city_health_score"]
    with k1:
        st.metric(
            label="City Health Score",
            value=f"{score} / 100",
            delta=None,
        )

    with k2:
        alerts = status["active_alerts"]
        st.metric(
            label="Active Alerts",
            value=str(alerts),
            delta=f"{sev_counts['Critical']} Critical",
            delta_color="inverse",
        )

    with k3:
        st.metric(
            label="High Risk Zones",
            value=str(sev_counts["Critical"] + sev_counts["High"]),
            delta=f"{sev_counts['Medium']} Medium",
            delta_color="off",
        )

    with k4:
        # Find the hotspot with the highest violation increase
        worst  = max(hotspots, key=lambda h: h["violation_increase_percentage"])
        worst_pct = worst["violation_increase_percentage"]
        worst_loc = worst["location"]
        # Truncate long names for the metric display
        label_short = worst_loc if len(worst_loc) <= 14 else worst_loc[:13] + "…"
        st.metric(
            label="Highest Spike",
            value=f"+{worst_pct}%",
            delta=label_short,
            delta_color="inverse",
        )

    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)


def render_hotspot_grid(hotspots: list) -> None:
    """
    Render the full-detail hotspot cards in a responsive grid.

    One card per hotspot, laid out in columns.
    """
    # Section header
    st.html(f"""
    <div style="display:flex; align-items:center; justify-content:space-between;
                margin-bottom:12px; margin-top:6px;">
        <div>
            <div style="font-size:0.9rem; font-weight:600;
                        color:{COLORS['text_primary']};">Active Hotspot Analysis</div>
            <div style="font-size:0.75rem; color:{COLORS['text_muted']}; margin-top:2px;">
                Showing {len(hotspots)} active zone{"s" if len(hotspots) != 1 else ""} —
                data from Road Memory Engine &amp; Digital Twin
            </div>
        </div>
        <div style="font-size:0.68rem; color:{COLORS['text_muted']};
                    font-family:'JetBrains Mono',monospace;">
            LIVE
            <span style="display:inline-block; width:6px; height:6px; border-radius:50%;
                         background:{COLORS['success']}; margin-left:5px;
                         vertical-align:middle;"></span>
        </div>
    </div>
    """)


    # Render cards in columns
    cols = st.columns(len(hotspots))
    for col, hotspot in zip(cols, hotspots):
        with col:
            _render_single_card(hotspot)


def render_dashboard(
    status: dict,
    hotspots: list,
    sev_counts: dict,
    health_color: str,
) -> None:
    """
    Master render function for the Dashboard tab.
    Called once from app.py.

    Args:
        status:       system_status dict from ai_context.json
        hotspots:     list of hotspot dicts from ai_context.json
        sev_counts:   dict of severity → count from data_loader
        health_color: hex color string for the current health score
    """
    render_kpi_row(status, hotspots, sev_counts, health_color)
    render_hotspot_grid(hotspots)
