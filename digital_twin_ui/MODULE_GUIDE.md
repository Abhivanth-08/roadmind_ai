# Digital Twin Dashboard (Actionable Outputs Layer)

## 🌍 Global Context
This module represents the **Actionable Outputs** (Steps 7-9). After the Perception layer detects cars, and the Cognitive layer finds the cause, city planners need a way to actually solve the problem. 

This Dashboard is the "Command Center". It demonstrates the system forecasting future violations and running a Behavioral Digital Twin to simulate how physical interventions (like adding parking or signs) will fix the traffic.

## 📐 Architecture Alignment (What you must demonstrate)
According to the pitch deck, this layer MUST show:
1.  **Contagion & Forecast Engine:** Showing predicted violations before they happen.
2.  **Behavioral Digital Twin:** A map or UI where simulations happen.
3.  **Intervention Engine:** A tool to test solutions (e.g., policy changes, physical signs) and see their simulated impact.

## 🛠️ Step-by-Step Build Guide
**Tech Stack:** React/Next.js, TailwindCSS, Recharts (for graphs).

1.  **The Interface Layout:** 
    *   Build a dark, premium SaaS dashboard. 
    *   Center: A map view (can be a static image of a map with HTML overlay markers for hotspots).
    *   Left Panel: A Line Chart showing "Forecasted Violations" (Next 72 Hours).
2.  **Data Loading:** Parse the `data/urban_memory_logs.json` file to populate the charts. Focus on the `simulated_impact` and `recommended_intervention` fields.
3.  **The Digital Twin Simulation (The Hack):**
    *   Below the map, add an "Intervention Testing Console".
    *   Create a dropdown menu where the user selects an action: "Test Intervention: Add 20 Parking Spaces".
    *   When the user clicks "Run Simulation", trigger a CSS animation. 
    *   Dynamically redraw the "Forecasted Violations" line chart so the curve drops significantly, visually proving that the system simulated a successful intervention.
4.  **Metric Updates:** Update the summary cards on the screen (e.g., change "Predicted Accidents" from 45 to 12). This tangibly demonstrates the "Prevention" value of RoadMind-X.
