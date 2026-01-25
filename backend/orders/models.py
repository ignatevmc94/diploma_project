from django.db import models
from django.conf import settings
from contacts.models import Contact
from products.models import ProductInfo
from django.db.models import Sum, F

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
    created_at = models.DateTimeField(auto_now_add=True)
    contact = models.ForeignKey(
        Contact,
        on_delete=models.PROTECT,
        related_name='orders',
        null=True,
        blank=True
    )


    @property
    def total_price(self):
        return (self.items.aggregate(
            total=Sum(
                F('product_info__price') * F('quantity')
            )
        )['total'] or 0)

    def __str__(self):
        return f'Order {self.id} - {self.user.username} - {self.status}'
    

class OrderItem(models.Model):
    STATUS_CHOICES = (
        ('cart', 'Корзина'),
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('done', 'Выполнен'),
    )

    order = models.ForeignKey(
        Order, 
        related_name='items',
        on_delete=models.CASCADE
        
    )
    product_info = models.ForeignKey(
        ProductInfo, 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new'
    )

    @property
    def total_price(self):
        return self.product_info.price * self.quantity

    def __str__(self):
        return self.order.user.username





