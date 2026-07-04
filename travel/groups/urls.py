from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('create/', views.create_group, name='create_group'),
    path('join/', views.join_group, name='join_group'),
    path('group/<str:code>/', views.group_detail, name='group_detail'),
    path('group/<str:code>/lock/', views.lock_group, name='lock_group'),
    path('group/<str:code>/trip/create/', views.create_trip, name='create_trip'),
    path('group/<str:code>/preference/', views.submit_preference, name='submit_preference'),
    path('group/<str:code>/plan/', views.plan_itinerary, name='plan_itinerary'),
    path('group/<str:code>/plan/check-ready/', views.check_plan_ready, name='check_plan_ready'),
    path('api/webhook/plan/<str:code>/', views.webhook_plan_result, name='webhook_plan_result'),
    path('group/<str:code>/itinerary/', views.view_itinerary, name='view_itinerary'),
    path('group/<str:code>/itinerary/save/', views.save_itinerary, name='save_itinerary'),
    path('group/<str:code>/itinerary/day/<int:day_number>/update/', views.update_daily_plan, name='update_daily_plan'),
    path('group/<str:code>/itinerary/day/<int:day_number>/regenerate/', views.regenerate_daily_plan, name='regenerate_daily_plan'),
    path('group/<str:code>/itinerary/day/<int:day_number>/regenerate/check-ready/', views.check_regenerate_ready, name='check_regenerate_ready'),
    path('api/webhook/regenerate/<str:code>/<int:day_number>/', views.webhook_regenerate_result, name='webhook_regenerate_result'),
    path('budget/', views.budget_predictor, name='budget_predictor'),
    path('api/budget/predict/', views.api_budget_predict, name='api_budget_predict'),
]
