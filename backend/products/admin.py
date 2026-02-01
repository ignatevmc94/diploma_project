from django.contrib import admin
from .models import Product, Parameter
from .tasks import generate_product_thumbnails
# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.image:
            generate_product_thumbnails.delay(obj.id)


admin.site.register(Parameter)