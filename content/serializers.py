from django.db.models import CharField
from rest_framework import serializers

from content.models import Profile, Post, Relation
from django.contrib.auth import get_user_model


User = get_user_model()


# class RelationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Relation
#         fields = ("id", "follower", "following")
#


class RelationFollowersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Relation
        fields = (
            "id",
            "follower",
        )


class RelationFollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relation
        fields = (
            "id",
            "following",
        )


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = (
            "id",
            "nickname",
            "first_name",
            "last_name",
            "gender",
            "birth_date",
            "bio",
            "profile_picture",
            "created_at",
        )


class ProfileListSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "id",
            "nickname",
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
        followers = obj.followers.all()
        return RelationFollowersSerializer(followers, many=True).data

    def get_following(self, obj):
        following = obj.following.all()
        return RelationFollowingSerializer(following, many=True).data


class ProfileRetrieveSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "id",
            "nickname",
            "first_name",
            "last_name",
            "gender",
            "birth_date",
            "bio",
            "created_at",
            "followers",
            "following",
        )

    def get_followers(self, obj):
        followers = obj.followers.all()
        return RelationFollowersSerializer(followers, many=True).data

    def get_following(self, obj):
        following = obj.following.all()
        return RelationFollowingSerializer(following, many=True).data


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("id", "profile_picture")


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "owner",
            "title",
            "content",
            "hashtags",
            "created_at",
            "comments",
            "is_liked",
            "is_unliked",
        )


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "owner",
            "title",
            "content",
            "hashtags",
            "created_at",
            "post_media",
            "nums_of_comments",
            "is_liked",
            "is_unliked",
        )


class PostRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "owner",
            "title",
            "content",
            "hashtags",
            "created_at",
            "post_media",
            "comments",
            "likes",
            "is_liked",
            "is_unliked",
        )


class PostMediaSerializer(PostRetrieveSerializer):
    owner = serializers.ReadOnlyField(source="profile.nickname")
    title = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "owner", "title", "post_media")


# class LikeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Like
#         fields = "__all__"
#
#     def validate(self, data):
#         if data.get('is_liked') and data.get('is_unliked'):
#             raise serializers.ValidationError("is_liked and is_unliked cannot both be True at the same time.")
#         return data
