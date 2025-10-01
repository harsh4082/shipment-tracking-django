from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from functools import wraps
from .models import AdminTable, Customer, Container, Order
import io
import xlsxwriter
from django.http import HttpResponse, HttpResponseNotFound
from reportlab.pdfgen import canvas
from .utils import encrypt_text, decrypt_text
from django.conf import settings
import os
from django.core import signing
from django.core.files import File
from django.core.files.storage import FileSystemStorage
import openpyxl
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from django.core.files.storage import default_storage
from django.conf import settings
import io
import xlsxwriter
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Container, Order
# from .decorators import customer_required
import os

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

    # Get all related orders
    related_orders = Order.objects.filter(container=container)
    order_count = related_orders.count()

    # Delete related orders first
    related_orders.delete()

    # Now delete the container
    container.delete()

    messages.success(
        request,
        f"Container {container_id} and its {order_count} related order(s) deleted successfully."
    )
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


@admin_required
def upload_orders_excel(request):
    containers = Container.objects.all()
    preview_data = None
    selected_container = None

    if request.method == "POST" and request.FILES.get("excel_file"):
        selected_container = request.POST.get("container")
        excel_file = request.FILES["excel_file"]

        # Save uploaded Excel
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "excel_uploads"))
        filename = fs.save(excel_file.name, excel_file)
        file_path = fs.path(filename)

        wb = None
        try:
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active

            # Save merged ranges before unmerging
            original_merged_ranges = list(sheet.merged_cells.ranges)

            # Expand merged cells
            for merged_range in original_merged_ranges:
                min_col, min_row, max_col, max_row = merged_range.bounds
                first_val = sheet.cell(row=min_row, column=min_col).value
                sheet.unmerge_cells(range_string=str(merged_range))
                for r in range(min_row, max_row + 1):
                    for c in range(min_col, max_col + 1):
                        sheet.cell(row=r, column=c, value=first_val)

            # Extract images into media/order_pics
            images_dir = os.path.join(settings.MEDIA_ROOT, "order_pics")
            os.makedirs(images_dir, exist_ok=True)
            images_map = {}

            for img in sheet._images:
                try:
                    img_bytes = img._data()
                    img_filename = f"img_{len(images_map)+1}.png"
                    img_path = os.path.join(images_dir, img_filename)
                    with open(img_path, "wb") as f:
                        f.write(img_bytes)

                    # --- DEBUG PRINT ---
                    # print(f"[UPLOAD DEBUG] Saved image to: {img_path}")
                    # print(f"[UPLOAD DEBUG] Access URL: {settings.MEDIA_URL}order_pics/{img_filename}")

                    anchor_row = img.anchor._from.row + 1
                    anchor_col = img.anchor._from.col + 1
                    assigned = False

                    for merged_range in original_merged_ranges:
                        min_col, min_row, max_col, max_row = merged_range.bounds
                        if min_row <= anchor_row <= max_row and min_col <= anchor_col <= max_col:
                            for r in range(min_row, max_row + 1):
                                images_map.setdefault(r, set()).add(f"order_pics/{img_filename}")
                            assigned = True
                            break

                    if not assigned:
                        images_map.setdefault(anchor_row, set()).add(f"order_pics/{img_filename}")

                except Exception as e:
                    print("Image extraction failed:", e)

            # Normalize headers (row 3)
            headers = []
            for cell in sheet[3]:
                if cell.value:
                    header = str(cell.value).replace("\n", " ").replace('"', '').strip()
                    if re.search(r"shipping\s*mark", header, re.I):
                        header = "Shipping Mark"
                    elif re.search(r"item\s*no.*spec", header, re.I):
                        header = "Item No. /Specification"
                    elif re.search(r"total\s*qty", header, re.I):
                        header = "Total Qty"
                    headers.append(header)
                else:
                    headers.append(f"Column{len(headers)+1}")

            # Collect rows
            raw_rows = []
            for i, row in enumerate(sheet.iter_rows(min_row=4, values_only=True), start=4):
                if all(v is None for v in row):
                    continue
                row_dict = dict(zip(headers, row))
                if i in images_map:
                    row_dict["Pictures"] = list(images_map[i])
                raw_rows.append(row_dict)

            # Group images by (Customer, Shipping Mark)
            preview_data = []
            customer_shipping_images = {}

            for row_dict in raw_rows:
                customer = str(row_dict.get("CUSTOMER")).strip() if row_dict.get("CUSTOMER") else None
                shipping_mark = str(row_dict.get("Shipping Mark")).strip() if row_dict.get("Shipping Mark") else None

                if "Pictures" in row_dict and row_dict["Pictures"]:
                    key = (customer, shipping_mark)
                    customer_shipping_images.setdefault(key, set()).update(row_dict["Pictures"])

                preview_data.append(row_dict)

            # Attach grouped images
            for row_dict in preview_data:
                customer = str(row_dict.get("CUSTOMER")).strip() if row_dict.get("CUSTOMER") else None
                shipping_mark = str(row_dict.get("Shipping Mark")).strip() if row_dict.get("Shipping Mark") else None

                key = (customer, shipping_mark)
                if ("Pictures" not in row_dict or not row_dict.get("Pictures")) and key in customer_shipping_images:
                    row_dict["Pictures"] = list(customer_shipping_images[key])

            # Save preview in session
            request.session["excel_preview"] = preview_data
            request.session["selected_container"] = selected_container
            request.session["uploaded_excel_path"] = file_path

        except Exception as e:
            messages.error(request, f"Error processing Excel file: {e}")
            preview_data = None

        finally:
            if wb:
                wb.close()
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except PermissionError:
                print(f"Could not delete {file_path}, still in use.")

    return render(request, "upload_orders_excel.html", {
        "containers": containers,
        "preview_data": preview_data,
        "selected_container": selected_container,
        "MEDIA_URL": settings.MEDIA_URL,
    })


