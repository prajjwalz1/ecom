from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [

    path('homepage',HomeView.as_view()),
    path('details',ProductDetailView.as_view()),
    path('brands',BrandView.as_view()),
    path('category-wise-product',CategoryWiseProduct.as_view()),
    path('search-product',SearchProduct.as_view()),
    path('productreview',ProductReviewView.as_view()),
    path('brandwiseproduct',BrandWiseProducts.as_view()),

    



]
