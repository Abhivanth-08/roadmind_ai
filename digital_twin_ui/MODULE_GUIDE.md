# Digital Twin Dashboard (Cognitive Intelligence Layer)

## 🌍 Global Context
This module represents the second half of the **Cognitive Intelligence Engine**. Once the Causality Graph (CG) finds the root cause, city planners need to know where it will spread and how to fix it. 

This Dashboard is the "Command Center". It demonstrates the system forecasting future violations and running a Behavioral Digital Twin to simulate how physical interventions (like adding parking or signs) will fix the traffic.

## 📐 Architecture Alignment (What you must demonstrate)
According to the `README.md` architecture diagram, you must demonstrate the flow from **CG** into the **TIE** node:
*   **VCE:** Violation Contagion Engine (How the violation spreads)
*   **VFE:** Violation Forecast Engine (Predicting the future state)
*   **BDT:** Behavioral Digital Twin (The simulation environment)
*   **TIE:** Traffic Intervention Engine (Testing the fixes)

## 🛠️ Step-by-Step Build Guide
**Tech Stack:** React/Next.js, TailwindCSS, Recharts (for graphs).

1.  **The Interface Layout (BDT):** 
    *   Build a dark, premium SaaS dashboard representing the **Behavioral Digital Twin (BDT)**. 
    *   Center: A map view (can be a static image of a map with HTML overlay markers for hotspots).
2.  **Forecasting (VCE & VFE):** 
    *   Parse the `data/urban_memory_logs.json` file.
    *   Left Panel: Create a Line Chart showing the **Violation Forecast Engine (VFE)** output (e.g., "Predicted Violations: Next 72 Hours").
    *   Include a metric card for the **Violation Contagion Engine (VCE)** showing "Spread Risk: High (Impacting 3 adjacent roads)".
3.  **The Intervention Engine Simulation (TIE - The Hack):**
    *   Below the map, add an "Intervention Testing Console" representing the **TIE**.
    *   Create a dropdown menu where the user selects an action: "Test Intervention: Add 20 Parking Spaces".
    *   When the user clicks "Run Simulation", trigger a CSS animation. 
    *   Dynamically redraw the **VFE** line chart so the curve drops significantly, visually proving that the system simulated a successful intervention inside the Digital Twin.
