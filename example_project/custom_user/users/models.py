from django.db import models
from django.contrib.auth.models import AbstractUser
from users.managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(null=True, blank=True)
    full_name = models.CharField(max_length=35)
    phone = models.CharField(max_length=10, unique=True)
    objects = UserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return "{}".format(self.full_name)
