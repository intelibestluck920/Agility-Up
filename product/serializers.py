from rest_framework import serializers
from .models import *
from core.serializers import TeamSerializer
from accounts.serializers import UserInforSerializer


class CreateProductAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductArea
        fields = ('id', 'name',)


class ListProductAreaSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(read_only=True, many=True)

    class Meta:
        model = ProductArea
        fields = ('id', 'name', 'product_area_creator', 'product_area_lead', 'teams')


class ProductAreaTeamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAreaTeams
        fields = ('Team',)


class CreateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name')


class ListProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'product_creator', 'product_lead', 'product_areas')


class ProductTeamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTeams
        fields = ('Product_Area',)


class EnterpriseProductsSerializer(serializers.ModelSerializer):
    Product = serializers.ListField(
        child=serializers.IntegerField(label='prod_id')
    )

    class Meta:
        model = EnterpriseProducts
        fields = ('Product',)


class ListEnterpriseSerializer(serializers.ModelSerializer):
    Product = ListProductSerializer(many=True, read_only=True)

    class Meta:
        model = Enterprise
        fields = ('Product',)


class ProductAreaMembersSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductAreaMembers
        fields = ('id', 'User', 'Product_Area')


class ProductMembersSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductMembers
        fields = ('id', 'User', 'Product')

