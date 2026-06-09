from django.urls import path
from . import views

urlpatterns = [
    path('<str:group_code>/', views.chat_room, name='chat_room'),
]
