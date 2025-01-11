from aiohttp import request
from django.db import IntegrityError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from content.filters import CustomSearchFilter
from content.models import Profile, Post
from content.permissions import IsUserAllOwnIsAuthenticatedReadOnly

from content.serializers import (
    ProfileSerializer,
    PostSerializer,
    PostListSerializer,
    PostRetrieveSerializer,
    ProfileListSerializer,
    ProfileRetrieveSerializer,
    ProfilePictureSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    permission_classes = [IsUserAllOwnIsAuthenticatedReadOnly]
    serializer_class = ProfileSerializer
    filter_backends = [CustomSearchFilter]
    search_fields = ["nickname", "first_name", "last_name", "birth_date"]

    def get_queryset(self):
        queryset = Profile.objects.select_related("user").prefetch_related(
            "followers", "following"
        )
        return queryset

    def get_serializer_class(self):
        if self.action in (
            "list",
            "retrieve",
        ):
            return ProfileListSerializer
        if self.action in (
            "update",
            "partial_update",
        ):
            return ProfileRetrieveSerializer
        if self.action == "upload_profile_picture":
            return ProfilePictureSerializer
        return ProfileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"detail": "You can only create one profile."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        methods=["post"],
        detail=True,
        permission_classes=(IsUserAllOwnIsAuthenticatedReadOnly,),
        url_path="upload_profile_picture",
    )
    def upload_profile_picture(self, request, pk=None):
        bus = self.get_object()
        serializer = self.get_serializer(bus, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostRetrieveSerializer
        # if self.action == "upload_media":
        #     return PostMediaSerializer
        return PostSerializer

    @action(
        methods=["post", "get"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        url_path="upload-media",
    )
    def upload_media(self, request, pk=None):
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
