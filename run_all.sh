#!/bin/bash

# RoadMind-X Unified Startup Script for macOS
# This script automatically checks/installs dependencies and opens each service in its own terminal tab/window.

# Get the absolute path of the project root
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo "    RoadMind-X Unified macOS Service Launcher"
echo "=========================================================="

# 1. Check/Install Python virtual environment & dependencies
if [ ! -d "$ROOT_DIR/venv" ]; then
    echo "📦 Creating python virtual environment..."
    python3 -m venv "$ROOT_DIR/venv"
fi

echo "🔌 Activating virtual environment & updating dependencies..."
source "$ROOT_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$ROOT_DIR/requirements.txt"

# 2. Check/Install Node.js packages for the Digital Twin frontend
if [ ! -d "$ROOT_DIR/digital_twin_ui/frontend/node_modules" ]; then
    echo "📦 Node modules not found. Running npm install for the Digital Twin UI..."
    (cd "$ROOT_DIR/digital_twin_ui/frontend" && npm install)
else
    echo "✅ Frontend Node modules already installed."
fi

# 3. Read environment variables and check for keys
if [ -f "$ROOT_DIR/.env" ]; then
    source "$ROOT_DIR/.env"
fi

if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "your_groq_api_key_here" ]; then
    echo "⚠️  WARNING: GROQ_API_KEY is not set in .env."
    echo "   The Traffic Strategist AI (chatbot) requires this key to function."
    echo "   Please update the .env file in the root directory with your key."
    echo ""
fi

# Define commands with their absolute virtualenv paths
PYTHON_CMD="$ROOT_DIR/venv/bin/python"
STREAMLIT_CMD="$ROOT_DIR/venv/bin/streamlit"
UVICORN_CMD="$ROOT_DIR/venv/bin/uvicorn"

echo ""
echo "🚀 Spawning services in separate macOS Terminal windows..."
echo ""

# Module 1: CV Perception Tracker
echo "🎥 Launching CV Perception Tracker..."
osascript -e "tell application \"Terminal\" to do script \"echo -n -e '\\033]0;RoadMind-X | CV Tracker\\007'; cd '$ROOT_DIR/cv_tracker' && '$PYTHON_CMD' main.py\""

# Module 2: Causality Graph Streamlit UI
echo "🕸️ Launching Causality Graph UI..."
osascript -e "tell application \"Terminal\" to do script \"echo -n -e '\\033]0;RoadMind-X | Causality Graph UI\\007'; cd '$ROOT_DIR/graph_visualizer' && '$STREAMLIT_CMD' run app.py --server.port 8501\""

# Module 3: Digital Twin FastAPI Backend
echo "⚙️ Launching Digital Twin Backend API..."
osascript -e "tell application \"Terminal\" to do script \"echo -n -e '\\033]0;RoadMind-X | Digital Twin API\\007'; cd '$ROOT_DIR/digital_twin_ui/backend' && '$UVICORN_CMD' main:app --port 8000 --reload\""

# Module 4: Digital Twin React Frontend
echo "💻 Launching Digital Twin React Frontend..."
osascript -e "tell application \"Terminal\" to do script \"echo -n -e '\\033]0;RoadMind-X | Digital Twin UI\\007'; cd '$ROOT_DIR/digital_twin_ui/frontend' && npm run dev\""

# Module 5: Traffic Strategist AI Streamlit UI
echo "🧠 Launching Traffic Strategist AI..."
osascript -e "tell application \"Terminal\" to do script \"echo -n -e '\\033]0;RoadMind-X | Strategist AI\\007'; cd '$ROOT_DIR/strategist_ai' && '$STREAMLIT_CMD' run app.py --server.port 8502\""

echo ""
echo "=========================================================="
echo "🎉 SUCCESS: All 5 processes spawned in separate Terminal windows!"
echo "----------------------------------------------------------"
echo " 🌐 Port Map:"
echo "   - Digital Twin Frontend: http://localhost:5173"
echo "   - Digital Twin API:      http://localhost:8000"
echo "   - Causality Graph UI:    http://localhost:8501"
echo "   - Traffic Strategist AI: http://localhost:8502"
echo "   - CV Tracker:            Window overlay (Saves to outputs/)"
echo "=========================================================="
