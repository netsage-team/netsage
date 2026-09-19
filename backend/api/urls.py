from django.urls import path

from .delivery_views import sms_delivery_report
from rest_framework.routers import SimpleRouter
from .incoming_views import incoming_sms_webhook

from .notification_views import (
    IncidentNotificationApproveView,
    IncidentNotificationAudienceView,
    IncidentNotificationDraftView,
    IncidentNotificationHistoryView,
    IncidentNotificationSendView,
)

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
        "sms/delivery-report/",
        sms_delivery_report,
        name="sms-delivery-report",
    ),
    path(
    "sms/incoming/",
    incoming_sms_webhook,
    name="incoming-sms-webhook",
    ),
    path(
        "incidents/<int:incident_id>/notification-audience/",
        IncidentNotificationAudienceView.as_view(),
        name="notification-audience",
    ),
    path(
        "incidents/<int:incident_id>/notification-draft/",
        IncidentNotificationDraftView.as_view(),
        name="notification-draft",
    ),
    path(
        "incidents/<int:incident_id>/notification-approve/",
        IncidentNotificationApproveView.as_view(),
        name="notification-approve",
    ),
    path(
        "incidents/<int:incident_id>/notification-send/",
        IncidentNotificationSendView.as_view(),
        name="notification-send",
    ),
    path(
        "incidents/<int:incident_id>/notification-history/",
        IncidentNotificationHistoryView.as_view(),
        name="notification-history",
    ),
    path(
        "dashboard/summary/",
        DashboardSummaryView.as_view(),
        name="dashboard-summary",
    ),
]

urlpatterns += router.urls