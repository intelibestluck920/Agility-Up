from rest_framework import serializers


class ProductInviteSerializer(serializers.Serializer):
    product = serializers.IntegerField(allow_null=True)
    product_area = serializers.IntegerField(allow_null=True)
    email = serializers.EmailField()
