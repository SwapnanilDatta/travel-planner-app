import os
import io
import time
import requests
import numpy as np

import base64

# Load the API URL for microservice2
MICROSERVICE2_URL = os.getenv('MICROSERVICE2_URL', 'http://127.0.0.1:8001/embed')

class MicroserviceClipModel:
    def encode(self, input_data):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if isinstance(input_data, str):
                    payload = {"text": input_data}
                    response = requests.post(MICROSERVICE2_URL, json=payload, timeout=10)
                else:
                    # Assume it's a PIL Image
                    buffered = io.BytesIO()
                    input_data.save(buffered, format="JPEG")
                    img_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    payload = {"image_b64": img_b64}
                    response = requests.post(MICROSERVICE2_URL, json=payload, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'embedding' in data:
                        return np.array(data['embedding']).flatten()
                    
                print(f"Microservice API Error: {response.status_code} - {response.text}")
                return np.zeros(512)
            except requests.exceptions.RequestException as e:
                print(f"Microservice Network Error: {e}")
                time.sleep(2)
        return np.zeros(512)

clip_model = MicroserviceClipModel()

# Define and compute category embeddings on startup
CATEGORIES = {
    "Beach": "a photo of a beach with sand, ocean waves and coastline",
    "Food": "restaurants, dishes, street food, local cuisine",
    "Museum": "historical artifacts, galleries, exhibitions, architecture",
    "Hotel": "hotel rooms, lobby, resort, accommodation",
    "Nature": "forests, mountains, lakes, trails, wilderness",
    "Shopping": "malls, markets, souvenirs, stores",
    "Nightlife": "bars, clubs, neon lights, parties",
    "Temple": "shrines, places of worship, religious architecture",
    "Adventure": "hiking, ziplining, extreme sports, outdoor activities",
    "Transportation": "trains, buses, airplanes, roads, vehicles",
}

_CATEGORY_EMBEDDINGS = None

def get_category_embeddings():
    global _CATEGORY_EMBEDDINGS
    if _CATEGORY_EMBEDDINGS is None:
        print("Lazy-loading category embeddings from HF API...")
        _CATEGORY_EMBEDDINGS = {}
        for category_name, description in CATEGORIES.items():
            _CATEGORY_EMBEDDINGS[category_name] = clip_model.encode(description)
    return _CATEGORY_EMBEDDINGS
