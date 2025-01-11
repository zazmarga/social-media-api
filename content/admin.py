from django.contrib import admin

from content.models import Profile, Post, PostMedia, Comment, Like, Relation


class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1


@admin.register(Post)
class OrderAdmin(admin.ModelAdmin):
    inlines = (PostMediaInline,)


admin.site.register(Profile)
# admin.site.register(Post)
admin.site.register(PostMedia)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Relation)
