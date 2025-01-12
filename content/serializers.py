from rest_framework import serializers

from content.models import Profile, Post, Relation
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
    # followers = serializers.SerializerMethodField()
    # following = serializers.SerializerMethodField()
    # followers = serializers.PrimaryKeyRelatedField(
    #     many=True, read_only=True, source="followers.all"
    # )
    # following = serializers.PrimaryKeyRelatedField(
    #     many=True, read_only=True, source="following.all"
    # )

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

    # def get_followers(self, obj):
    #     followers = obj.following.all()
    #     return RelationFollowersSerializer(followers, many=True).data
    #
    # def get_following(self, obj):
    #     following = obj.followers.all()
    #     return RelationFollowingSerializer(following, many=True).data


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
