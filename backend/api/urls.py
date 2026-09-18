from django.urls import path
from rest_framework.routers import SimpleRouter

from .operations_views import (
    AlertViewSet,
    DashboardSummaryView,
    EngineerViewSet,
    IncidentViewSet,
)
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
router.register("alerts", AlertViewSet, basename="alert")
router.register("incidents", IncidentViewSet, basename="incident")
router.register("engineers", EngineerViewSet, basename="engineer")

urlpatterns = [
    path("health/", health, name="health"),
    path(
        "dashboard/summary/",
        DashboardSummaryView.as_view(),
        name="dashboard-summary",
    ),
]

urlpatterns += router.urls