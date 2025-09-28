from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from functools import wraps
from .models import AdminTable, Customer, Container
from .models import Customer, Container, Order

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
