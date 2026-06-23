# Causality Graph Visualizer (Cognitive Layer)

## 🌍 Global Context
The RoadMind-X system operates in three layers: Perception, Reasoning, and Prevention. 
This module represents **Step 5 and Step 6** of the workflow. The system has already detected violations (via the CV Layer), but now it needs to figure out *why* they happened. This module is the "brain" linking traffic spikes to urban events (festivals, construction, etc.).

## 📊 How it interacts with Data
You will use the `data/urban_memory_logs.json` file. 
You need to write a script that parses this file and groups the data. For example, if there are 50 "Illegal Parking" events at "MG Road" and they all have the `urban_context` of "Hospital Shift Change", you will generate a node for "MG Road", a node for "Hospital Shift Change", and draw a thick red link between them. 

## 🛠️ How to Build It
1.  **Tech Stack:** Use HTML/JavaScript or React.
2.  **Library:** Import `react-force-graph` or `d3.js`.
3.  **The Logic Hack:** Map the `locations` from the JSON to blue nodes, and `urban_context` to red nodes. The link thickness between them is based on how many violations occur between those two points.
4.  **Interaction:** Make it so when a judge clicks the "MG Road" node, it highlights the exact causality path showing what is causing the traffic there. This visually proves the "Reasoning" aspect of your pitch.
