from accounts.models import User
from django.contrib.auth.models import Group
from rest_framework import permissions


class IsTeam(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='Team').exists():
            return True
        else:
            return False


class IsProductArea(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='Product Area').exists():
            return True
        else:
            return False


class IsProduct(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='Product').exists():
            return True
        else:
            return False


class IsEnterprise(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='Enterprise').exists():
            return True
        else:
            return False
