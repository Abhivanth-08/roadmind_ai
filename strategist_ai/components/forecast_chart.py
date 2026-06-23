"""
components/forecast_chart.py
──────────────────────────────
Plotly-based forecast and analytics charts for the Dashboard tab.

Public API:
    render_forecast_charts(hotspots, sev_counts)
"""

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd

from config.settings import COLORS


def _make_violation_bar(hotspots: list) -> go.Figure:
    """Horizontal bar chart — violation increase % by location."""
    locs   = [h["location"] for h in hotspots]
    values = [h["violation_increase_percentage"] for h in hotspots]
    sevs   = [h["severity"] for h in hotspots]

    color_map = {
        "Critical": COLORS["sev_critical"],
        "High":     COLORS["sev_high"],
        "Medium":   COLORS["sev_medium"],
        "Low":      COLORS["sev_low"],
    }
    bar_colors = [color_map.get(s, COLORS["info"]) for s in sevs]

    fig = go.Figure(go.Bar(
        x=values,
        y=locs,
        orientation="h",
        marker=dict(color=bar_colors, line=dict(width=0)),
        text=[f"+{v}%" for v in values],
        textposition="outside",
        textfont=dict(color=COLORS["text_primary"], size=12, family="JetBrains Mono"),
        hovertemplate="<b>%{y}</b><br>Increase: +%{x}%<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text="Violation Increase by Hotspot",
            font=dict(color=COLORS["text_primary"], size=13, family="Inter"),
            x=0,
        ),
        paper_bgcolor=COLORS["bg_secondary"],
        plot_bgcolor=COLORS["bg_secondary"],
        font=dict(color=COLORS["text_muted"], family="Inter"),
        height=230,
        margin=dict(l=10, r=60, t=40, b=10),
        xaxis=dict(
            showgrid=True,
            gridcolor=COLORS["border"],
            tickcolor=COLORS["text_muted"],
            tickfont=dict(size=11),
            zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(size=11, color=COLORS["text_primary"]),
            tickcolor=COLORS["border"],
        ),
    )
    return fig


def _make_severity_donut(sev_counts: dict) -> go.Figure:
    """Donut chart — hotspot severity distribution."""
    labels = [k for k, v in sev_counts.items() if v > 0]
    values = [v for v in sev_counts.values() if v > 0]
    colors = [
        COLORS["sev_critical"],
        COLORS["sev_high"],
        COLORS["sev_medium"],
        COLORS["sev_low"],
    ][:len(labels)]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors, line=dict(color=COLORS["bg_secondary"], width=2)),
        textfont=dict(color=COLORS["text_primary"], size=11, family="Inter"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(
            text="Severity Distribution",
            font=dict(color=COLORS["text_primary"], size=13, family="Inter"),
            x=0,
        ),
        paper_bgcolor=COLORS["bg_secondary"],
        plot_bgcolor=COLORS["bg_secondary"],
        font=dict(color=COLORS["text_muted"], family="Inter"),
        height=230,
        margin=dict(l=10, r=10, t=40, b=10),
        showlegend=True,
        legend=dict(
            font=dict(color=COLORS["text_muted"], size=11),
            bgcolor="rgba(0,0,0,0)",
            orientation="v",
            x=1.0,
        ),
    )
    return fig


def _make_forecast_trend(hotspots: list) -> go.Figure:
    """Multi-line simulated forecast trend over 72 hours."""
    hours = [0, 6, 12, 24, 48, 72]

    fig = go.Figure()
    colors_cycle = [COLORS["sev_critical"], COLORS["sev_high"], COLORS["sev_medium"]]

    for idx, h in enumerate(hotspots):
        base   = h["violation_increase_percentage"]
        # Simulate a realistic growth curve from current baseline
        trend = [
            0,
            round(base * 0.3, 1),
            round(base * 0.6, 1),
            round(base * 1.0, 1),
            round(base * 1.35, 1),
            round(base * 1.65, 1),
        ]
        fig.add_trace(go.Scatter(
            x=hours,
            y=trend,
            mode="lines+markers",
            name=h["location"],
            line=dict(color=colors_cycle[idx % len(colors_cycle)], width=2),
            marker=dict(size=5),
            hovertemplate=f"<b>{h['location']}</b><br>+%{{y}}% at +%{{x}}h<extra></extra>",
        ))

    fig.update_layout(
        title=dict(
            text="72-Hour Violation Forecast",
            font=dict(color=COLORS["text_primary"], size=13, family="Inter"),
            x=0,
        ),
        paper_bgcolor=COLORS["bg_secondary"],
        plot_bgcolor=COLORS["bg_secondary"],
        font=dict(color=COLORS["text_muted"], family="Inter"),
        height=230,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(
            title="Hours from Now",
            showgrid=True,
            gridcolor=COLORS["border"],
            tickvals=hours,
            ticktext=[f"+{h}h" for h in hours],
            tickfont=dict(size=10),
            zeroline=False,
        ),
        yaxis=dict(
            title="Violation Increase (%)",
            showgrid=True,
            gridcolor=COLORS["border"],
            tickfont=dict(size=10),
        ),
        legend=dict(
            font=dict(color=COLORS["text_muted"], size=10),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            y=-0.25,
        ),
    )
    return fig


def render_forecast_charts(hotspots: list, sev_counts: dict) -> None:
    """
    Render all three analytics charts in the Dashboard tab.
    Called from app.py after render_dashboard().
    """
    st.markdown(
        f"<div style='height:18px;'></div>"
        f"<div style='font-size:0.9rem; font-weight:600; color:{COLORS['text_primary']};"
        f"margin-bottom:12px;'>Analytics & Forecast</div>",
        unsafe_allow_html=True,
    )

    col_bar, col_donut = st.columns([2, 1])
    with col_bar:
        st.plotly_chart(
            _make_violation_bar(hotspots),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with col_donut:
        st.plotly_chart(
            _make_severity_donut(sev_counts),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    st.plotly_chart(
        _make_forecast_trend(hotspots),
        use_container_width=True,
        config={"displayModeBar": False},
    )
