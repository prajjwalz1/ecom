# urls.py
from django.urls import path
from .views import CustomTokenObtainView,CustomTokenRefreshView
urlpatterns = [
    path('api/login/', CustomTokenObtainView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]