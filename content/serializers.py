from datetime import datetime

from rest_framework import serializers

from content.models import Profile, Post, Relation, PostMedia, Comment, Like
from django.contrib.auth import get_user_model


User = get_user_model()


class RelationFollowersSerializer(serializers.ModelSerializer):
    profile = serializers.ReadOnlyField(source="follower.full_name")

    class Meta:
        model = Relation
        fields = ("id", "profile", "created_at")


class RelationFollowingSerializer(serializers.ModelSerializer):
    profile = serializers.ReadOnlyField(source="following.full_name")

    class Meta:
        model = Relation
        fields = ("id", "profile", "created_at")


class RelationRetrieveFollowingSerializer(serializers.ModelSerializer):
    profile = serializers.ReadOnlyField(source="following.full_name")

    class Meta:
        model = Relation
        fields = ("id", "profile", "created_at")


class RelationAddFollowingSerializer(serializers.ModelSerializer):
    follower = serializers.HiddenField(default=serializers.CurrentUserDefault())
    following = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.none())

    class Meta:
        model = Relation
        fields = ("id", "follower", "following", "created_at")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request:
            following_ids = Relation.objects.filter(
                follower=request.user.profile
            ).values_list("following__id", flat=True)

            self.fields["following"].queryset = Profile.objects.exclude(
                user=request.user
            ).exclude(id__in=following_ids)


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "gender",
            "birth_date",
            "bio",
            "created_at",
        )


class ProfileListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "gender",
            "birth_date",
            "bio",
            "profile_picture",
            "created_at",
            "followers",
            "following",
        )


class ProfileRetrieveSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "gender",
            "birth_date",
            "bio",
            "profile_picture",
            "created_at",
            "followers",
            "following",
        )

    def get_followers(self, obj):
        followers = obj.following.all()
        return RelationFollowersSerializer(followers, many=True).data

    def get_following(self, obj):
        following = obj.followers.all()
        return RelationFollowingSerializer(following, many=True).data


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "profile_picture")


class PostMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostMedia
        fields = ("id", "post", "media")


class PostSerializer(serializers.ModelSerializer):
    media_files = PostMediaSerializer(many=True, read_only=True)
    time_posting = serializers.DateTimeField(required=False)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "hashtags",
            "created_at",
            "media_files",
            "time_posting",
        )

    def create(self, validated_data):
        owner = self.context["request"].user.profile
        title = validated_data.pop("title")
        content = validated_data.pop("content")
        time_posting = validated_data.pop("time_posting")
        if time_posting:
            #  create but no save post hasta time_posting

            #  created_at  = time_posting
            if time_posting > datetime.now():
                created_at = time_posting
            #  planing post in time_posting, create Celery task for save post
            #  create but no save post hasta time_posting

        post = Post.objects.create(
            owner=owner, title=title, content=content, created_at=created_at
        )
        return post


class PostListSerializer(serializers.ModelSerializer):
    is_liked = serializers.IntegerField(read_only=True)
    is_unliked = serializers.IntegerField(read_only=True)
    nums_of_comments = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "owner",
            "title",
            "content",
            "hashtags",
            "created_at",
            "media_files",
            "nums_of_comments",
            "is_liked",
            "is_unliked",
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class CommentAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "owner",
            "post",
            "content",
        )
        read_only_fields = (
            "owner",
            "post",
        )

    def create(self, validated_data):
        validated_data["post"] = self.context["post"]
        validated_data["owner"] = self.context["request"].user.profile
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"


class LikeDislikeAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = (
            "id",
            "owner",
            "post",
            "is_liked",
            "is_unliked",
        )
        read_only_fields = (
            "owner",
            "post",
        )

    def create(self, validated_data):
        validated_data["post"] = self.context["post"]
        validated_data["owner"] = self.context["request"].user.profile
        return super().create(validated_data)


class PostRetrieveSerializer(serializers.ModelSerializer):
    media_files = PostMediaSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "owner",
            "title",
            "content",
            "hashtags",
            "created_at",
            "media_files",
            "comments",
            "likes",
        )

    def get_likes(self, obj):
        likes = obj.likes.order_by("-is_liked", "is_unliked")
        return LikeSerializer(likes, many=True).data
