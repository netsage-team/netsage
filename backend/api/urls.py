from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import (
    DeviceViewSet,
    SiteViewSet,
    TelemetryReadingViewSet,
    health,
)


router = SimpleRouter()
router.register("sites", SiteViewSet, basename="site")
router.register("devices", DeviceViewSet, basename="device")
router.register(
    "telemetry",
    TelemetryReadingViewSet,
    basename="telemetry",
)

urlpatterns = [
    path("health/", health, name="health"),
]

urlpatterns += router.urls