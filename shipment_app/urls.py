from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),   # Add this

    
    # Admin URLs
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('containers/', views.admin_containers, name='admin_containers'),
    path('orders/', views.admin_orders, name='admin_orders'),
    path('users/', views.admin_users, name='admin_users'),

    # User URLs
    path('user/login/', views.user_login, name='user_login'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('user/status/', views.user_status, name='user_status'),
]
