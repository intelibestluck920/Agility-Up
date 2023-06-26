from rest_framework import serializers
from .models import *


class PermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = assigned_permissions
        exclude = ['email', 'user_exists', 'profile', 'billing']


    # def create(self, validated_data):
    #     print(validated_data)
