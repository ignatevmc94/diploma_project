from django.contrib import admin
from .models import Order, OrderItem
# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_info', 'total_price', 'get_shop')
    fields = ('product_info', 'get_shop', 'quantity', 'total_price', 'status')

    def get_shop(self, obj):
        if obj.product_info and obj.product_info.shop:
            return obj.product_info.shop.name
        return "-"
    get_shop.short_description = "Shop"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [OrderItemInline]