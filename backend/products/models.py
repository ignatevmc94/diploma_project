from django.db import models
from shops.models import Shop, Category



class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        related_name='products', 
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
    

class ProductInfo(models.Model):
    product = models.ForeignKey(
        Product, 
        related_name='product_infos', 
        on_delete=models.CASCADE
    )
    shop = models.ForeignKey(
        Shop, 
        related_name='products', 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_rrc = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ('product', 'shop')

    def __str__(self):
        return f"{self.product.name} - {self.shop.name} - {self.price}"


class Parameter(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class ProductParameter(models.Model):
    product_info = models.ForeignKey(
        ProductInfo, 
        related_name='parameters', 
        on_delete=models.CASCADE
    )
    parameter = models.ForeignKey(
        Parameter, 
        on_delete=models.CASCADE
    )
    value = models.CharField(max_length=255)









