# Causality Graph Visualizer (Cognitive Intelligence Layer)

## 🌍 Global Context
This module represents the **Cognitive Intelligence Engine** (Steps 5 & 6). Once the CV Layer has logged evidence, this module takes over. It proves the core innovation of RoadMind-X: moving beyond simple detection by actually *reasoning* about the Root Cause of traffic patterns. 

For the hackathon demo, this will be a standalone web interface that visualizes the "Urban Memory Graph" and the "Causality Trace" algorithms.

## 📐 Architecture Alignment (What you must demonstrate)
According to the pitch deck, this layer MUST show:
1.  **Urban Memory Graph:** Linking roads (internal data) with events (external context).
2.  **Causality Engine:** Tracing the root cause of a violation spike.
3.  **Road Memory & DNA:** Showing the historical profile of a location.

## 🛠️ Step-by-Step Build Guide
**Tech Stack:** React (or vanilla JS/HTML), `react-force-graph` (or D3.js), TailwindCSS.

1.  **The Data Source:** Use the `data/urban_memory_logs.json` file. 
2.  **Building the Graph Nodes:** 
    *   Create three types of nodes in your visualization: 
        *   🔵 **Location Nodes** (e.g., MG Road)
        *   🔴 **Violation Nodes** (e.g., Illegal Parking Spike)
        *   🟡 **Context Nodes** (e.g., Hospital Shift Change, Rain, Festival)
3.  **The Causality Demo (The Hack):** 
    *   The graph should load as a beautiful, floating 2D or 3D network.
    *   Add a large button on the screen: `"Run Causality Analysis: MG Road"`.
    *   When clicked, the app should highlight a specific path through the network (e.g., The line connects `Hospital Shift Change` → `Parking Overflow` → `MG Road Violations`) and dim the rest of the graph.
4.  **Road DNA Panel:** 
    *   When the user clicks on a "Location Node", open a side panel.
    *   The panel should display the "Road DNA Profile" (e.g., "High Risk Time: 6 PM - 8 PM", "Primary Violation: Parking", "Historical Severity: Medium"). This proves the Road Memory Engine concept.
