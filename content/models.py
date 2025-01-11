import pathlib
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.text import slugify
from rest_framework.exceptions import ValidationError


def media_file_path(instance: "Profile", filename: str, catalog: str) -> pathlib.Path:
    filename = f"{slugify(instance.id)}-{uuid.uuid4()}" + pathlib.Path(filename).suffix
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
    nickname = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=48)
    last_name = models.CharField(max_length=48)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    profile_picture = models.ImageField(
        null=True, blank=True, upload_to=profile_picture_file_path
    )
    created_at = models.DateTimeField(auto_now_add=True)
    # relations = models.ManyToManyField("Profile", through="Relation", blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "first_name",
                    "last_name",
                ]
            ),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Relation(models.Model):
    follower = models.ForeignKey(
        Profile, related_name="followers", on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        Profile, related_name="following", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.follower} {self.following}"


class Post(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    hashtags = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    post_media = models.ForeignKey(
        "PostMedia", on_delete=models.CASCADE, related_name="post_medias", blank=True
    )
    comments = models.ManyToManyField("Comment", blank=True, related_name="posts")
    likes = models.ManyToManyField("Like", blank=True, related_name="posts")

    @property
    def is_liked(self):
        return self.likes.filter(is_liked=True).count()

    @property
    def is_unliked(self):
        return self.likes.filter(is_liked=False).count()

    @property
    def nums_of_comments(self):
        return self.comments.count()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.owner}: {self.title}"


class PostMedia(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="media_files")
    media = models.FileField(upload_to=post_media_file_path, blank=True, null=True)

    def __str__(self):
        return f"Post: {self.post} , media file number: {str(self.id)}"


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_comments"
    )
    owner = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.owner} - {self.content}"


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="likes")
    is_liked = models.BooleanField(default=False)
    is_unliked = models.BooleanField(default=False)

    class Meta:
        unique_together = (("owner", "post"),)

    def __str__(self):
        return f"{self.owner} - {self.post}"

    def clean(self):
        if self.is_liked and self.is_unliked:
            raise ValidationError(
                "is_liked and is_unliked cannot both be True at the same time."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
