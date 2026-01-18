from django.contrib import admin
from .models import Order, OrderItem
# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_info', 'total_price')
    fields = ('product_info', 'quantity', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at')
    list_filter = ('status',)
    inlines = [OrderItemInline]