# from rest_framework.authtoken.views import ObtainAuthToken
# from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from allauth.account.admin import EmailAddress
from rest_framework.views import APIView
from .models import User
from .serializers import UserInforSerializer, UserDeactivateSerializer
from rest_framework.permissions import IsAuthenticated
from allauth.account.models import EmailAddress
from rest_framework import status
from core.models import Team, TeamMembers
from product.models import ProductArea, ProductAreaMembers, Product, ProductMembers
from django.db.models import Q


#
# class CloseAccount(APIView):


class UserList(APIView):
    def get(self, request):
        obj = User.objects.all()
        serializer = UserInforSerializer(obj, many=True)
        return Response(data=serializer.data)


class DeactivateAccount(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        serializer = UserDeactivateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data['email']
            user = EmailAddress.objects.get(email=email)
            user.verified = False
            user.save()
            successor_id = serializer.data['successor']
            successor = User.objects.get(id=successor_id)
            teams = Team.objects.filter(team_lead_id=user.user.id).values('id').update(team_lead_id=successor.id)
            product_areas = ProductArea.objects.filter(
                Q(product_area_creator_id=user.user.id) | Q(product_area_lead_id=user.user.id))\
                .update(product_area_creator_id=successor.id, product_area_lead_id=successor.id)
            products = Product.objects.filter(
                Q(product_creator_id=user.user.id) | Q(product_lead_id=user.user.id))\
                .update(product_creator_id=successor.id, product_lead_id=successor.id)

            return Response(status=status.HTTP_200_OK)

