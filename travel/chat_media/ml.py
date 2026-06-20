from sentence_transformers import SentenceTransformer

# Load the model once at module level so it isn't reloaded per request
clip_model = SentenceTransformer('clip-ViT-B-32')

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
