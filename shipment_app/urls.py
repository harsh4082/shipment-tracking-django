from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # -------------------
    # Admin URLs
    # -------------------
    path('myadmin/login/', views.admin_login, name='admin_login'),
    path('myadmin/logout/', views.admin_logout, name='admin_logout'),
    path('myadmin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('myadmin/containers/', views.admin_containers, name='admin_containers'),
    path('myadmin/containers/delete/<str:container_id>/', views.delete_container, name='delete_container'),
    path('myadmin/customers/', views.admin_customers, name='admin_customers'),
    path('myadmin/order/add/', views.add_order, name='add_order'),
    # urls.py
    path('myadmin/order/upload-excel/', views.upload_orders_excel, name='upload_orders_excel'),
    path('myadmin/order/confirm-excel/', views.confirm_orders_excel, name='confirm_orders_excel'),
    # ------------------- Admin View Orders -------------------
    path('myadmin/orders/view/', views.view_orders_by_container, name='view_orders_by_container'),
    path('myadmin/orders/view-by-customer/', views.view_orders_by_customer, name='view_orders_by_customer'),
    path('ajax/get-customers/', views.get_customers_by_container, name='get_customers_by_container'),
    path("myadmin/field-visibility/", views.manage_field_visibility, name="manage_field_visibility"),



    # -------------------
    # User URLs
    # -------------------
    path('user/login/', views.user_login, name='user_login'),
    path('user/logout/', views.user_logout, name='user_logout'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/update-password/', views.user_update_password, name='user_update_password'),

    # -------------------
    # User Order Views
    # -------------------
    path('user/containers/', views.user_containers, name='user_containers'),
    path('user/container/<str:enc_container_id>/', views.user_container_orders, name='user_container_orders'),
    path('user/container/<str:enc_container_id>/export/pdf/', views.export_orders_pdf, name='export_orders_pdf'),
    path('user/container/<str:enc_container_id>/export/excel/', views.export_orders_excel, name='export_orders_excel'),

    # -------------------
    # User Profile Update
    # -------------------
    path('user/update-profile/', views.user_update_profile, name='user_update_profile'),
        path('forgot-password/', views.user_forgot_password, name='user_forgot_password'),
    path('reset-password/<uidb64>/', views.user_reset_password, name='user_reset_password'),
]

# -------------------
# Custom error handlers
# -------------------
handler404 = 'shipment_app.views.custom_404_view'
handler500 = 'shipment_app.views.custom_500_view'  # optional
