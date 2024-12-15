from django.urls import path, include
from .views import *
from . import views
urlpatterns = [
    path('calculate-emi/',  views.calculate_emi, name='calculate-emi'),
    path('emi-configs/', EMIConfigListCreateView.as_view(), name='emi-config-list-create'),
    path('emi-configs/<int:pk>/', EMIConfigDetailView.as_view(), name='emi-config-detail'),
    path('loan-types/', LoanTypeListCreateView.as_view(), name='loan-type-list-create'),
    path('loan-types/<int:pk>/', LoanTypeDetailView.as_view(), name='loan-type-detail'),
]
