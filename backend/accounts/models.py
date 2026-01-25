from django.db import models
from django.contrib.auth.models import AbstractUser, User

# Create your models here.

class User(AbstractUser):
    """
    Кастомный пользователь.
    """
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


    
