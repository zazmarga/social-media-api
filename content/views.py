from aiohttp import request
from django.db import IntegrityError
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from content.filters import CustomSearchFilter
from content.models import Profile, Post, Relation
from content.permissions import IsUserAllOwnIsAuthenticatedReadOnly

from content.serializers import (
    ProfileSerializer,
    PostSerializer,
    PostListSerializer,
    PostRetrieveSerializer,
    ProfileListSerializer,
    ProfilePictureSerializer,
    RelationAddFollowingSerializer,
    RelationFollowersSerializer,
    RelationFollowingSerializer,
    RelationRetrieveFollowingSerializer,
    ProfileRetrieveSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    permission_classes = [IsUserAllOwnIsAuthenticatedReadOnly]
    serializer_class = ProfileSerializer
    filter_backends = [CustomSearchFilter]
    search_fields = ["username", "first_name", "last_name", "birth_date"]

    def get_queryset(self):
        queryset = Profile.objects.select_related("user").prefetch_related(
            "followers", "following"
        )
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        if self.action == "retrieve":
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
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class RelationFollowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Relation.objects.all()
    permission_classes = [IsUserAllOwnIsAuthenticatedReadOnly]
    serializer_class = RelationFollowingSerializer

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if self.action in (
            "list",
            "retrieve",
        ):
            queryset = Relation.objects.filter(follower__user=user)
        if self.action in ("create",):
            following_ids = Relation.objects.filter(follower__user=user).values_list(
                "following__id", flat=True
            )
            print(following_ids)
            queryset = (
                Relation.objects.filter(follower__user=user)
                .exclude(following__id__in=following_ids)
                .exclude(following__user=user)
            )
            print(queryset)
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RelationRetrieveFollowingSerializer
        if self.action == "create":
            return RelationAddFollowingSerializer
        return RelationFollowingSerializer

    def perform_create(self, serializer):
        follower_profile = self.request.user.profile
        following_profile = serializer.validated_data["following"]

        if Relation.objects.filter(
            follower=follower_profile.id, following=following_profile.id
        ).exists():
            return Response(
                {"detail": "You are already following this profile."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Relation.objects.create(follower=follower_profile, following=following_profile)


class RelationFollowersViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Relation.objects.all()
    permission_classes = [IsUserAllOwnIsAuthenticatedReadOnly]
    serializer_class = RelationFollowersSerializer

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if self.action in (
            "list",
            "retrieve",
        ):
            queryset = Relation.objects.filter(following__user=user)
        return queryset


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
