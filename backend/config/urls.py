from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("api/auth/", include("api.auth_urls")),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path(
        "api-auth/",
        include("rest_framework.urls", namespace="rest_framework"),
    ),
]
