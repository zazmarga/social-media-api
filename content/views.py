from django.db import IntegrityError
from django.db.models import Count, Q
from django_filters import rest_framework as filters
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from content.filters import (
    ProfileSearchFilter,
    PostFilter,
)
from content.models import Profile, Post, Relation, PostMedia, Comment, Like
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
    PostMediaSerializer,
    CommentSerializer,
    CommentAddSerializer,
    LikeDislikeAddSerializer,
)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    permission_classes = [IsUserAllOwnIsAuthenticatedReadOnly]
    serializer_class = ProfileSerializer
    filter_backends = [ProfileSearchFilter]
    search_fields = ["username", "first_name", "last_name", "birth_date"]

    def get_queryset(self):
        queryset = Profile.objects.select_related("user").prefetch_related(
            "followers", "following"
        )
        return queryset

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

    def list(self, request, *args, **kwargs):
        """
        Get list of profiles
        (optional: filtered by username, last_name, first_name (ex. 'mark')
            or by birth_date (ex. '1-28') )
        """
        return super().list(request, *args, **kwargs)


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

    def list(self, request, *args, **kwargs):
        """
        Get a list of profiles that the current user is following
        """
        return super().list(request, *args, **kwargs)


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

    def list(self, request, *args, **kwargs):
        """
        Get a list of profiles that are followers of the current user
        """
        return super().list(request, *args, **kwargs)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsUserAllOwnIsAuthenticatedReadOnly]
    filter_backends = [
        filters.DjangoFilterBackend,
    ]
    filterset_class = PostFilter
    search_fields = ["hashtags", "title", "content"]

    def get_queryset(self):
        queryset = Post.objects.select_related("owner__user").prefetch_related(
            "comments",
            "likes",
            "media_files",
        )
        if self.action == "list":
            queryset = Post.objects.annotate(
                is_liked=Count("likes", filter=Q(likes__is_liked=True), distinct=True),
                is_unliked=Count(
                    "likes", filter=Q(likes__is_unliked=True), distinct=True
                ),
                nums_of_comments=Count("comments"),
            ).filter(is_draft=False)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostRetrieveSerializer
        if self.action == "upload_media":
            return PostMediaSerializer
        if self.action == "add_comment":
            return CommentAddSerializer
        if self.action == "add_like_or_dislike":
            return LikeDislikeAddSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)

    @action(
        methods=["post"],
        detail=True,
        permission_classes=(IsUserAllOwnIsAuthenticatedReadOnly,),
        url_path="upload-media",
    )
    def upload_media(self, request, pk=None):
        post = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        media = serializer.validated_data.pop("media")
        post_media = PostMedia.objects.create(post=post, media=media)
        post_media.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
    )
    def add_comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentAddSerializer(
            data=request.data, context={"request": request, "post": post}
        )
        if serializer.is_valid():
            comment = serializer.save()
            print(comment)
            post.comments.add(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def add_like_or_dislike(self, request, pk=None):
        post = self.get_object()
        serializer = LikeDislikeAddSerializer(
            data=request.data, context={"request": request, "post": post}
        )
        if serializer.is_valid():
            like, created = Like.objects.update_or_create(
                post=post,
                owner=request.user.profile,
                defaults={
                    "is_liked": serializer.validated_data["is_liked"],
                    "is_unliked": serializer.validated_data["is_unliked"],
                },
            )
            if created:
                post.likes.add(like)
            if not created:
                if like.is_liked == like.is_unliked == False:
                    post.likes.remove(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        """
        Get a list of posts of all user-owners
        (optional: filtered - Liked by me (ex. True), all posts of any user-owner (ex. 4),
        any string in hashtags, title or content)
        """
        return super().list(request, *args, **kwargs)


class CommentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Comment.objects.all()
    permission_classes = [IsUserAllOwnIsAuthenticatedReadOnly]
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = self.queryset
        queryset = queryset.select_related("owner").prefetch_related("posts")
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)