@admin_required
def confirm_orders_excel(request):
    preview_data = request.session.get("excel_preview")
    selected_container = request.session.get("selected_container")
    excel_file_path = request.session.get("uploaded_excel_path")

    if not preview_data or not selected_container:
        messages.error(request, "No preview data found. Please upload again.")
        return redirect("upload_orders_excel")

    container = get_object_or_404(Container, container_id=selected_container)
    missing_customers = []

    for row in preview_data:
        customer_id = str(row.get("CUSTOMER")).strip() if row.get("CUSTOMER") else None
        if not customer_id:
            continue

        customer = Customer.objects.filter(customer_id=customer_id).first()
        if not customer:
            missing_customers.append(customer_id)
            continue

        try:
            order = Order(
                customer=customer,
                container=container,
                shipping_mark=row.get("Shipping Mark") or None,
                description=row.get("Description") or None,
                item_no_spec=row.get("Item No. /Specification") or None,
                material=row.get("Material") or None,
                ctns=row.get("Ctns") or None,
                qty_per_ctn=row.get("Qty/Ctn") or None,
                total_qty=row.get("Total Qty") or None,
                unit=row.get("Unit") or None,
                cbm_per_ctn=row.get("CBM/Ctn") or None,
                cbm=row.get("CBM") or None,
                total_cbm=row.get("Total CBM") or None,
                wt_per_ctn=row.get("Wt/Ctn") or None,
                total_wt=row.get("Total Wt") or None,
                supplier=row.get("Supplier") or None,
            )

            # Handle multiple images
            if row.get("Pictures"):
                for img_relative_path in row["Pictures"]:
                    img_path = os.path.join(settings.MEDIA_ROOT, img_relative_path)
                    img_url = settings.MEDIA_URL + img_relative_path
                    # print(f"[CONFIRM DEBUG] Full path: {img_path}")
                    # print(f"[CONFIRM DEBUG] URL for browser: {img_url}")

                    if os.path.exists(img_path):
                        if not order.pictures:
                            order.pictures.save(
                                os.path.basename(img_path),
                                File(open(img_path, "rb")),
                                save=False
                            )

            order.save()

        except Exception as e:
            messages.warning(request, f"Error saving order for Customer {customer_id}: {e}")

    # Delete uploaded Excel file after processing
    if excel_file_path and os.path.exists(excel_file_path):
        try:
            os.remove(excel_file_path)
        except Exception as e:
            print(f"Could not delete uploaded Excel file: {e}")

    # Clear session
    request.session.pop("excel_preview", None)
    request.session.pop("selected_container", None)
    request.session.pop("uploaded_excel_path", None)

    if missing_customers:
        messages.warning(request, f"The following customer IDs were not found in database: {', '.join(missing_customers)}")

    messages.success(request, "Orders imported successfully!")
    return redirect("admin_dashboard")

