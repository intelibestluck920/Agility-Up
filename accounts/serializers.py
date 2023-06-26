from django.db import transaction
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import PasswordResetSerializer
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls.base import reverse
from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import user_pk_to_url_str, user_username
from dj_rest_auth.forms import AllAuthPasswordResetForm
from rest_framework.authtoken.models import Token
from accounts.models import User
from allauth.account.models import EmailAddress


class UserInforSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')


class UserInfominimal(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name',)


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """
    user = UserInforSerializer(many=False, read_only=True)  # this is add by myself.

    class Meta:
        model = Token
        fields = ('key', 'user')  # there I add the `user` field ( this is my need data ).


class CustomRegisterSerializer(RegisterSerializer):
    email = serializers.EmailField(allow_blank=False, required=True)
    first_name = serializers.CharField(max_length=200, allow_blank=False, required=True)
    last_name = serializers.CharField(max_length=200, allow_blank=False, required=True)

    # Define transaction.atomic to rollback the save operation in case of error
    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        user.email = self.data.get('email')
        user.first_name = self.data.get('first_name')
        user.last_name = self.data.get('last_name')
        user.save()
        print(request.session.get('team-id'))
        return user


# class MyPasswordResetSerializer(PasswordResetSerializer):
#
#     def get_email_options(self):
#         print('get email options')
#
#         dict = {
#             'html_email_template_name': 'account/email/password_reset_key.txt',
#             'domain_override': '://www.agilityup.ai/change-password/',
#             'test': 'test',
#         }
#         print(dict)
#
#         return dict
#         # {
#         #     # 'email_template_name': 'templates/account/email/password_reset_key.txt',
#         #     'html_email_template_name': 'account/email/password_reset_key.txt',
#         #     'domain_override': '://www.agilityup.ai/change-password/',
#         #     'test': 'test',
#         # }


class CustomAllAuthPasswordResetForm(AllAuthPasswordResetForm):
    def save(self, request, **kwargs):
        current_site = get_current_site(request)
        email = self.cleaned_data['email']
        token_generator = kwargs.get('token_generator',
                                     default_token_generator)

        for user in self.users:

            temp_key = token_generator.make_token(user)

            # save it to the password reset model
            # password_reset = PasswordReset(user=user, temp_key=temp_key)
            # password_reset.save()

            # send the password reset email
            path = reverse(
                'password_reset_confirm',
                args=[user_pk_to_url_str(user), temp_key],
            )
            # url = build_absolute_uri(None, path)  # PASS NONE INSTEAD OF REQUEST
            url = 'http://www.agilityup.ai/change-password/' + user_pk_to_url_str(user) + '/' + temp_key + '/'
            context = {
                'current_site': current_site,
                'user': user,
                'password_reset_url': url,
                'request': request,
            }
            if app_settings.AUTHENTICATION_METHOD != app_settings.AuthenticationMethod.EMAIL:
                context['username'] = user_username(user)
            get_adapter(request).send_mail('account/email/password_reset_key',
                                           email, context)
        return self.cleaned_data['email']


class CustomPasswordResetSerializer(PasswordResetSerializer):
    @property
    def password_reset_form_class(self):
        return CustomAllAuthPasswordResetForm


class UserDeactivateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    successor = serializers.IntegerField()

    class Meta:
        fields = ('email', 'successor')
