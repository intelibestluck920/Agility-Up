from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import assigned_permissions
from accounts.models import User
from django.contrib.auth.models import Group


@receiver(post_save, sender=assigned_permissions)
def assign_permissions(sender, instance, created, **kwargs):
    if created and instance.user_exists:
        user = User.objects.get(id=instance.user.id)
        if instance.product_area:
            grp = Group.objects.get(name='Product Area')
            user.groups.add(grp)
            user.save()
        if instance.product:
            grp = Group.objects.get(name='Product')
            user.groups.add(grp)
            user.save()
        if instance.team:
            grp = Group.objects.get(name='Team')
            user.groups.add(grp)
            user.save()
        if instance.enterprise:
            grp = Group.objects.get(name='Enterprise')
            user.groups.add(grp)
            user.save()



