from typing import List, Dict

# Original VFE forecast
BASE_FORECAST = [
    {"hour": 0, "violations": 120},
    {"hour": 12, "violations": 135},
    {"hour": 24, "violations": 148},
    {"hour": 36, "violations": 160},
    {"hour": 48, "violations": 172},
    {"hour": 60, "violations": 185},
    {"hour": 72, "violations": 195}
]


# Intervention effectiveness
INTERVENTION_FACTORS = {
    "Add 20 Parking Spaces": 0.58,
    "Deploy Traffic Police": 0.42,
    "Signal Retiming": 0.35,
    "Dynamic Signboards": 0.25
}


def get_risk(predicted_violations: int) -> str:
    """
    Determine risk level based on final violation count
    """
    if predicted_violations >= 150:
        return "HIGH"
    elif predicted_violations >= 100:
        return "MEDIUM"
    else:
        return "LOW"


def simulate_intervention(intervention: str) -> Dict:
    """
    Run Behavioral Digital Twin simulation
    """

    reduction_factor = INTERVENTION_FACTORS.get(intervention, 0)

    simulated_forecast = []

    for point in BASE_FORECAST:

        reduced_value = int(
            point["violations"] *
            (1 - reduction_factor)
        )

        simulated_forecast.append({
            "hour": point["hour"],
            "violations": reduced_value
        })

    predicted_violations = simulated_forecast[-1]["violations"]

    reduction_percentage = int(reduction_factor * 100)

    risk = get_risk(predicted_violations)

    response = {
        "intervention": intervention,

        "forecast": simulated_forecast,

        "current_violations": BASE_FORECAST[-1]["violations"],

        "predicted_violations": predicted_violations,

        "reduction_percentage": reduction_percentage,

        "risk": risk,

        "affected_roads": [
            "Main Street",
            "School Road",
            "Hospital Lane"
        ],

        "spread_risk": "HIGH"
    }

    return response