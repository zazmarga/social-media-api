from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from user.authentication import SocialMediaTokenAuthentication
from user.models import InvalidToken
from user.serializers import UserSerializer, UserUpdateSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = ()


class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data["token"])

        InvalidToken.objects.filter(token=token.key).delete()

        token.delete()
        new_token, created = Token.objects.get_or_create(user=token.user)

        return Response({"token": new_token.key}, status=status.HTTP_200_OK)


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    authentication_classes = (SocialMediaTokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token = request.auth
        InvalidToken.objects.create(token=token)
        return Response(status=status.HTTP_204_NO_CONTENT)
