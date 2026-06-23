# Digital Twin Dashboard (Prevention Layer)

## 🌍 Global Context
The RoadMind-X system operates in three layers: Perception, Reasoning, and Prevention. 
This module represents **Step 7, 8, and 9** of the workflow. Once the system has detected violations and found the root cause, it simulates solutions. This Dashboard is the ultimate "Wrapper" of the entire project—the actual software screen the end-user (a city traffic planner) would stare at.

## 📊 How it interacts with Data
You will load the `data/urban_memory_logs.json` file. 
You will parse the data to populate line charts (e.g., violations over the last 30 days) and a summary table of the most critical hotspots. 
The JSON data includes a `simulated_impact` field (e.g., "-25% violations") and a `recommended_intervention` field. You will use these fields to power the "What-If" slider on the dashboard.

## 🛠️ How to Build It
1.  **Tech Stack:** Next.js or React, Tailwind CSS, and Recharts.
2.  **Layout:** Create a premium dark-mode interface. Put a dummy Mapbox or static map in the center. Put a Line Chart on the left showing historical data from the JSON.
3.  **The Logic Hack:** On the right side, build a "Simulation Console." Provide a dropdown for the user to select an intervention (e.g., "Deploy Dynamic Signage"). When they select it, run a fake animation and redraw the line chart to dip down by 25%. 
4.  **Integration:** Leave an empty `<div>` container in the UI. Later, we will paste the Graph Visualizer module inside it.
