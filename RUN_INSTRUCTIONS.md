# 🕸️ RoadMind-X: Running the Cognitive Traffic Intelligence Platform

RoadMind-X is an end-to-end traffic management and prediction pipeline. It is divided into 4 core functional modules:
1. **CV Perception Tracker (`cv_tracker`)**: Transforms video feeds into vehicle detections, counts, and logs congestion events.
2. **Causality Graph Visualizer (`graph_visualizer`)**: Relates traffic congestion hotspots to urban events (festivals, hospital shifts, construction).
3. **Behavioral Digital Twin (`digital_twin_ui`)**: Simulates traffic interventions (e.g., adding parking, dynamic signs) and forecasts outcomes.
4. **Traffic Strategist AI (`strategist_ai`)**: A dark-theme chat dashboard that interprets simulations into policy reports.

---

## ⚡ Quick Start: Run Everything Automatically (Recommended)

An automated launcher script `run_all.sh` is provided in the project root. It will:
- Set up a unified python virtual environment and install all packages.
- Run `npm install` for the frontend.
- Launch all 5 backend/frontend components in separate macOS Terminal windows so you can see all outputs and log streams simultaneously.

### Steps:
1. Open your terminal in the repository root.
2. Ensure you have Node.js / npm installed (`node -v` and `npm -v`).
3. Set your environment variables in the `.env` file in the root directory (see **Environment Configuration** below).
4. Run the launcher script:
   ```bash
   ./run_all.sh
   ```

---

## 🔑 Environment Configuration

Ensure your `.env` file in the project root contains your PostgreSQL connection string and your Groq API Key (required for the Traffic Strategist AI):

```env
# Database configuration for Road Memory
POSTGRES_CONN_STRING=postgresql://username:password@hostname/dbname?sslmode=require

# Groq API key for Strategist AI Chatbot (llama models)
GROQ_API_KEY=gsk_your_actual_key_here
```

---

## 🌐 Port Map

Once started, the services can be accessed at:

| Component | Port / URL | Description |
| :--- | :--- | :--- |
| **Digital Twin React UI** | [http://localhost:5173](http://localhost:5173) | Main dashboard showing traffic simulation controls. |
| **Digital Twin API Backend** | [http://localhost:8000](http://localhost:8000) | FastAPI endpoint processing interventions. |
| **Causality Graph UI** | [http://localhost:8501](http://localhost:8501) | Streamlit dashboard visualising causal node graphs. |
| **Traffic Strategist AI** | [http://localhost:8502](http://localhost:8502) | Streamlit chatbot workspace translating metrics into policy advice. |
| **CV Tracker** | GUI Window / `cv_tracker/outputs/` | Interactive video process screen showing real-time HUD metrics. |

---

## 🛠️ Running Modules Individually (Manual Startup)

If you prefer to run services manually, follow the steps below. We recommend setting up a single virtual environment at the repository root to avoid installing duplicate packages.

### 0. Prepare Python Environment (Root Directory)
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all package dependencies
pip install -r requirements.txt
```

---

### Module 1: CV Perception Tracker
Processes the traffic feed, tracks vehicle occupancy, and logs congestion events to both SQLite and Neon PostgreSQL database tables.
```bash
cd cv_tracker
python main.py
```
> [!NOTE]
> - If `traffic.mp4` is missing, the tracker automatically downloads a public CCTV sample.
> - If offline, it runs `generate_sample_video.py` to create a synthetic video and falls back to color contour-based tracking.
> - Runs **headless** automatically if no display server (X11) is detected, saving the output video to `outputs/processed_video.mp4`.

---

### Module 2: Causality Graph Visualizer
Streams correlation graphs mapping traffic spikes back to external factors.
```bash
cd graph_visualizer
streamlit run app.py --server.port 8501
```
*(Optional) To run the local graph backend server:*
```bash
cd graph_visualizer
python api.py
```
> [!TIP]
> The Streamlit application falls back automatically to reading the local JSON database file `data/urban_memory_logs.json` if the FastAPI `api.py` server is not running on port 8000.

---

### Module 3: Behavioral Digital Twin (React + FastAPI)
Calculates impact and displays simulated reductions based on physical traffic changes.

**Start the FastAPI Backend:**
```bash
cd digital_twin_ui/backend
uvicorn main:app --port 8000 --reload
```

**Start the React Frontend:**
```bash
cd digital_twin_ui/frontend
npm install
npm run dev
```

---

### Module 4: Traffic Strategist AI (Chatbot)
Synthesizes reports, handles CCTV uploads, and creates markdown recommendations.
```bash
cd strategist_ai
streamlit run app.py --server.port 8502
```
> [!IMPORTANT]
> The Strategist AI requires a valid `GROQ_API_KEY` defined in the `.env` file to successfully access Groq's high-speed inference endpoints.
