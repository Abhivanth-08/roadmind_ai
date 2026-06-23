# Strategist AI Chatbot (Actionable Outputs Layer)

## 🌍 Global Context
This module represents the final **Step 10** of the pipeline. The CV Layer collected the data, the Graph found the root cause, and the Digital Twin simulated the fix. But raw data and charts can be overwhelming for government officials. 

The Strategist AI acts as the translation layer. It is an explainable LLM that turns complex mathematical simulations into clear, actionable, plain-English policies for city planners.

## 📐 Architecture Alignment (What you must demonstrate)
According to the pitch deck, this layer MUST show:
1.  **Explainable AI Outputs:** Translating raw causality paths into human-readable advice.
2.  **Confidence-Ranked Recommendations:** Providing the planner with the highest-probability fix.
3.  **Cross-layer Awareness:** Proving the Chatbot actually "knows" about the Graph and Digital Twin data.

## 🛠️ Step-by-Step Build Guide
**Tech Stack:** Python, Streamlit, Google Gemini API (or OpenAI).

1.  **The LLM Integration:** Set up a simple Streamlit interface with a chat box. Connect it to the Gemini API using an API key.
2.  **Context Injection (The Hack):** 
    *   Load the `data/urban_memory_logs.json` file in Python.
    *   Prepend this JSON data to the system prompt (invisible to the user).
    *   System Prompt Example: `"You are RoadMind-X Strategist AI. You analyze urban memory graphs and digital twin simulations. Based on the attached JSON data, answer user questions like an expert traffic advisor."`
3.  **The Live Demo Chat:**
    *   **User Types:** `"Why are violations up by 18% on MG Road today, and what should we do?"`
    *   **AI Replies:** The AI scans the JSON, notices the "Hospital Shift Change" cause and the simulated intervention data. It should output a beautifully formatted markdown response:
        *   **Root Cause:** "Urban Graph traces the spike to a Hospital Shift Change."
        *   **Recommended Action:** "Deploy dynamic parking signs."
        *   **Simulated Impact:** "Digital Twin forecasts a 25% reduction in violations."
4.  **Integration:** This Streamlit app will ultimately run on a local port, and Niranjana can embed it directly into the Digital Twin Dashboard UI using an HTML `<iframe>`, creating the final unified product.
