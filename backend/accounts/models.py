from django.db import models
from django.contrib.auth.models import AbstractUser
from easy_thumbnails.fields import ThumbnailerImageField

# Create your models here.

class User(AbstractUser):
    """
    Кастомный пользователь.
    """
    email = models.EmailField(unique=True)

    avatar = ThumbnailerImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    

    
