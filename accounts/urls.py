from django.urls import path
from . import views

urlpatterns = [
    path('', views.account_list, name='account_list'),
    path('add/', views.account_create, name='account_create'),
    path('edit/<int:pk>/', views.account_edit, name='account_edit'),
    path('delete/<int:pk>/', views.account_delete, name='account_delete'),
]
