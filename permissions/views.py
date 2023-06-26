from accounts.models import User
from django.contrib.auth.models import Group
from core.models import *
from product.models import *
from .serailizers import PermissionsSerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# Create your views here.


class Permissions(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = PermissionsSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            valid_data = request.data
            id = valid_data['user']
            print(serializer.validated_data)

            user = User.objects.get(id=id)
            email = user.email
            serializer.save(email=email, user_exists=True)

        return Response(status=status.HTTP_201_CREATED)
