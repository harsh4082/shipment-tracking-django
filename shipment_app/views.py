from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from functools import wraps
from .models import AdminTable, Customer, Container
from .models import Customer, Container, Order
import io
import xlsxwriter
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .utils import encrypt_text, decrypt_text
from django.shortcuts import redirect
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.conf import settings
import os
import json
import uuid
# from io import BytesIO
# from django.shortcuts import render, redirect, get_object_or_404
# from django.conf import settings
# from django.core.files.storage import default_storage
# from django.contrib import messages
# from django.views.decorators.http import require_http_methods
# from django.utils.html import escape

# import openpyxl
# from openpyxl.utils import get_column_letter
# from openpyxl.drawing.spreadsheet_drawing import SpreadsheetDrawing
# from openpyxl.worksheet.worksheet import Worksheet
# from openpyxl.drawing.image import Image as OpenpyxlImage
# from PIL import Image as PILImage

# from .models import Customer, Container, Order
# from .decorators import admin_required  # you used @admin_required earlier

# ----------------------------
# Decorators
# ----------------------------
def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_id'):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def customer_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('customer_id'):
            return redirect('user_login')
        return view_func(request, *args, **kwargs)
    return wrapper

# ----------------------------
# Home
# ----------------------------
def home(request):
    return render(request, "home.html")

# ----------------------------
# Admin Views
# ----------------------------
def admin_login(request):
    if request.method == "POST":
        user_id = request.POST.get("username")
        password = request.POST.get("password")

        try:
            admin = AdminTable.objects.get(user_id=user_id)
            if admin.check_password(password):
                request.session['admin_id'] = admin.admin_id
                request.session['admin_user_id'] = admin.user_id
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Invalid password")
        except AdminTable.DoesNotExist:
            messages.error(request, "Admin not found")

    return render(request, "admin_login.html")

@admin_required
def admin_dashboard(request):
    admin_user_id = request.session.get('admin_user_id')
    return render(request, "admin_dashboard.html", {"admin_user_id": admin_user_id})

@admin_required
def admin_containers(request):
    containers = Container.objects.all()

    if request.method == "POST":
        container_no = request.POST.get("container_no")
        container_name = request.POST.get("container_name")
        if container_no and container_name:
            container = Container(container_no=container_no, container_name=container_name)
            container.save()
            messages.success(request, f"Container {container.container_id} added successfully")
            return redirect('admin_containers')

    return render(request, "admin_containers.html", {"containers": containers})

@admin_required
def delete_container(request, container_id):
    container = get_object_or_404(Container, container_id=container_id)
    container.delete()
    messages.success(request, f"Container {container_id} deleted successfully")
    return redirect('admin_containers')

@admin_required
def admin_customers(request):
    customers = Customer.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer_id")
        name = request.POST.get("name")
        user_id = request.POST.get("user_id")
        password = request.POST.get("password")
        email = request.POST.get("email")
        whatsapp = request.POST.get("whatsapp_number")

        if Customer.objects.filter(user_id=user_id).exists():
            messages.error(request, "User ID already exists")
        else:
            customer = Customer(
                customer_id=customer_id,
                name=name,
                user_id=user_id,
                password=password,  # will be hashed in save()
                email=email,
                whatsapp_number=whatsapp
            )
            customer.save()
            messages.success(request, f"Customer {customer_id} added successfully")
            return redirect('admin_customers')

    return render(request, "admin_customers.html", {"customers": customers})

@admin_required
def admin_logout(request):
    request.session.flush()
    messages.success(request, "Admin logged out successfully")
    return redirect('admin_login')


