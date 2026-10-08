from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView


urlpatterns = [
    path("api/auth/", include("api.auth_urls")),
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path(
        "api-auth/",
        include("rest_framework.urls", namespace="rest_framework"),
    ),

    # Serve the React application while keeping API and admin routes in Django.
    path("", TemplateView.as_view(template_name="index.html"), name="frontend"),
    re_path(
        r"^operations(?:/.*)?$",
        TemplateView.as_view(template_name="index.html"),
        name="frontend-operations",
    ),
]
