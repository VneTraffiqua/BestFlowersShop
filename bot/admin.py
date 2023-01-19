from django.contrib import admin
from .models import Customer, Bouquet, Order, Category, Flower


# admin.site.register(Customer)
# admin.site.register(Bouquet)
# admin.site.register(Order)
admin.site.register(Category)
admin.site.register(Flower)


class OrdersInline(admin.TabularInline):
    model = Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'address', 'delivery_date', 'delivery_time'
    )


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'price', 'category'
    )
    list_filter = ('category', 'flowers')


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    inlines = [
        OrdersInline
    ]
