from django.contrib import admin
from .models import Container, AdminTable, Customer, Order, OrderFieldVisibility

admin.site.register(Container)
admin.site.register(AdminTable)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderFieldVisibility)
