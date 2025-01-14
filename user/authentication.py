from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication

from user.models import InvalidToken


class SocialMediaTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        if InvalidToken.objects.filter(token=key).exists():
            raise exceptions.AuthenticationFailed("Token is invalid")
        return super().authenticate_credentials(key)
