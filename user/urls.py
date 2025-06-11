# users/urls.py
from django.urls import path

from .views import LoginView, RegisterUserView, UserProfileView

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", UserProfileView.as_view(), name="user-profile"),
]
