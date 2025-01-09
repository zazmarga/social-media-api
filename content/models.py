import pathlib
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify


def media_file_path(instance: "Profile", filename: str, catalog: str) -> pathlib.Path:
    filename = (
        f"{slugify(instance.id)}-{instance.nickname}-{uuid.uuid4()}"
        + pathlib.Path(filename).suffix
    )
    return pathlib.Path(f"upload/{catalog}/") / pathlib.Path(filename)


def profile_picture_file_path(instance, filename):
    return media_file_path(instance, filename, "profile_pictures")


def post_media_file_path(instance, filename):
    return media_file_path(instance, filename, "posts_media")


class Profile(models.Model):
    GENDER_CHOICES = (
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    )
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    nickname = models.CharField(max_length=48)
    profile_status = models.CharField(null=True, blank=True, max_length=255)
    profile_picture = models.ImageField(null=True, upload_to=profile_picture_file_path)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    bio = models.TextField(null=True, blank=True)
    followers = models.ManyToManyField(
        get_user_model(), related_name="followers_profiles", blank=True
    )
    followings = models.ManyToManyField(
        get_user_model(), related_name="followings_profiles", blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "user",
                ]
            ),
        ]

    def __str__(self):
        return self.nickname


class Post(models.Model):
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    hashtags = models.CharField(max_length=255, blank=True)
    post_media = models.ForeignKey(
        "PostMedia", on_delete=models.CASCADE, related_name="post_media", null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    comments = models.ManyToManyField("Comment", blank=True, related_name="posts")
    likes = models.ManyToManyField("Like", blank=True, related_name="posts")

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class PostMedia(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media_files")
    media = models.FileField(upload_to=post_media_file_path)

    def __str__(self):
        return self.id


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_comments"
    )
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user} - {self.content}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="likes"
    )

    class Meta:
        unique_together = (("user", "post"),)

    def __str__(self):
        return f"{self.user} - {self.post}"
