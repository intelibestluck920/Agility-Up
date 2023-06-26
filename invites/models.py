from django.db import models
from accounts.models import User
from core.models import Team
from product.models import ProductArea, Product


# Create your models here.
class Invite(models.Model):
    invitee = models.EmailField()

    Inviter = models.ForeignKey(User, on_delete=models.CASCADE)
    Team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    product_Area = models.ForeignKey(ProductArea, on_delete=models.CASCADE, null=True, blank=True)

    invite_date = models.DateTimeField(auto_now_add=True)

    accepted = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
