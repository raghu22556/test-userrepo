# authapp/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add your custom field
    login = models.CharField(max_length=50, unique=True, null=False, blank=False)
    # password = models.CharField(max_length=50, unique=False, null=False, blank=False)


    def __str__(self):
        return self.username