@admin_required
def add_order(request):
    customers = Customer.objects.all()
    containers = Container.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer")
        container_id = request.POST.get("container")
        shipping_mark = request.POST.get("shipping_mark")
        description = request.POST.get("description")
        item_no_spec = request.POST.get("item_no_spec")
        material = request.POST.get("material")
        pictures = request.FILES.get("pictures")

        # Numeric fields with proper casting
        ctns = int(request.POST.get("ctns", 0))
        qty_per_ctn = int(request.POST.get("qty_per_ctn", 0))
        total_qty = ctns * qty_per_ctn

        unit = request.POST.get("unit")
        cbm_per_ctn = float(request.POST.get("cbm_per_ctn", 0))
        cbm = float(request.POST.get("cbm", 0))
        total_cbm = float(request.POST.get("total_cbm", 0))
        wt_per_ctn = float(request.POST.get("wt_per_ctn", 0))
        total_wt = float(request.POST.get("total_wt", 0))
        supplier = request.POST.get("supplier")

        customer = get_object_or_404(Customer, customer_id=customer_id)
        container = get_object_or_404(Container, container_id=container_id)

        Order.objects.create(
            customer=customer,
            container=container,
            shipping_mark=shipping_mark,
            description=description,
            item_no_spec=item_no_spec,
            material=material,
            pictures=pictures,
            ctns=ctns,
            qty_per_ctn=qty_per_ctn,
            total_qty=total_qty,
            unit=unit,
            cbm_per_ctn=cbm_per_ctn,
            cbm=cbm,
            total_cbm=total_cbm,
            wt_per_ctn=wt_per_ctn,
            total_wt=total_wt,
            supplier=supplier
        )

        messages.success(request, f"Order added successfully for {customer.customer_id}")
        return redirect("add_order")

    return render(request, "add_order.html", {"customers": customers, "containers": containers})

# ----------------------------
# Customer Views
# ----------------------------
def user_login(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        password = request.POST.get("password")

        try:
            customer = Customer.objects.get(user_id=user_id)
            if customer.check_password(password):
                # Set session
                request.session['customer_id'] = customer.customer_id
                request.session['customer_name'] = customer.name

                # First time login check
                if customer.is_first_login:
                    return redirect('user_update_password')
                return redirect('user_dashboard')
            else:
                messages.error(request, "Invalid password")
        except Customer.DoesNotExist:
            messages.error(request, "User not found")

    return render(request, "user_login.html")


@customer_required
def user_dashboard(request):
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, customer_id=customer_id)
    return render(request, "user_dashboard.html", {"customer": customer})


@customer_required
def user_update_password(request):
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, customer_id=customer_id)

    if request.method == "POST":
        new_password = request.POST.get("password")
        if not new_password:
            messages.error(request, "Password cannot be empty")
        else:
            customer.set_password(new_password)  # Hashes the password
            customer.is_first_login = False
            customer.save()
            messages.success(request, "Password updated successfully")
            return redirect('user_dashboard')

    return render(request, "user_update_password.html", {"customer": customer})


@customer_required
def user_logout(request):
    request.session.flush()
    messages.success(request, "User logged out successfully")
    return redirect('user_login')

# ----------------------------
# User Containers (list only user's containers)
# ----------------------------
@customer_required
def user_containers(request):
    customer_id = request.session.get('customer_id')
    # Get unique containers for this customer
    containers = Container.objects.filter(order__customer_id=customer_id).distinct()
    return render(request, "user_containers.html", {"containers": containers})


# ----------------------------
# Orders inside selected container
# ----------------------------
@customer_required
def user_container_orders(request, container_id):
    customer_id = request.session.get('customer_id')
    container = get_object_or_404(Container, container_id=container_id)
    orders = Order.objects.filter(container=container, customer_id=customer_id)
    return render(request, "user_container_orders.html", {
        "container": container,
        "orders": orders
    })


