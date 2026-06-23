from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import base64
import io
from PIL import Image

app = FastAPI(title="Travel App ML Service", description="Local CLIP Processing")

print("Loading clip-ViT-B-32 model...")
clip_model = SentenceTransformer('clip-ViT-B-32')
print("Model loaded successfully.")

class EmbedRequest(BaseModel):
    text: str | None = None
    image_b64: str | None = None

@app.post("/embed")
async def embed(request: EmbedRequest):
    if request.text:
        embedding = clip_model.encode(request.text)
        return {"embedding": embedding.tolist()}
    elif request.image_b64:
        try:
            image_data = base64.b64decode(request.image_b64)
            image = Image.open(io.BytesIO(image_data)).convert('RGB')
            embedding = clip_model.encode(image)
            return {"embedding": embedding.tolist()}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Must provide either 'text' or 'image_b64' in payload.")
