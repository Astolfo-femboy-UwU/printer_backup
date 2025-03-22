from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    class Meta:
        app_label = "main_app"
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.TextField(max_length=100, blank=True)
    last_name = models.TextField(max_length=100, blank=True)
    username = models.TextField(max_length=25, blank=True)
    email = models.EmailField(null=True, blank=True)
