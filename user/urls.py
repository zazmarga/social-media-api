from django.urls import path

from user.views import CreateUserView, LoginUserView, ManageUserView, LogoutView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", LoginUserView.as_view(), name="token"),
    path("me/", ManageUserView.as_view(), name="manage-user"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

app_name = "user"
