from django.db import models

# Create your models here.


class Shop(models.Model):
    """
    Модель магазина.
    """
    name = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    """
    Модель категории товаров.
    """
    name = models.CharField(max_length=255)
    shops = models.ManyToManyField(Shop, related_name='categories')

    def __str__(self):
        return self.name