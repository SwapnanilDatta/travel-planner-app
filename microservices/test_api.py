import requests
import json

data = data = {
  "destinations": ["mumbai"],
  "total_days": 4,
  "group_size": 4,
  "pace": "moderate",
  "budget_per_day_INR": "3000",
  "budget_type": "mid-range",
  "use_llm": True,
  "hotel_name": "Hotel Sahil, Marine Drive",
  "hotel_lat": 18.9430,
  "hotel_lng": 72.8238,
  "members": [
    {
      "name": "Arun",
      "age_group": "30-40",
      "mobility_constraints": False,
      "preferences": {
        "nature",
        "photography",
        "history"
      }
    }
  ]
}

try:
    print("Testing the API with the proper payload...")
    response = requests.post("https://microservices-f9319416.fastapicloud.dev/plan-trip", json=data)
    print("Status:", response.status_code)
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