# view_orders_by_container
@admin_required
def view_orders_by_container(request):
    containers = Container.objects.all()
    selected_container_id = request.GET.get("container")
    orders = []

    if selected_container_id:
        container = get_object_or_404(Container, container_id=selected_container_id)
        orders = Order.objects.filter(container=container).order_by("customer__customer_id")

    return render(request, "view_orders_by_container.html", {
        "containers": containers,
        "selected_container_id": selected_container_id,
        "orders": orders,
    })


@admin_required
def view_orders_by_customer(request):
    containers = Container.objects.all()
    selected_container_id = None
    selected_customer_id = None
    customers = []
    orders = []

    # ----- Decode container from GET -----
    container_signed = request.GET.get("container")
    if container_signed:
        try:
            selected_container_id = signing.loads(container_signed)
        except signing.BadSignature:
            selected_container_id = None

    # ----- Decode customer from GET -----
    customer_signed = request.GET.get("customer")
    if customer_signed:
        try:
            decoded = signing.loads(customer_signed)
            selected_container_id = decoded.get("container")
            selected_customer_id = decoded.get("customer")
        except signing.BadSignature:
            selected_customer_id = None

    container = None
    if selected_container_id:
        container = get_object_or_404(Container, container_id=selected_container_id)

        # Populate customer dropdown for selected container
        customers_raw = Order.objects.filter(container=container).values_list('customer__customer_id', flat=True).distinct()
        customers = []
        for c in customers_raw:
            signed_data = signing.dumps({'container': selected_container_id, 'customer': c})
            customers.append({'id': c, 'signed': signed_data})

    # Fetch orders only if both container and customer are selected
    if selected_container_id and selected_customer_id:
        orders = Order.objects.filter(
            container__container_id=selected_container_id,
            customer__customer_id=selected_customer_id
        )

    # Sign container IDs for dropdown
    signed_containers = []
    for c in containers:
        signed_containers.append({
            'id': c.container_id,
            'signed': signing.dumps(c.container_id)
        })

    return render(request, "view_orders_by_customer.html", {
        "containers": signed_containers,
        "selected_container_id": selected_container_id,
        "customers": customers,
        "selected_customer_id": selected_customer_id,
        "orders": orders,
    })



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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.core.files import File
from .models import Container, Order
from .utils import decrypt_text
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os
import io
import xlsxwriter

# ----------------------------
# List all containers for the logged-in user
# ----------------------------
# from .utils import encrypt_text  # assuming you have this utility

@customer_required
def user_containers(request):
    customer_id = request.session.get('customer_id')

    # Get unique containers for this customer
    containers = Container.objects.filter(order__customer_id=customer_id).distinct()

    # Prepare list of dicts with container and encrypted ID
    container_links = []
    for c in containers:
        container_links.append({
            "container": c,
            "enc_id": encrypt_text(c.container_id)
        })

    return render(request, "user_containers.html", {
        "container_links": container_links
    })

# ----------------------------
# Show orders inside a selected container (with images)
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
# Export orders to PDF (with images)
# ----------------------------

