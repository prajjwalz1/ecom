from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [

    path('homepage',HomeView.as_view())

]
