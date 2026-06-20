import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel.settings')
django.setup()

from chat_media.models import ChatImage
from groups.models import ChatGroup
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import numpy as np

try:
    print("Getting user and group...")
    user = User.objects.first()
    group = ChatGroup.objects.first()
    if not user or not group:
        print("No user or group found. Cannot test.")
        exit()

    print(f"User: {user.username}, Group: {group.code}")

    print("Creating dummy image...")
    # Create a 10x10 red square jpeg
    from PIL import Image
    import io
    img = Image.new('RGB', (10, 10), color = 'red')
    img_io = io.BytesIO()
    img.save(img_io, format='JPEG')
    
    img_file = SimpleUploadedFile("test_red.jpg", img_io.getvalue(), content_type="image/jpeg")

    print("Creating ChatImage...")
    chat_image = ChatImage.objects.create(
        group=group,
        uploader=user,
        image=img_file,
    )
    
    print("Testing ML logic...")
    from chat_media.ml import clip_model, CATEGORY_EMBEDDINGS
    pil_img = Image.open(chat_image.image.path).convert('RGB')
    embedding = clip_model.encode(pil_img)
    chat_image.embedding = embedding.tolist()

    print("Duplicate detection...")
    existing_images = ChatImage.objects.filter(group=group).exclude(id=chat_image.id).exclude(embedding=None)
    is_duplicate = False
    for img_obj in existing_images:
        img_emb = np.array(img_obj.embedding)
        sim = float(np.dot(embedding, img_emb) / (np.linalg.norm(embedding) * np.linalg.norm(img_emb)))
        if sim > 0.95:
            is_duplicate = True
            break
    chat_image.is_duplicate = is_duplicate

    print("Categorization...")
    best_category = None
    best_confidence = -1.0
    for cat_name, cat_emb in CATEGORY_EMBEDDINGS.items():
        sim = float(np.dot(embedding, cat_emb) / (np.linalg.norm(embedding) * np.linalg.norm(cat_emb)))
        if sim > best_confidence:
            best_confidence = sim
            best_category = cat_name

    print(f"Assigned category: {best_category} with confidence {best_confidence}")
    chat_image.category = best_category
    chat_image.confidence = best_confidence

    print("Thumbnail generation...")
    from django.core.files.base import ContentFile
    thumb_img = pil_img.copy()
    thumb_img.thumbnail((200, 200))
    thumb_io = io.BytesIO()
    thumb_img.save(thumb_io, format='JPEG')
    chat_image.thumbnail.save(
        f'thumb_{chat_image.id}.jpg',
        ContentFile(thumb_io.getvalue()),
        save=False,
    )
    chat_image.save()
    
    print("Success! Image processed correctly.")
except Exception as e:
    import traceback
    traceback.print_exc()
