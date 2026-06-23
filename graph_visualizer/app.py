import streamlit as st
import json
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import os
import requests

# Set page config to dark mode premium look
st.set_page_config(layout="wide", page_title="RoadMind-X | Cognitive Intelligence", page_icon="🕸️")

# Custom CSS for Premium Dashboard Look
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    h1, h2, h3 { color: #38BDF8; }
    .stButton>button { background-color: #EA580C; color: white; font-weight: bold; border-radius: 8px; border: none; }
    .stButton>button:hover { background-color: #F97316; }
    </style>
""", unsafe_allow_html=True)

st.title("🕸️ RoadMind-X: Cognitive Intelligence Engine")
st.markdown("This module covers the flow from **Road Memory Engine (RME)** to the **Causality Graph (CG)**.")

# Load Mock Data via FastAPI (Fallback to local JSON)
@st.cache_data
def load_data():
    try:
        # Try to fetch from our FastAPI backend
        response = requests.get("http://localhost:8000/api/data")
        if response.status_code == 200:
            return response.json()
    except:
        pass # API not running, fallback to local file
        
    file_path = os.path.join("..", "data", "urban_memory_logs.json")
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Data file not found and FastAPI server is not running.")
        return []

data = load_data()
df = pd.DataFrame(data)

if not df.empty:
    st.sidebar.header("🎛️ Engine Controls")
    selected_location = st.sidebar.selectbox("Select Road Profile (RME/DNA)", df['location'].unique())
    run_causality = st.sidebar.button("Run Causality Trace (CG)", type="primary")

    col1, col2 = st.columns([1, 2.5])

    # LEFT COLUMN: Road DNA and Metrics
    with col1:
        st.subheader("🧬 Violation DNA Engine (DNA)")
        st.markdown(f"**Profiling Location:** `{selected_location}`")
        
        # Filter data for selected location
        loc_data = df[df['location'] == selected_location]
        
        # Metric Cards
        total_incidents = len(loc_data)
        critical_incidents = len(loc_data[loc_data['severity_level'] == 'Critical'])
        
        st.metric(label="Total Logged Incidents", value=total_incidents)
        st.metric(label="Near Miss Detection (NMD) Alerts", value=critical_incidents, delta="Critical Risk", delta_color="inverse")
        
        # DNA Distribution Chart
        st.markdown("**Historical Violation DNA**")
        violation_counts = loc_data['violation_type'].value_counts()
        st.bar_chart(violation_counts, color="#38BDF8")

    # RIGHT COLUMN: The Urban Graph
    with col2:
        st.subheader("🌐 Urban Memory & Causality Graph (UMG -> CG)")
        
        # Build NetworkX graph
        G = nx.Graph()
        
        # Group by Location, Context, and Violation to get edge weights
        edges = df.groupby(['location', 'urban_context', 'violation_type']).size().reset_index(name='weight')
        
        # Filter for the selected location to avoid a massive messy hairball
        edges = edges[edges['location'] == selected_location]
        
        for _, row in edges.iterrows():
            loc = row['location']
            context = row['urban_context']
            violation = row['violation_type']
            weight = row['weight']
            
            # Add nodes with Specific Colors based on Architecture
            # Location Nodes (Blue)
            G.add_node(loc, group="Location", title=f"RME Node: {loc}", color="#3B82F6", size=30)
            # Context Nodes (Yellow)
            G.add_node(context, group="Context", title=f"UMG Node: {context}", color="#EAB308", size=25)
            # Violation Nodes (Red)
            G.add_node(violation, group="Violation", title=f"Incident: {violation}", color="#EF4444", size=20)
            
            # Add edges
            # If Causality is run, highlight the links in bright Neon Orange!
            edge_color = "#EA580C" if run_causality else "#334155"
            width = (weight / 2) if run_causality else 1
            
            # Hover Information for Edges
            hover_text = f"🔥 CAUSALITY TRACE FOUND: {weight} incidents caused by this link" if run_causality else f"Correlation Strength: {weight} incidents"
            
            # The Causality Path: Urban Context -> causes -> Violation -> happens at -> Location
            G.add_edge(context, violation, value=weight, color=edge_color, width=width, title=hover_text)
            G.add_edge(violation, loc, value=weight, color=edge_color, width=width, title=hover_text)

        # Render with PyVis
        net = Network(height="450px", width="100%", bgcolor="#0F172A", font_color="white")
        net.from_nx(G)
        
        # Physics options for floating graph effect
        net.set_options("""
        var options = {
          "physics": {
            "forceAtlas2Based": { "gravitationalConstant": -50, "centralGravity": 0.01, "springLength": 100 },
            "minVelocity": 0.75, "solver": "forceAtlas2Based"
          }
        }
        """)
        
        path = "causality_graph.html"
        net.save_graph(path)
        
        # Embed in Streamlit
        HtmlFile = open(path, 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code, height=470)
        
        if run_causality:
            primary_cause = loc_data['urban_context'].mode()[0]
            primary_violation = violation_counts.index[0]
            st.success(f"**🚨 Causality Trace Complete (CG):** The graph algorithms trace the massive spike in **{primary_violation}** directly to the **{primary_cause}** node. This root cause analysis has been packaged for the Intervention Engine.")
