"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.server_health_status),
    path("api/users/", include("user.urls")),
    path("admin/", admin.site.urls),
    path("product/", include("product.urls")),
    path(
        "ckeditor/", include("ckeditor_uploader.urls")
    ),  # If you plan to use file uploads
    path("order/", include("Order.urls")),
    path("auth/", include("authentication.urls")),
    path("api/emi/", include("EmiService.urls")),
    path("api/pages/", include("DynamicPages.urls")),
    path("localgov/", include("palikadata.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
