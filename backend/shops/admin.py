from django.contrib import admin
from .models import Shop
from products.models import ProductInfo
# Register your models here.


class ProductInfoInline(admin.TabularInline):
    model = ProductInfo
    extra = 0
    fields = ("product", "price", "price_rrc", "quantity")
    readonly_fields = ()
    show_change_link = True


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "is_accepting_orders")
    inlines = [ProductInfoInline]