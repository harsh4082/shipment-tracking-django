from django.contrib import admin
from .models import Container, AdminTable, Customer, Order

admin.site.register(Container)
admin.site.register(AdminTable)
admin.site.register(Customer)
admin.site.register(Order)
