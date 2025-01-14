from django.contrib import admin

from content.models import Profile, Post, PostMedia, Comment, Like, Relation


admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(PostMedia)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Relation)
