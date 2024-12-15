from django.urls import path
from .views import DynamicPageDetailView, DynamicPageListView

urlpatterns = [
    path('DynamicPages/', DynamicPageListView.as_view(), name='dynamic-page-list'),
    path('DynamicPages/<slug:slug>/', DynamicPageDetailView.as_view(), name='dynamic-page-detail'),
]
