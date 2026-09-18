from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import DeviceViewSet, SiteViewSet, health


router = SimpleRouter()
router.register("sites", SiteViewSet, basename="site")
router.register("devices", DeviceViewSet, basename="device")

urlpatterns = [
    path("health/", health, name="health"),
]

urlpatterns += router.urls