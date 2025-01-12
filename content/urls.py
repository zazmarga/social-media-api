from django.urls import path, include
from rest_framework import routers

from content.views import (
    ProfileViewSet,
    PostViewSet,
    RelationFollowingViewSet,
    RelationFollowersViewSet,
)


router = routers.DefaultRouter()


router.register("profiles", ProfileViewSet)
router.register("following", RelationFollowingViewSet, basename="following")
router.register("followers", RelationFollowersViewSet, basename="followers")


router.register("posts", PostViewSet)

app_name = "content"


urlpatterns = [
    path("", include(router.urls)),
    # path("my_profile/", my_profile, name="my_profile"),  #  111111111
    # path("my_profile/", MyProfileView.as_view(), name="my_profile-detail"),   #  222222
]
