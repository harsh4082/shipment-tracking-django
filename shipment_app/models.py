from django.db import models
from datetime import date
import string
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

# -----------------------------
# 1) Container Table
# -----------------------------
class Container(models.Model):
    container_id = models.CharField(max_length=50, unique=True, primary_key=True)
    container_no = models.CharField(max_length=100)
    container_name = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        # Auto-generate container_id if not provided
        if not self.container_id:
            today = date.today().strftime("%d%b%Y")  # e.g., 28Sep2025
            existing_count = Container.objects.filter(container_id__startswith=today).count()
            letter = string.ascii_uppercase[existing_count]  # A, B, C...
            self.container_id = f"{today}{letter}"
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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shipping_mark = models.CharField(max_length=200)
    description = models.TextField()
    item_no_spec = models.CharField(max_length=100)
    material = models.CharField(max_length=100, blank=True, null=True)
    pictures = models.ImageField(upload_to="order_pics/", blank=True, null=True)
    ctns = models.IntegerField()
    qty_per_ctn = models.IntegerField()
    total_qty = models.IntegerField()
    unit = models.CharField(max_length=50)
    cbm_per_ctn = models.DecimalField(max_digits=10, decimal_places=2)
    cbm = models.DecimalField(max_digits=10, decimal_places=2)
    total_cbm = models.DecimalField(max_digits=10, decimal_places=2)
    wt_per_ctn = models.DecimalField(max_digits=10, decimal_places=2)
    total_wt = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.CharField(max_length=100)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)

    def __str__(self):
        return f"Order for {self.customer.name} - {self.shipping_mark}"
