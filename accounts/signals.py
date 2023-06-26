from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Group
from django.dispatch import receiver
from core.models import TeamMembers, Team
from invites.models import Invite
from product.models import Enterprise, ProductMembers, ProductAreaMembers
from permissions.models import assigned_permissions


@receiver(user_signed_up)
def user_signed_up(request, user, **kwargs):
    if Invite.objects.filter(invitee=user.email, accepted=False).exists():
        invite = Invite.objects.filter(invitee=user.email, accepted=False)
        for invi in invite:
            if invi.Team is not None:
                team_member = TeamMembers.objects.create(team_id=invi.Team.id, member=user)
                team_member.save()
                invi.accepted = True
                invi.save()
            if invi.product is not None:
                ProductMembers.objects.create(User=user, Product_id=invi.product.id)
                invi.accepted = True
                invi.accepted
                invi.save()
            if invi.product_Area is not None:
                ProductAreaMembers.objects.create(User=user, Product_Area_id=invi.product_Area.id)
                invi.accepted = True
                invi.accepted
                invi.save()

    # auto create enterprise
    Enterprise.objects.create(owner=user)


    try:
        perms = assigned_permissions.objects.get(email__exact=user.email, user_exists=False)
        if perms.product_area:
            grp = Group.objects.get(name='Product Area')
            user.groups.add(grp)
            user.save()
        if perms.product:
            grp = Group.objects.get(name='Product')
            user.groups.add(grp)
            user.save()
        if perms.team:
            grp = Group.objects.get(name='Team')
            user.groups.add(grp)
            user.save()
        if perms.enterprise:
            grp = Group.objects.get(name='Enterprise')
            user.groups.add(grp)
            user.save()
        perms.user_exists = True
        perms.save()

    except:
        # assign default team access
        grp = Group.objects.get(name='Team')
        user.groups.add(grp)
        user.save()
