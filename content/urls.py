from django.urls import path, include
from rest_framework import routers

from content.views import ProfileViewSet

router = routers.DefaultRouter()

router.register("profiles", ProfileViewSet)
#    profile_picture its part of Profile, so no need register


app_name = "content"


urlpatterns = [
    path("", include(router.urls)),
]
