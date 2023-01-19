from django.contrib import admin
from .models import Customer, Bouquet, Order, Category


admin.site.register(Customer)
admin.site.register(Bouquet)
admin.site.register(Order)
admin.site.register(Category)
