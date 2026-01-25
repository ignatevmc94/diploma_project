from django.db import models
from django.conf import settings
from contacts.models import Contact
from products.models import ProductInfo
from django.db.models import Sum, F


class Order(models.Model):
    # возможные статусы заказа (корзина → новый → подтвержден → выполнен)
    STATUS_CHOICES = (
        ('cart', 'Корзина'),
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('done', 'Выполнен'),
    )

    # владелец заказа (покупатель)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    # общий статус заказа
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='cart'
    )

    # дата/время создания заказа
    created_at = models.DateTimeField(auto_now_add=True)

    # контакт доставки (адрес/телефон), может быть пустым пока заказ не подтвержден
    contact = models.ForeignKey(
        Contact,
        on_delete=models.PROTECT,
        related_name='orders',
        null=True,
        blank=True
    )

    @property
    def total_price(self):
        # итоговая сумма заказа = сумма (цена товара * количество) по всем позициям
        return (self.items.aggregate(
            total=Sum(
                F('product_info__price') * F('quantity')
            )
        )['total'] or 0)

    def __str__(self):
        # строковое представление заказа в админке/логах
        return f'Order {self.id} - {self.user.username} - {self.status}'


class OrderItem(models.Model):
    # статусы для каждой позиции заказа (нужно для поставщиков)
    STATUS_CHOICES = (
        ('cart', 'Корзина'),
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('done', 'Выполнен'),
    )

    # ссылка на заказ, к которому относится позиция
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )

    # конкретное предложение товара в магазине (ProductInfo = товар+магазин+цена+остаток)
    product_info = models.ForeignKey(
        ProductInfo,
        on_delete=models.CASCADE
    )

    # количество товара в позиции
    quantity = models.PositiveIntegerField()

    # статус позиции (может отличаться от общего статуса заказа)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    @property
    def total_price(self):
        # стоимость позиции = цена * количество
        return self.product_info.price * self.quantity

    def __str__(self):
        # отображение позиции в админке (сейчас просто имя покупателя)
        return self.order.user.username