@customer_required
def export_orders_pdf(request, enc_container_id):
    customer_id = request.session.get('customer_id')
    container_id = decrypt_text(enc_container_id)
    container = get_object_or_404(Container, container_id=container_id)
    orders = Order.objects.filter(container=container, customer_id=customer_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    elements = []

    styles = getSampleStyleSheet()
    wrap_style = ParagraphStyle(
        name='wrap',
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        alignment=TA_LEFT,
        wordWrap='CJK'  # ensures long words wrap properly
    )

    # Title
    title = Paragraph(f"Orders for Container {container.container_id}", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Table headers
    data = [["Shipping Mark", "Description", "Item No", "Qty", "Supplier", "Picture"]]

    for o in orders:
        shipping_mark = Paragraph(o.shipping_mark or "", wrap_style)
        description = Paragraph(o.description or "", wrap_style)
        item_no = Paragraph(o.item_no_spec or "", wrap_style)
        qty = Paragraph(f"{o.total_qty or ''} {o.unit or ''}", wrap_style)
        supplier = Paragraph(o.supplier or "", wrap_style)

        # Image or "No Image"
        if o.pictures:
            img_path = os.path.join(settings.MEDIA_ROOT, o.pictures.name)
            if os.path.exists(img_path):
                img = Image(img_path, width=60, height=60)  # scaled image
            else:
                img = Paragraph("No Image", wrap_style)
        else:
            img = Paragraph("No Image", wrap_style)

        data.append([shipping_mark, description, item_no, qty, supplier, img])

    # Table with wider columns and top alignment
    table = Table(data, colWidths=[80, 200, 80, 50, 100, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('ALIGN',(0,1),(-2,-1),'LEFT'),  # left-align text except image
        ('ALIGN',(-1,1),(-1,-1),'CENTER'),  # center images
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.lightgrey, colors.whitesmoke])
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="orders_{container.container_id}.pdf"'
    return response


@customer_required
def export_orders_excel(request, enc_container_id):
    customer_id = request.session.get('customer_id')
    container_id = decrypt_text(enc_container_id)
    container = get_object_or_404(Container, container_id=container_id)
    orders = Order.objects.filter(container=container, customer_id=customer_id)

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Orders")

    # Set column widths for better display
    worksheet.set_column('A:A', 20)  # Shipping Mark
    worksheet.set_column('B:B', 40)  # Description
    worksheet.set_column('C:C', 20)  # Item No
    worksheet.set_column('D:D', 10)  # Qty
    worksheet.set_column('E:E', 25)  # Supplier
    worksheet.set_column('F:F', 15)  # Picture

    # Headers
    headers = ["Shipping Mark", "Description", "Item No", "Qty", "Supplier", "Picture"]
    header_format = workbook.add_format({'bold': True, 'bg_color': '#4F81BD', 'font_color': 'white', 'align': 'center'})
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)

    # Rows
    row_idx = 1
    for order in orders:
        worksheet.write(row_idx, 0, order.shipping_mark or "")
        worksheet.write(row_idx, 1, order.description or "")
        worksheet.write(row_idx, 2, order.item_no_spec or "")
        worksheet.write(row_idx, 3, f"{order.total_qty or ''} {order.unit or ''}")
        worksheet.write(row_idx, 4, order.supplier or "")

        # Insert image or "No Image"
        if order.pictures:
            img_path = os.path.join(settings.MEDIA_ROOT, order.pictures.name)
            if os.path.exists(img_path):
                # Insert scaled image
                worksheet.insert_image(row_idx, 5, img_path, {'x_scale': 0.5, 'y_scale': 0.5, 'object_position': 1})
            else:
                worksheet.write(row_idx, 5, "No Image")
        else:
            worksheet.write(row_idx, 5, "No Image")

        row_idx += 1

    workbook.close()
    output.seek(0)

    response = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename="orders_{container.container_id}.xlsx"'
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
