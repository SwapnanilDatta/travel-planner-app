import os
import io
import time
import requests
import numpy as np

# Load the API token and URL
HF_API_TOKEN = os.getenv('HF_API_TOKEN')
API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/clip-ViT-B-32"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

class HFClipModel:
    def encode(self, input_data):
        max_retries = 3
        for attempt in range(max_retries):
            if isinstance(input_data, str):
                payload = {"inputs": input_data}
                response = requests.post(API_URL, headers=headers, json=payload)
            else:
                # Assume it's a PIL Image
                buffered = io.BytesIO()
                input_data.save(buffered, format="JPEG")
                img_bytes = buffered.getvalue()
                response = requests.post(API_URL, headers=headers, data=img_bytes)
            
            if response.status_code == 200:
                return np.array(response.json()).flatten()
            elif response.status_code == 503:
                # Model is loading
                time.sleep(15)
            else:
                print(f"HF API Error: {response.text}")
                return np.zeros(512)
        return np.zeros(512)

clip_model = HFClipModel()

# Define and compute category embeddings on startup
CATEGORIES = {
    "Beach": "sandy beaches, ocean, sea, shoreline, sunset, water sports",
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

CATEGORY_EMBEDDINGS = {}
for category_name, description in CATEGORIES.items():
    CATEGORY_EMBEDDINGS[category_name] = clip_model.encode(description)
