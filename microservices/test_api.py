from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_plan_itinerary():
    payload = {
        "destinations": ["Delhi", "Agra"],
        "total_days": 5,
        "group_size": 4,
        "pace": "Moderate",
        "budget_per_day_INR": "1500-3000",
        "members": [
            {
                "name": "Ankit",
                "age_group": "Adult",
                "mobility_constraints": False,
                "preferences": {
                    "Historical & Heritage": 5,
                    "Food & Local Culture": 4,
                    "Shopping": 2
                }
            },
            {
                "name": "Neha",
                "age_group": "Adult",
                "mobility_constraints": False,
                "preferences": {
                    "Historical & Heritage": 3,
                    "Nature & Outdoors": 5,
                    "Photography Spots": 5
                }
            }
        ],
        "use_llm": True
    }

    response = client.post("/api/v1/plan-itinerary", json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_plan_itinerary()
