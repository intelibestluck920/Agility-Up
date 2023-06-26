"""AgilityUp_2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from dj_rest_auth.registration.views import VerifyEmailView, ConfirmEmailView, RegisterView
from dj_rest_auth.views import PasswordResetConfirmView
from accounts.views import UserList, DeactivateAccount

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'account/registration/account-confirm-email/<str:key>/',
        ConfirmEmailView.as_view()),
    # path('account/', include('dj_rest_auth.urls')),
    #path('account/registration/', include('dj_rest_auth.registration.urls')),
    path('account/registration/', RegisterView.as_view()),
    # path('account/account-confirm-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    path(
        'account/password/reset/confirm/<slug:uidb64>/<slug:token>/',
        PasswordResetConfirmView.as_view(), name='password_reset_confirm'
    ),
    path('account/user-list/', UserList.as_view(), name='user_list'),
    path('account/deactivate/', DeactivateAccount.as_view(), name='deactivate_account'),

    path('', include('core.urls')),
    path('product/', include('product.urls')),
    path('permissions/', include('permissions.urls')),
    # path('account/', include('accounts.urls')),
]

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns += [
    # path('swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    #path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
