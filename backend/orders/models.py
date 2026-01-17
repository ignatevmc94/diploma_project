from django.db import models
from django.conf import settings
from products.models import ProductInfo

# Create your models here.


class Order(models.Model):
    STATUS_CHOICES = (
        ('cart', 'Корзина'),
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('done', 'Выполнен'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='cart'
    )
    crated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.id} - {self.user.username} - {self.status}'
    

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product_info = models.ForeignKey(
        ProductInfo, 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()





