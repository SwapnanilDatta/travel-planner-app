from django.db import models
from django.contrib.auth.models import User
from groups.models import ChatGroup

class ChatImage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='images')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='chat_images/')
    thumbnail = models.ImageField(upload_to='chat_thumbnails/', blank=True, null=True)
    embedding = models.JSONField(blank=True, null=True)  # list of 512 floats from CLIP
    caption = models.CharField(max_length=255, blank=True)  # optional
    category = models.CharField(max_length=50, blank=True, null=True)
    confidence = models.FloatField(blank=True, null=True)
    is_duplicate = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image by {self.uploader.username} in {self.group.name}"
