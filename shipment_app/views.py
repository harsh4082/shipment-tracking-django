from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to Shipment Tracking System")

# Admin Views
def admin_dashboard(request):
    return HttpResponse("Admin Dashboard Page")

def admin_containers(request):
    return HttpResponse("Admin Containers Page")

def admin_orders(request):
    return HttpResponse("Admin Orders Page")

def admin_users(request):
    return HttpResponse("Admin Users Page")

# User Views
def user_login(request):
    return HttpResponse("User Login Page")

def user_dashboard(request):
    return HttpResponse("User Dashboard Page")

def user_profile(request):
    return HttpResponse("User Profile Page")

def user_status(request):
    return HttpResponse("User Status Page")
