# Generated by Django 5.1.4 on 2025-01-14 19:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("content", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="post",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="posts",
                to="content.profile",
            ),
        ),
        migrations.AddField(
            model_name="like",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="likes",
                to="content.profile",
            ),
        ),
        migrations.AddField(
            model_name="comment",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="content.profile",
            ),
        ),
        migrations.AddField(
            model_name="relation",
            name="follower",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="followers",
                to="content.profile",
            ),
        ),
        migrations.AddField(
            model_name="relation",
            name="following",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="following",
                to="content.profile",
            ),
        ),
        migrations.AddIndex(
            model_name="profile",
            index=models.Index(
                fields=["first_name", "last_name"],
                name="content_pro_first_n_2bf436_idx",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="like",
            unique_together={("owner", "post")},
        ),
        migrations.AlterUniqueTogether(
            name="relation",
            unique_together={("follower", "following")},
        ),
    ]
