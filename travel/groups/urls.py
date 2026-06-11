from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_group, name='create_group'),
    path('join/', views.join_group, name='join_group'),
    path('group/<str:code>/', views.group_detail, name='group_detail'),
    path('group/<str:code>/lock/', views.lock_group, name='lock_group'),
    path('group/<str:code>/trip/create/', views.create_trip, name='create_trip'),
    path('group/<str:code>/preference/', views.submit_preference, name='submit_preference'),
    path('group/<str:code>/plan/', views.plan_itinerary, name='plan_itinerary'),
]
