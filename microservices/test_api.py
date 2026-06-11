import requests
import json

data = {
  "destinations": [
    "Andaman",
    "Nicobar"
  ],
  "total_days": 4,
  "group_size": 4,
  "pace": "moderate",
  "budget_per_day_INR": "3000",
  "budget_type": "mid-range",
  "use_llm": True,
  "members": [
    {
      "name": "Arun",
      "age_group": "30-40",
      "mobility_constraints": False,
      "preferences": {
        "nature": 5,
        "photography": 4,
        "history": 2
      }
    }
  ]
}

try:
    print("Testing the API with the proper payload...")
    response = requests.post("http://127.0.0.1:8002/plan-trip", json=data)
    print("Status:", response.status_code)
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