# ----------------------------
# Export Orders to PDF
# ----------------------------
@customer_required
def export_orders_pdf(request, container_id):
    customer_id = request.session.get('customer_id')
    container = get_object_or_404(Container, container_id=container_id)
    orders = Order.objects.filter(container=container, customer_id=customer_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="orders_{container_id}.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)
    p.drawString(100, 800, f"Orders for Container {container_id}")

    y = 770
    for order in orders:
        p.drawString(100, y, f"Shipping Mark: {order.shipping_mark} | "
                             f"Item: {order.item_no_spec} | Qty: {order.total_qty}")
        y -= 20
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 770

    p.showPage()
    p.save()
    return response


# ----------------------------
# Export Orders to Excel
# ----------------------------
@customer_required
def export_orders_excel(request, container_id):
    customer_id = request.session.get('customer_id')
    container = get_object_or_404(Container, container_id=container_id)
    orders = Order.objects.filter(container=container, customer_id=customer_id)

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Headers
    headers = ["Shipping Mark", "Description", "Item No", "Material",
               "CTNs", "Qty/CTN", "Total Qty", "Unit", "Supplier"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    # Rows
    for row, order in enumerate(orders, start=1):
        worksheet.write(row, 0, order.shipping_mark)
        worksheet.write(row, 1, order.description)
        worksheet.write(row, 2, order.item_no_spec)
        worksheet.write(row, 3, order.material or "")
        worksheet.write(row, 4, order.ctns)
        worksheet.write(row, 5, order.qty_per_ctn)
        worksheet.write(row, 6, order.total_qty)
        worksheet.write(row, 7, order.unit)
        worksheet.write(row, 8, order.supplier)

    workbook.close()
    output.seek(0)

    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = f'attachment; filename="orders_{container_id}.xlsx"'
    return response


# ----------------------------
# User Containers (list only user's containers)
# ----------------------------
@customer_required
def user_containers(request):
    customer_id = request.session.get('customer_id')
    containers = Container.objects.filter(order__customer_id=customer_id).distinct()

    # Add encrypted IDs for URLs
    container_links = [
        {
            'container': c,
            'enc_id': encrypt_text(c.container_id)
        }
        for c in containers
    ]

    return render(request, "user_containers.html", {"container_links": container_links})


# ----------------------------
# Orders inside selected container
# ----------------------------
@customer_required
def user_container_orders(request, enc_container_id):
    customer_id = request.session.get('customer_id')
    container_id = decrypt_text(enc_container_id)
    container = get_object_or_404(Container, container_id=container_id)
    orders = Order.objects.filter(container=container, customer_id=customer_id)

    return render(request, "user_container_orders.html", {
        "container": container,
        "orders": orders,
        "enc_container_id": enc_container_id  # for PDF/Excel links
    })


# ----------------------------
# Export Orders to PDF
# ----------------------------
@customer_required
def export_orders_pdf(request, enc_container_id):
    customer_id = request.session.get('customer_id')
    container_id = decrypt_text(enc_container_id)
    container = get_object_or_404(Container, container_id=container_id)
    orders = Order.objects.filter(container=container, customer_id=customer_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="orders_{container_id}.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica", 12)
    p.drawString(100, 800, f"Orders for Container {container_id}")

    y = 770
    for order in orders:
        p.drawString(100, y, f"Shipping Mark: {order.shipping_mark} | "
                             f"Item: {order.item_no_spec} | Qty: {order.total_qty}")
        y -= 20
        if y < 50:
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 770

    p.showPage()
    p.save()
    return response


# ----------------------------
# Export Orders to Excel
# ----------------------------
@customer_required
def export_orders_excel(request, enc_container_id):
    customer_id = request.session.get('customer_id')
    container_id = decrypt_text(enc_container_id)
    container = get_object_or_404(Container, container_id=container_id)
    orders = Order.objects.filter(container=container, customer_id=customer_id)

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Headers
    headers = ["Shipping Mark", "Description", "Item No", "Material",
               "CTNs", "Qty/CTN", "Total Qty", "Unit", "Supplier"]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    # Rows
    for row, order in enumerate(orders, start=1):
        worksheet.write(row, 0, order.shipping_mark)
        worksheet.write(row, 1, order.description)
        worksheet.write(row, 2, order.item_no_spec)
        worksheet.write(row, 3, order.material or "")
        worksheet.write(row, 4, order.ctns)
        worksheet.write(row, 5, order.qty_per_ctn)
        worksheet.write(row, 6, order.total_qty)
        worksheet.write(row, 7, order.unit)
        worksheet.write(row, 8, order.supplier)

    workbook.close()
    output.seek(0)

    response = HttpResponse(output.read(),
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = f'attachment; filename="orders_{container_id}.xlsx"'
    return response

# ----------------------------
# Update Customer Profile
# ----------------------------
@customer_required
def user_update_profile(request):
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(Customer, customer_id=customer_id)

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        whatsapp = request.POST.get("whatsapp_number")

        # Simple validation
        if not name or not email:
            messages.error(request, "Name and Email cannot be empty")
        else:
            customer.name = name
            customer.email = email
            customer.whatsapp_number = whatsapp
            customer.save()
            request.session['customer_name'] = customer.name  # Update session
            messages.success(request, "Profile updated successfully")
            return redirect('user_dashboard')

    return render(request, "user_update_profile.html", {"customer": customer})




def custom_404_view(request, exception=None):
    # If not logged in → redirect to login
    if not request.session.get("admin_id") and not request.session.get("customer_id"):
        return redirect("user_login")

    # If logged in → redirect to correct dashboard
    if request.session.get("admin_id"):
        return redirect("admin_dashboard")
    elif request.session.get("customer_id"):
        return redirect("user_dashboard")

    # fallback → show friendly 404 page
    return render(request, "404.html", status=404)


def custom_500_view(request):
    return render(request, "500.html", status=500)
