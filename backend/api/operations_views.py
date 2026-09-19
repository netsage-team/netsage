from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from rest_framework.authentication import SessionAuthentication
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import (
    Alert,
    CustomerNetworkReport,
    Device,
    Incident,
    IncidentEvent,
    Site,
)
from .services.recovery import evaluate_incident_recovery
from .operations_serializers import (
    AlertFilterSerializer,
    AlertSerializer,
    EngineerSerializer,
    IncidentEventSerializer,
    IncidentFilterSerializer,
    IncidentNoteSerializer,
    IncidentResolutionSerializer,
    IncidentSerializer,
    IncidentUpdateSerializer,
    SiteFilterSerializer,
    CustomerReportSerializer,
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
            .prefetch_related(
                "affected_sites",
                "timeline__actor",
            )
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
            incident = self.get_queryset().select_for_update(
                of=("self",)
            ).get(pk=self.get_object().pk)

            previous_assignee = incident.assigned_to_id
            previous_status = incident.status

            serializer = IncidentUpdateSerializer(
                incident,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            if incident.assigned_to_id != previous_assignee:
                if incident.assigned_to:
                    message = (
                        f"Incident assigned to "
                        f"{incident.assigned_to.username}."
                    )
                else:
                    message = "Engineer assignment cleared."

                IncidentEvent.objects.create(
                    incident=incident,
                    event_type=IncidentEvent.EventType.ASSIGNMENT,
                    message=message,
                    actor=request.user,
                )

            if incident.status != previous_status:
                IncidentEvent.objects.create(
                    incident=incident,
                    event_type=IncidentEvent.EventType.STATUS,
                    message=(
                        f"Incident status changed from "
                        f"{previous_status} to {incident.status}."
                    ),
                    actor=request.user,
                )

            incident = self.get_queryset().get(pk=incident.pk)

            return Response(
                IncidentSerializer(incident).data
            )

    @action(
        detail=True,
        methods=["post"],
        url_path="notes",
    )
    def notes(self, request, pk=None):
        serializer = IncidentNoteSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            incident = self.get_queryset().select_for_update(
                of=("self",)
            ).get(pk=self.get_object().pk)

            event = IncidentEvent.objects.create(
                incident=incident,
                event_type=IncidentEvent.EventType.NOTE,
                message=serializer.validated_data["note"],
                actor=request.user,
            )

        return Response(
            IncidentEventSerializer(event).data,
            status=status.HTTP_201_CREATED,
        )


    @action(
        detail=True,
        methods=["post"],
        url_path="verify-recovery",
    )
    def verify_recovery(self, request, pk=None):
        with transaction.atomic():
            incident = self.get_queryset().select_for_update(
                of=("self",)
            ).get(pk=self.get_object().pk)

            if incident.status != Incident.Status.INVESTIGATING:
                return Response(
                    {
                        "detail": (
                            "Recovery can only be verified while "
                            "an incident is being investigated."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if incident.assigned_to_id is None:
                return Response(
                    {
                        "detail": (
                            "Assign an engineer before verifying "
                            "recovery."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            recovery = evaluate_incident_recovery(
                incident
            )

            if not recovery["recovered"]:
                return Response(
                    {
                        "detail": (
                            "Sustained recovery has not yet been "
                            "verified across every affected site."
                        ),
                        "recovery": recovery,
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            verified_at = timezone.now()

            incident.status = Incident.Status.MONITORING
            incident.recovery_verified_at = verified_at
            incident.save(
                update_fields=[
                    "status",
                    "recovery_verified_at",
                    "updated_at",
                ]
            )

            site_names = ", ".join(
                result["site_name"]
                for result in recovery["sites"]
            )

            IncidentEvent.objects.create(
                incident=incident,
                event_type=IncidentEvent.EventType.RECOVERY,
                message=(
                    "Sustained healthy telemetry verified across "
                    f"{site_names}. Incident moved to monitoring."
                ),
                actor=request.user,
            )

            incident = self.get_queryset().get(
                pk=incident.pk
            )

            return Response({
                "incident": IncidentSerializer(
                    incident
                ).data,
                "recovery": recovery,
            })

    @action(
        detail=True,
        methods=["post"],
        url_path="resolve",
    )
    def resolve_incident(self, request, pk=None):
        serializer = IncidentResolutionSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            incident = self.get_queryset().select_for_update(
                of=("self",)
            ).get(pk=self.get_object().pk)

            if incident.status != Incident.Status.MONITORING:
                return Response(
                    {
                        "detail": (
                            "Only an incident in recovery "
                            "monitoring can be resolved."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if incident.assigned_to_id is None:
                return Response(
                    {
                        "detail": (
                            "The incident must have an assigned "
                            "engineer before resolution."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if (
                incident.assigned_to_id != request.user.id
                and not request.user.is_superuser
            ):
                return Response(
                    {
                        "detail": (
                            "Only the assigned engineer can "
                            "resolve this incident."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            resolved_at = timezone.now()

            incident.status = Incident.Status.RESOLVED
            incident.resolved_at = resolved_at
            incident.resolution_notes = (
                serializer.validated_data[
                    "resolution_notes"
                ]
            )
            incident.save(
                update_fields=[
                    "status",
                    "resolved_at",
                    "resolution_notes",
                    "updated_at",
                ]
            )

            cleared_count = incident.alerts.filter(
                cleared_at__isnull=True,
            ).update(
                cleared_at=resolved_at,
            )

            IncidentEvent.objects.create(
                incident=incident,
                event_type=IncidentEvent.EventType.RESOLVED,
                message=(
                    "Incident resolved after sustained recovery "
                    f"verification. {cleared_count} related "
                    "alert(s) cleared."
                ),
                actor=request.user,
            )

            incident = self.get_queryset().get(
                pk=incident.pk
            )

            return Response({
                "incident": IncidentSerializer(
                    incident
                ).data,
                "alerts_cleared": cleared_count,
            })


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

class CustomerReportViewSet(StaffReadOnlyViewSet):
    queryset = (
        CustomerNetworkReport.objects
        .select_related(
            "customer",
            "site",
            "incident",
        )
        .order_by("-created_at", "-id")
    )
    serializer_class = CustomerReportSerializer