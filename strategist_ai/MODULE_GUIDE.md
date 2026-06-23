# Strategist AI Chatbot (Action Layer)

## 🌍 Global Context
The RoadMind-X system operates in three layers: Perception, Reasoning, and Prevention. 
This module represents **Step 10** of the workflow—the final output. After the CV detects the car, the Graph finds the cause, and the Twin simulates a fix, the authorities need to know what to do in plain English. That is the job of the Strategist AI. It takes complex mathematical data and makes it "Explainable."

## 📊 How it interacts with Data
You will load the `data/urban_memory_logs.json` file. 
You will not show this file to the user. Instead, you will pass this massive JSON block to a Large Language Model (like Gemini or OpenAI) as a *hidden system prompt*. 
You will instruct the LLM: `"You are RoadMind-X Strategist AI. The attached JSON is live city data. Answer the user's questions based strictly on this data."`

## 🛠️ How to Build It
1.  **Tech Stack:** Python, Streamlit, and an LLM API (Google Gemini API is free and fast).
2.  **Interface:** Use `st.chat_input` and `st.chat_message` to build a clean chat interface.
3.  **The Logic Hack:** When the user types: `"Why are there so many violations at City Hospital Junction?"`, the LLM will scan the JSON, see the `urban_context` is "Hospital Shift Change", and reply: *"There has been a 40% spike in Illegal Parking due to the Hospital Shift Change. I recommend we Reroute Traffic, which is simulated to reduce violations by 25%."*
4.  **Integration:** This Streamlit app can later be embedded via an iframe into the Digital Twin Dashboard, creating a seamless unified system.
