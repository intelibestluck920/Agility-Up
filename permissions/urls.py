from django.urls import path
from .views import *

app_name = 'permissions'

urlpatterns = [
    path('', Permissions.as_view(), name='permissions'),
]
