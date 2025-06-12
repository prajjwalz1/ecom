# users/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, RegisterUserView

router = DefaultRouter()
router.register(r"users", CustomUserViewSet, basename="customuser")


urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("", include(router.urls)),
]
