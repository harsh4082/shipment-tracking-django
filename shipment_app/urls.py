from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Admin URLs
    path('myadmin/login/', views.admin_login, name='admin_login'),
    path('myadmin/logout/', views.admin_logout, name='admin_logout'),
    path('myadmin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('myadmin/containers/', views.admin_containers, name='admin_containers'),
    path('myadmin/containers/delete/<str:container_id>/', views.delete_container, name='delete_container'),
    path('myadmin/customers/', views.admin_customers, name='admin_customers'),
    path('myadmin/order/add/', views.add_order, name='add_order'),


    # User URLs
    path('user/login/', views.user_login, name='user_login'),
    path('user/logout/', views.user_logout, name='user_logout'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/update-password/', views.user_update_password, name='user_update_password'),
]
