from rest_framework import serializers

from content.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "id",
            "user",
            "nickname",
            "profile_picture",
            "profile_picture",
            "birth_date",
            "gender",
            "bio",
            "followers",
            "followings",
            "created_at",
        )
