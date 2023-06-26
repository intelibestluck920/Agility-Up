from django.db import models
from accounts.models import User


# Create your models here.


class assigned_permissions(models.Model):
    product_area = models.BooleanField(null=True, blank=True, default=False)
    product = models.BooleanField(null=True, blank=True, default=False)
    team = models.BooleanField(null=True, blank=True, default=True)
    enterprise = models.BooleanField(null=True, blank=True, default=True)
    profile = models.BooleanField(null=True, blank=True, default=False)
    billing = models.BooleanField(null=True, blank=True, default=False)

    email = models.EmailField(max_length=125)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)

    user_exists = models.BooleanField()