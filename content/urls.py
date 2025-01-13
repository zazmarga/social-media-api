from django.urls import path, include
from rest_framework import routers

from content.views import (
    ProfileViewSet,
    PostViewSet,
    RelationFollowingViewSet,
    RelationFollowersViewSet,
    CommentViewSet,
)


router = routers.DefaultRouter()


router.register("profiles", ProfileViewSet)
router.register("following", RelationFollowingViewSet, basename="following")
router.register("followers", RelationFollowersViewSet, basename="followers")


router.register("posts", PostViewSet)
router.register("comments", CommentViewSet)

app_name = "content"


urlpatterns = [
    path("", include(router.urls)),
]
