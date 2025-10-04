from django.contrib import admin
from django.utils import timezone
from django.db.models.signals import post_migrate
from django.db.utils import IntegrityError

from .models import Container, AdminTable, Customer, Order, OrderFieldVisibility

# Register models in admin panel
admin.site.register(Container)
admin.site.register(AdminTable)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderFieldVisibility)


# --- Create default admin only once ---
def create_default_admin(sender, **kwargs):
    """Create a default admin/admin user if not exists"""
    try:
        if not AdminTable.objects.filter(user_id="admin").exists():
            default_admin = AdminTable(
                user_id="admin",
                password="admin",   # will be hashed in model.save()
                date_joined=timezone.now(),
                is_active=True,
            )
            default_admin.save()
            print("✅ Default admin user created: user_id='admin', password='admin'")
        else:
            print("ℹ️ Default admin user already exists, skipping.")
    except IntegrityError:
        print("⚠️ Could not create default admin (maybe already exists).")


# Connect signal to run after migrate (only for shipment_app)
post_migrate.connect(create_default_admin, sender=AdminTable._meta.app_config)
