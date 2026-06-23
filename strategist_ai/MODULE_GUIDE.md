# Strategist AI Chatbot (Cognitive Intelligence to Actionable Outputs)

## 🌍 Global Context
This module represents the final bridging node (`TSA` - Traffic Strategist AI) in the RoadMind-X pipeline. According to the architecture diagram, it sits at the very end of the **Cognitive Intelligence Engine** and is responsible for feeding all 7 of the **Actionable Outputs** (O1 to O7). 

After the CV Layer collects data, the Graph finds the root cause, and the Digital Twin/Intervention Engine simulates the fix, the Strategist AI translates these complex mathematical simulations into human-readable policies and dashboards.

## 📐 Architecture Alignment & Aesthetics
According to the `README.md` architecture diagram, the Strategist AI MUST directly output or address:
1.  **O1 & O2:** Violation Reports & Hotspot Detection
2.  **O3 & O4:** Root Cause Analysis & Future Violation Forecast
3.  **O5 & O6:** Policy Recommendations & Dynamic Traffic Management
4.  **Multimodal & Visual:** The AI shouldn't just output text; it should output charts, tables, and metrics directly inside the chat window.
5.  **Premium Aesthetics:** It must be set to a dark "cyber" theme so it looks like enterprise command-center software.

## 🛠️ Step-by-Step Build Guide
**Tech Stack:** Python, Streamlit (configured to Dark Mode), and the Gemini Vision API.

1.  **The Hidden Brain (`ai_context.json`):** 
    *   Load the `ai_context.json` file in your Python script.
    *   Prepend this JSON data to the system prompt (invisible to the user).
    *   *System Prompt Example:* `"You are RoadMind-X Strategist AI. You analyze urban graphs and digital twin simulations. Based strictly on the attached JSON data, generate Violation Reports, Root Cause Analysis, and Policy Recommendations. Always format your responses using markdown tables and bullet points."*

2.  **The User Interface & Image Upload:**
    *   Use `st.sidebar` to display the "Overall City Health Score" and "Active Alerts" directly from the JSON so the UI feels alive.
    *   Add `st.file_uploader` so the user can upload a fake CCTV snapshot of a traffic jam.

3.  **The Live Demo Chat (How the AI MUST Reply):**
    *   **User Uploads:** A picture of traffic at MG Road.
    *   **User Types:** `"Generate a hotspot report for this frame, including the root cause analysis and a policy recommendation."`
    *   **AI Replies:** The AI scans the image and the JSON, hitting all your architecture nodes:
        *   **Hotspot & Root Cause (O2, O3):** *"I have cross-referenced the image. The hotspot is **MG Road**, and the root cause is a **Hospital Shift Change**."*
        *   **Future Forecast (O4):** *"Violations are forecasted to rise by 18%."*
        *   **Policy Recommendation & Dynamic Mgmt (O5, O6):** A Markdown table comparing interventions (e.g., Deploy Police vs. Dynamic Signs).
        *   *Streamlit Hack:* If you are using Streamlit, you can write a python `if` condition to dynamically render a small `st.bar_chart()` *inside the chat message* showing the predicted drop in violations.

4.  **Integration (O7 - Smart City Dashboard):** This Streamlit app will ultimately run on a local port, and it can be embedded directly into the Digital Twin Dashboard UI using an HTML `<iframe>`, creating the final unified O7 Smart City Dashboard.
