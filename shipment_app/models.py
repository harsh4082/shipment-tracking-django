from django.db import models
from datetime import date
import string
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

# -----------------------------
# 1) Container Table
# -----------------------------
# import string
# from datetime import date
# from django.db import models



#------------------------------------
#new


class FieldVisibility(models.Model):
    FIELD_CHOICES = [
        ('shipping_mark', 'Shipping Mark'),
        ('description', 'Description'),
        ('item_no_spec', 'Item No./Specification'),
        ('material', 'Material'),
        ('pictures', 'Pictures'),
        # ... add all other fields you want to control
    ]

    field_name = models.CharField(max_length=50, unique=True, choices=FIELD_CHOICES)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.get_field_name_display()

class Customer(models.Model):
    # ... your existing fields: customer_id, name, user_id, email, etc.
    date_joined = models.DateTimeField(auto_now_add=True)

    def get_initials(self):
        if self.name:
            parts = self.name.split()
            return parts[0][0].upper() + (parts[-1][0].upper() if len(parts) > 1 else '')
        return '?'
    
#NEW
#---------------------------------------


class Container(models.Model):
    container_id = models.CharField(max_length=50, unique=True, primary_key=True)
    container_no = models.CharField(max_length=100)
    container_name = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.container_id:
            today = date.today().strftime("%d%b%Y")  # e.g., 01Oct2025

            # Get the last container for today (highest letter at the end)
            last_container = (
                Container.objects.filter(container_id__startswith=today)
                .order_by("-container_id")
                .first()
            )

            if last_container:
                # Take last letter and increment
                last_letter = last_container.container_id[-1]
                if last_letter == "Z":
                    raise ValueError("Maximum containers reached for today (A-Z)")
                next_letter = chr(ord(last_letter) + 1)
            else:
                next_letter = "A"

            self.container_id = f"{today}{next_letter}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.container_id} - {self.container_name}"


# -----------------------------
# 2) Custom Admin Table
# -----------------------------

class AdminTable(models.Model):
    admin_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=200)  # hashed
    date_joined = models.DateTimeField(default=timezone.now)  # safer for migrations
    is_active = models.BooleanField(default=True)

    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Check password"""
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        # Hash password before saving if not already hashed
        if self.password and not self.password.startswith("pbkdf2_"):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user_id

# -----------------------------
# 3) Customer Table
# -----------------------------
class Customer(models.Model):
    customer_id = models.CharField(max_length=20, primary_key=True)  # Admin sets manually
    name = models.CharField(max_length=100)
    user_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=200)  # hashed
    email = models.EmailField()
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    is_first_login = models.BooleanField(default=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        if not self.password.startswith("pbkdf2_"):
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer_id} - {self.name}"


# -----------------------------
# 4) Order Table
# -----------------------------
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # NOT NULL
    container = models.ForeignKey(Container, on_delete=models.CASCADE)  # NOT NULL

    shipping_mark = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    item_no_spec = models.CharField(max_length=100, blank=True, null=True)
    material = models.CharField(max_length=100, blank=True, null=True)
    pictures = models.ImageField(upload_to="order_pics/", blank=True, null=True)  # only first image
    ctns = models.IntegerField(blank=True, null=True)
    qty_per_ctn = models.IntegerField(blank=True, null=True)
    total_qty = models.IntegerField(blank=True, null=True)
    unit = models.CharField(max_length=50, blank=True, null=True)
    cbm_per_ctn = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cbm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_cbm = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    wt_per_ctn = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_wt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    supplier = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Order for {self.customer.name} - {self.shipping_mark or 'N/A'}"

# models.py

# models.py

class OrderFieldVisibility(models.Model):
    FIELD_CHOICES = [
        ("shipping_mark", "Shipping Mark"),
        ("description", "Description"),
        ("item_no_spec", "Item No/Spec"),
        ("material", "Material"),
        ("ctns", "CTNs"),
        ("qty_per_ctn", "Qty/CTN"),
        ("total_qty", "Total Qty"),
        ("unit", "Unit"),
        ("cbm_per_ctn", "CBM/CTN"),
        ("cbm", "CBM"),
        ("total_cbm", "Total CBM"),
        ("wt_per_ctn", "Wt/CTN"),
        ("total_wt", "Total Wt"),
        ("supplier", "Supplier"),
        ("pictures", "Picture"),
    ]

    field_name = models.CharField(max_length=50, choices=FIELD_CHOICES, unique=True)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_field_name_display()} - {'Visible' if self.is_visible else 'Hidden'}"
