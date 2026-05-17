from django.urls import path, include
from .views import dashboard, analytics, admin_dashboard, login_success, register

urlpatterns = [
    path('register/', register, name='register'),
    path('', login_success, name='dashboard_root'), # Map root to smart redirect
    path('login-success/', login_success, name='login_success'),
    path('dashboard/', dashboard, name='dashboard'),
    path('analytics/', analytics, name='analytics'),
    path('admin-portal/', admin_dashboard, name='admin_dashboard'),
    path('accounts/', include('django.contrib.auth.urls')), # login, logout, password_change, etc.
]