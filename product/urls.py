from django.contrib import admin
from django.urls import path,include
from .views import *
from . import views

urlpatterns = [

    path('homepage',HomeView.as_view()),
    path('details',ProductDetailView.as_view()),
    path('brands',BrandView.as_view()),
    path('category-wise-product',CategoryWiseProduct.as_view()),
    path('search-product',SearchProduct.as_view()),
    path('productreview',ProductReviewView.as_view()),
    path('brandwiseproduct',BrandWiseProducts.as_view()),
    path('productaction',ProductCRUD.as_view()),
    path('get-category-brands-tags',ProductDependencies.as_view()),
    path('get-category-based-specification',CategorySpecificationsView.as_view()),
    

    path('brand/', views.BrandListCreateView.as_view(), name='brand-list-create'),
    path('brand/<int:pk>/', views.BrandRetrieveUpdateDestroyView.as_view(), name='brand-retrieve-update-destroy'),

    # Tag API Endpoints
    path('tags/', views.TagListCreateView.as_view(), name='tag-list-create'),
    path('tags/<int:pk>/', views.TagRetrieveUpdateDestroyView.as_view(), name='tag-retrieve-update-destroy'),

    # Category API Endpoints
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.CategoryRetrieveUpdateDestroyView.as_view(), name='category-retrieve-update-destroy'),

    # Specification API Endpoints
    path('specifications/', views.SpecificationListCreateView.as_view(), name='specification-list-create'),
    path('specifications/<int:pk>/', views.SpecificationRetrieveUpdateDestroyView.as_view(), name='specification-retrieve-update-destroy'),

    # CarouselImage API Endpoints
    path('carousel-images/', views.CarouselImageListCreateView.as_view(), name='carousel-image-list-create'),
    path('carousel-images/<int:pk>/', views.CarouselImageRetrieveUpdateDestroyView.as_view(), name='carousel-image-retrieve-update-destroy'),

    # Navbar API Endpoints
    path('navbars/', views.NavbarListCreateView.as_view(), name='navbar-list-create'),
    path('navbars/<int:pk>/', views.NavbarRetrieveUpdateDestroyView.as_view(), name='navbar-retrieve-update-destroy'),

    
    path('products/', views.ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', views.ProductRetrieveUpdateDestroyView.as_view(), name='product-retrieve-update-destroy'),


    path('productimage/', views.ProductImageCreateView.as_view(), name='productimage-list-create'),
    path('productimage/<int:pk>/', views.ProductImageUpdateDestroyView.as_view(), name='productimage-update-destroy'),


]
