from django.urls import path, include
from dj_rest_auth.registration.views import VerifyEmailView, ConfirmEmailView, RegisterView
from .views import UserList, DeactivateAccount
app_name = 'account'

urlpatterns = [
    # path('', include('dj_rest_auth.urls')),
    path('registration/account-confirm-email/<str:key>/',
        ConfirmEmailView.as_view()),
    # path('registration/', include('dj_rest_auth.registration.urls')),
    # path('registration/', RegisterView.as_view()),
    path('account-confirm-email/', VerifyEmailView.as_view(), name='account_email_verification_sent'),
]
