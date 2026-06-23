import json
import random
import datetime

locations = ["MG Road", "5th Avenue", "City Hospital Junction", "Tech Park Blvd", "Central Station Route"]
violation_types = ["Illegal Parking", "Wrong-Way Driving", "Signal Jump", "Speeding", "Lane Violation"]
root_causes = ["Hospital Shift Change", "Local Festival", "Heavy Rain", "VIP Convoy", "Construction Work", "None"]
interventions = ["Add 20 Parking Spaces", "Deploy Dynamic Signage", "Increase Fine Rate", "Reroute Traffic", "Traffic Police Deployment"]

events = []
base_time = datetime.datetime.now() - datetime.timedelta(days=30)

for i in range(1200): # Generating 1200 entries
    event_time = base_time + datetime.timedelta(minutes=random.randint(1, 40000))
    loc = random.choice(locations)
    v_type = random.choice(violation_types)
    
    # Introduce logical causality to make data realistic
    cause = "None"
    if v_type == "Illegal Parking" and loc in ["City Hospital Junction", "MG Road"]:
        cause = random.choice(["Hospital Shift Change", "Local Festival"])
    elif v_type == "Wrong-Way Driving" and loc == "Tech Park Blvd":
        cause = "Construction Work"
    elif v_type == "Signal Jump":
        cause = random.choice(["VIP Convoy", "Heavy Rain", "None"])
    else:
        cause = random.choice(root_causes)
        
    recommended_fix = random.choice(interventions)
    
    events.append({
        "violation_id": f"V-{10000 + i}",
        "timestamp": event_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "location": loc,
        "violation_type": v_type,
        "confidence_score": round(random.uniform(0.75, 0.99), 2),
        "urban_context": cause,
        "recommended_intervention": recommended_fix,
        "simulated_impact": f"-{random.randint(15, 45)}% violations",
        "severity_level": random.choice(["Low", "Medium", "High", "Critical"])
    })

# Sort by time
events.sort(key=lambda x: x["timestamp"])

with open(r"data\urban_memory_logs.json", "w") as f:
    json.dump(events, f, indent=4)

print("Generated 1200 records in data/urban_memory_logs.json")
