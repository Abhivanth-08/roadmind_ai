from fastapi import FastAPI, HTTPException
import json
import os
import uvicorn

app = FastAPI(title="RoadMind-X Cognitive Intelligence API")

def load_json_data():
    file_path = os.path.join("..", "data", "urban_memory_logs.json")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Data file not found")
    with open(file_path, "r") as f:
        return json.load(f)

@app.get("/api/data")
async def get_all_data():
    """Returns the full Urban Memory Logs dataset."""
    return load_json_data()

@app.get("/api/v1/causality/{location}")
async def get_location_causality(location: str):
    """Returns focused causation data for a specific location node."""
    data = load_json_data()
    filtered_data = [item for item in data if item.get("location") == location]
    
    if not filtered_data:
        raise HTTPException(status_code=404, detail="Location not found in memory logs")
        
    return {
        "location": location,
        "total_incidents": len(filtered_data),
        "causality_traces": filtered_data
    }

if __name__ == "__main__":
    print("Starting RoadMind-X FastAPI Server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
