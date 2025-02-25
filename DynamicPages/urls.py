from django.urls import path
from .views import (
    DynamicPageDetailView,
    DynamicPageListView,
    HappyCustomerListCreateView,
    HappyCustomerRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("DynamicPages/", DynamicPageListView.as_view(), name="dynamic-page-list"),
    path(
        "DynamicPages/<slug:slug>/",
        DynamicPageDetailView.as_view(),
        name="dynamic-page-detail",
    ),
    path(
        "happycustomer/",
        HappyCustomerListCreateView.as_view(),
        name="dynamic-page-list",
    ),
    path(
        "happycustomer/<int:pk>/",
        HappyCustomerRetrieveUpdateDestroyView.as_view(),
        name="dynamic-page-detail",
    ),
]
