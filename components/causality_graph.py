"""
components/causality_graph.py
───────────────────────────────
Interactive causality graph using NetworkX + PyVis.
Rendered inside Streamlit via st.components.v1.html.

Public API:
    render_causality_graph(nodes, links)
"""

import streamlit as st
import streamlit.components.v1 as components
import networkx as nx
from pyvis.network import Network

from config.settings import COLORS, GRAPH_NODE_COLORS, GRAPH_OUTPUT_PATH


def _build_network(nodes: list, links: list) -> Network:
    """
    Convert JSON graph data into a styled PyVis Network object.

    Node size  = degree centrality (more connections = larger node)
    Edge width = weight value from JSON
    Node color = group type (Location / Violation / Context)
    """
    # Build NetworkX graph for centrality calculation
    G = nx.DiGraph()
    for n in nodes:
        G.add_node(n["id"], group=n.get("group", "Context"))
    for lnk in links:
        G.add_edge(lnk["source"], lnk["target"], weight=lnk.get("weight", 1))

    centrality = nx.degree_centrality(G)

    # Build PyVis network
    net = Network(
        height="680px",
        width="100%",
        directed=True,
        bgcolor=COLORS["bg_primary"],
        font_color=COLORS["text_primary"],
    )

    # Add nodes
    for n in nodes:
        node_id    = n["id"]
        group      = n.get("group", "Context")
        color      = GRAPH_NODE_COLORS.get(group, COLORS["info"])
        size       = 18 + int(centrality.get(node_id, 0) * 60)
        border_col = "#FFFFFF" if group == "Location" else color

        net.add_node(
            node_id,
            label=node_id,
            color={"background": color, "border": border_col,
                   "highlight": {"background": COLORS["text_accent"], "border": "#FFFFFF"}},
            size=size,
            title=f"<b>{node_id}</b><br>Type: {group}<br>Centrality: {centrality.get(node_id, 0):.2f}",
            font={"color": COLORS["text_primary"], "size": 13, "face": "Inter", "bold": False},
        )

    # Add edges
    max_weight = max((lnk.get("weight", 1) for lnk in links), default=1)
    for lnk in links:
        weight     = lnk.get("weight", 1)
        norm_width = 1 + (weight / max_weight) * 5

        net.add_edge(
            lnk["source"],
            lnk["target"],
            width=norm_width,
            color={"color": COLORS["border"], "highlight": COLORS["text_accent"]},
            title=f"Weight: {weight}",
            arrows="to",
            smooth={"type": "curvedCW", "roundness": 0.1},
        )

    # Physics & interaction options
    net.set_options("""
    {
      "physics": {
        "enabled": true,
        "forceAtlas2Based": {
          "gravitationalConstant": -220,
          "centralGravity": 0.003,
          "springLength": 240,
          "springConstant": 0.04,
          "damping": 0.5,
          "avoidOverlap": 1.0
        },
        "solver": "forceAtlas2Based",
        "stabilization": { "iterations": 200, "fit": true },
        "minVelocity": 0.75
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 80,
        "navigationButtons": true,
        "keyboard": false,
        "zoomView": true
      },
      "edges": {
        "smooth": { "type": "continuous", "roundness": 0.2 },
        "length": 260
      },
      "nodes": {
        "scaling": { "min": 16, "max": 50 },
        "margin": 14
      }
    }
    """)

    return net


def _render_legend() -> None:
    """Render a color-coded node group legend."""
    legend_items = [
        ("Location",  GRAPH_NODE_COLORS["Location"],  "Physical road zones"),
        ("Violation", GRAPH_NODE_COLORS["Violation"],  "Traffic violation types"),
        ("Context",   GRAPH_NODE_COLORS["Context"],    "Urban context factors"),
    ]
    items_html = "".join(
        f'<div style="display:flex; align-items:center; gap:7px; margin-right:20px;">'
        f'<div style="width:10px; height:10px; border-radius:50%; background:{col};'
        f'flex-shrink:0;"></div>'
        f'<div>'
        f'<div style="font-size:0.75rem; font-weight:600; color:{COLORS["text_primary"]};">{label}</div>'
        f'<div style="font-size:0.65rem; color:{COLORS["text_muted"]};">{desc}</div>'
        f'</div></div>'
        for label, col, desc in legend_items
    )
    st.html(f"""
    <div style="display:flex; flex-wrap:wrap; gap:6px;
                background:{COLORS['bg_secondary']}; border:1px solid {COLORS['border']};
                border-radius:8px; padding:12px 16px; margin-bottom:14px;">
        {items_html}
    </div>
    """)


def _render_stats(nodes: list, links: list) -> None:
    """Render graph statistics row."""
    groups     = {}
    for n in nodes:
        g = n.get("group", "Context")
        groups[g] = groups.get(g, 0) + 1

    c1, c2, c3, c4 = st.columns(4)
    stats = [
        (c1, str(len(nodes)),                   "Total Nodes"),
        (c2, str(len(links)),                   "Causal Links"),
        (c3, str(groups.get("Location", 0)),    "Locations"),
        (c4, str(groups.get("Violation", 0)),   "Violation Types"),
    ]
    for col, val, label in stats:
        with col:
            st.html(f"""
            <div class="rmx-stat-card">
                <div class="rmx-stat-value">{val}</div>
                <div class="rmx-stat-label">{label}</div>
            </div>
            """)
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)


def render_causality_graph(nodes: list, links: list) -> None:
    """
    Render the complete Causality Graph tab.

    Args:
        nodes: List of node dicts with 'id' and 'group' keys.
        links: List of edge dicts with 'source', 'target', 'weight' keys.
    """
    # Header
    st.html(f"""
    <div style="margin-bottom:14px;">
        <div style="font-size:0.9rem; font-weight:600;
                    color:{COLORS['text_primary']}; margin-bottom:3px;">
            Urban Causality Graph
        </div>
        <div style="font-size:0.76rem; color:{COLORS['text_muted']};">
            Neo4j-style causal network — showing how urban context factors trigger
            traffic violations across hotspot locations. Node size = influence centrality.
            Edge thickness = causal weight.
        </div>
    </div>
    """)

    # Stats row
    _render_stats(nodes, links)

    # Legend
    _render_legend()

    # Build and render the interactive graph
    try:
        net      = _build_network(nodes, links)
        html_str = net.generate_html()

        # Inject dark background override into PyVis HTML
        html_str = html_str.replace(
            "<body>",
            f'<body style="background:{COLORS["bg_primary"]}; margin:0; padding:0;">',
        )

        components.html(html_str, height=700, scrolling=False)

    except Exception as exc:
        st.error(f"Graph rendering error: {exc}")
        st.info("Ensure pyvis is installed: `pip install pyvis==0.3.2`")
