from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from simulator import simulate_intervention

app = FastAPI(
    title="RoadMind-X Digital Twin API",
    version="1.0"
)

# Enable React frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# -----------------------------
# Request Model
# -----------------------------
class SimulationRequest(BaseModel):
    intervention: str


# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
def health_check():
    return {
        "message": "RoadMind-X Digital Twin API Running",
        "status": "OK"
    }


# -----------------------------
# Simulation Endpoint
# -----------------------------
@app.post("/simulate")
def simulate(request: SimulationRequest):

    result = simulate_intervention(
        request.intervention
    )

    return result