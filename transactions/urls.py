from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('add/', views.transaction_create, name='transaction_create'),
    path('edit/<int:pk>/', views.transaction_edit, name='transaction_edit'),
    path('delete/<int:pk>/', views.transaction_delete, name='transaction_delete'),
    path('transfer/add/', views.transfer_create, name='transfer_create'),
    path('transfer/delete/<int:pk>/', views.transfer_delete, name='transfer_delete'),
    path('recurring/add/', views.recurring_create, name='recurring_create'),
    path('recurring/delete/<int:pk>/', views.recurring_delete, name='recurring_delete'),
    path('export/csv/', views.export_transactions_csv, name='export_transactions_csv'),
]
