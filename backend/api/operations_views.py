from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Alert, Device, Incident, Site
from .operations_serializers import (
    AlertFilterSerializer,
    AlertSerializer,
    EngineerSerializer,
    IncidentFilterSerializer,
    IncidentSerializer,
    IncidentUpdateSerializer,
    SiteFilterSerializer,
)
from .views import StandardPagination


User = get_user_model()


def validated_filters(serializer_class, request):
    serializer = serializer_class(data=request.query_params)
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data


class StaffReadOnlyViewSet(ReadOnlyModelViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
    pagination_class = StandardPagination


class EngineerViewSet(StaffReadOnlyViewSet):
    serializer_class = EngineerSerializer
    queryset = User.objects.filter(
        is_active=True,
        is_staff=True,
    ).order_by("username", "id")


class IncidentViewSet(StaffReadOnlyViewSet):
    serializer_class = IncidentSerializer

    def get_queryset(self):
        filters = validated_filters(IncidentFilterSerializer, self.request)
        queryset = (
            Incident.objects.select_related(
                "site", "assigned_to",
            )
            .prefetch_related("affected_sites")
            .order_by("-opened_at", "-id")
        )

        if "site" in filters:
            site_id = filters["site"]
            queryset = queryset.filter(
                Q(site_id=site_id)
                | Q(affected_sites__id=site_id)
            ).distinct()

        mapping = {
            "status": "status",
            "severity": "severity",
            "assigned_to": "assigned_to_id",
        }

        for parameter, field in mapping.items():
            if parameter in filters:
                queryset = queryset.filter(**{field: filters[parameter]})

        return queryset

    @action(detail=True, methods=["patch"])
    def manage(self, request, pk=None):
        with transaction.atomic():
            # Lock during updates on databases supporting row locks.
            incident = self.get_queryset().select_for_update(
                of=("self",)
            ).get(pk=self.get_object().pk)

            serializer = IncidentUpdateSerializer(
                incident,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(IncidentSerializer(incident).data)


class AlertViewSet(StaffReadOnlyViewSet):
    serializer_class = AlertSerializer

    def get_queryset(self):
        filters = validated_filters(AlertFilterSerializer, self.request)
        queryset = Alert.objects.select_related(
            "device",
        ).order_by("-detected_at", "-id")

        mapping = {
            "site": "device__site_id",
            "device": "device_id",
            "incident": "incident_id",
            "severity": "severity",
        }

        for parameter, field in mapping.items():
            if parameter in filters:
                queryset = queryset.filter(**{field: filters[parameter]})

        if "cleared" in filters:
            queryset = queryset.filter(
                cleared_at__isnull=not filters["cleared"],
            )

        return queryset


class DashboardSummaryView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        filters = validated_filters(SiteFilterSerializer, request)

        sites = Site.objects.all()
        devices = Device.objects.all()
        incidents = Incident.objects.all()
        alerts = Alert.objects.all()

        if "site" in filters:
            site_id = filters["site"]
            sites = sites.filter(pk=site_id)
            devices = devices.filter(site_id=site_id)
            incidents = incidents.filter(
                Q(site_id=site_id)
                | Q(affected_sites__id=site_id)
            ).distinct()
            alerts = alerts.filter(device__site_id=site_id)

        status_counts = {
            value: 0 for value in Incident.Status.values
        }
        for row in incidents.values("status").annotate(total=Count("id")):
            status_counts[row["status"]] = row["total"]

        active_incidents = incidents.exclude(
            status=Incident.Status.RESOLVED,
        )
        active_alerts = alerts.filter(cleared_at__isnull=True)

        return Response({
            "generated_at": timezone.now(),
            "site": filters.get("site"),
            "sites_total": sites.count(),
            "sites_active": sites.filter(is_active=True).count(),
            "devices_total": devices.count(),
            "devices_active": devices.filter(is_active=True).count(),
            "incidents_active": active_incidents.count(),
            "incidents_unassigned": active_incidents.filter(
                assigned_to__isnull=True,
            ).count(),
            "incidents_by_status": status_counts,
            "alerts_active": active_alerts.count(),
            "alerts_critical": active_alerts.filter(
                severity="critical",
            ).count(),
        })