from django.contrib import admin
from .models import Customer, Bouquet, Order, Category


admin.site.register(Customer)
admin.site.register(Bouquet)
admin.site.register(Order)
admin.site.register(Category)

# @admin.register(Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = (
#         'name', 'delivery_date', 'delivery_time'
#     )
#
#
# @admin.register(Bouquet)
# class BouquetAdmin(admin.ModelAdmin):
#     list_display = (
#         'title', 'price'
#     )
