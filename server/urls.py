"""Root URL configuration for the Cars Dealership project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("djangoapp/", include("server.djangoapp.urls")),
    path("", include("server.djangoapp.page_urls")),
]
