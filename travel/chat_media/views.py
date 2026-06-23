import io
import numpy as np
from PIL import Image
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import ChatImage
from groups.models import ChatGroup
from .ml import clip_model, get_category_embeddings

@login_required
def upload_chat_image(request, group_code):
    if request.method != 'POST' or 'image' not in request.FILES:
        return JsonResponse({'error': 'No image provided'}, status=400)

    image_file = request.FILES['image']

    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if image_file.content_type not in allowed_types:
        return JsonResponse({'error': 'Unsupported file type'}, status=400)
    max_size_mb = 8
    if image_file.size > max_size_mb * 1024 * 1024:
        return JsonResponse({'error': 'File too large'}, status=400)

    try:
        group = ChatGroup.objects.get(code=group_code)
    except ChatGroup.DoesNotExist:
        return JsonResponse({'error': 'Group not found'}, status=404)

    chat_image = ChatImage.objects.create(
        group=group,
        uploader=request.user,
        image=image_file,
    )

    pil_img = Image.open(chat_image.image.path).convert('RGB')

    embedding = clip_model.encode(pil_img)
    chat_image.embedding = embedding.tolist()

    # 1. Duplicate detection
    existing_images = ChatImage.objects.filter(group=group).exclude(id=chat_image.id).exclude(embedding=None)
    is_duplicate = False
    for img in existing_images:
        img_emb = np.array(img.embedding)
        sim = float(np.dot(embedding, img_emb) / (np.linalg.norm(embedding) * np.linalg.norm(img_emb)))
        if sim > 0.95:
            is_duplicate = True
            break
    chat_image.is_duplicate = is_duplicate

    # 2. Categorization
    best_category = None
    best_confidence = -1.0
    for cat_name, cat_emb in get_category_embeddings().items():
        sim = float(np.dot(embedding, cat_emb) / (np.linalg.norm(embedding) * np.linalg.norm(cat_emb)))
        if sim > best_confidence:
            best_confidence = sim
            best_category = cat_name
            
    chat_image.category = best_category
    chat_image.confidence = best_confidence

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

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{group_code}',
        {
            'type': 'chat_image_message',
            'image_url': chat_image.image.url,
            'thumbnail_url': chat_image.thumbnail.url,
            'sender': request.user.username,
            'message_id': chat_image.id,
            'uploaded_at': chat_image.uploaded_at.isoformat(),
            'category': chat_image.category,
            'is_duplicate': chat_image.is_duplicate
        }
    )

    return JsonResponse({
        'status': 'ok',
        'id': chat_image.id,
        'image_url': chat_image.image.url,
        'thumbnail_url': chat_image.thumbnail.url,
        'category': chat_image.category,
        'is_duplicate': chat_image.is_duplicate
    })

@login_required
def search_chat_images(request, group_code):
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    
    images = ChatImage.objects.filter(group__code=group_code).exclude(embedding=None).order_by('-uploaded_at')

    if category:
        images = images.filter(category=category)

    if not query:
        # Return all images (Gallery mode)
        return JsonResponse({
            'results': [
                {
                    'id': img.id,
                    'image_url': img.image.url,
                    'thumbnail_url': img.thumbnail.url,
                    'uploader': img.uploader.username,
                    'uploaded_at': img.uploaded_at.isoformat(),
                    'score': 1.0,
                    'category': img.category,
                    'is_duplicate': img.is_duplicate
                }
                for img in images
            ]
        })

    query_embedding = clip_model.encode(query)

    results = []
    for img in images:
        img_embedding = np.array(img.embedding)
        score = float(np.dot(query_embedding, img_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(img_embedding)
        ))
        results.append((img, score))

    results.sort(key=lambda x: x[1], reverse=True)

    SIMILARITY_THRESHOLD = 0.2
    top_results = [r for r in results if r[1] > SIMILARITY_THRESHOLD][:20]

    return JsonResponse({
        'results': [
            {
                'id': img.id,
                'image_url': img.image.url,
                'thumbnail_url': img.thumbnail.url,
                'score': round(score, 4),
                'uploader': img.uploader.username,
                'uploaded_at': img.uploaded_at.isoformat(),
                'category': img.category,
                'is_duplicate': img.is_duplicate
            }
            for img, score in top_results
        ]
    })
