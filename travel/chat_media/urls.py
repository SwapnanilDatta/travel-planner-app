from django.urls import path
from . import views

urlpatterns = [
    path('groups/<str:group_code>/upload-image/', views.upload_chat_image, name='upload_chat_image'),
    path('groups/<str:group_code>/search-images/', views.search_chat_images, name='search_chat_images'),
]
