from sentence_transformers import SentenceTransformer

# Load the model once at module level so it isn't reloaded per request
clip_model = SentenceTransformer('clip-ViT-B-32')
