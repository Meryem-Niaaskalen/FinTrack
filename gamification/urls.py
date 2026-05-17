from django.urls import path
from . import views

urlpatterns = [
    path('badges/', views.badge_list, name='badge_list'),
]
