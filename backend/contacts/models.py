from django.db import models
from django.conf import settings
# Create your models here.


class Contact(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contacts'
    )
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    house = models.CharField(max_length=10)
    apartment = models.CharField(max_length=10, blank=True, null=True)
    