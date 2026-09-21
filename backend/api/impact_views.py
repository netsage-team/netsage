from collections import Counter

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response

from .models import (
    Customer,
    CustomerNetworkReport,
    Incident,
    IncidentEvent,
    Notification,
    Site,
)
from .notification_views import StaffAPIView


class EscalationSerializer(serializers.Serializer):
    escalation_level = serializers.ChoiceField(
        choices=Incident.EscalationLevel.choices,
        required=False,
    )

    escalation_status = serializers.ChoiceField(
        choices=Incident.EscalationStatus.choices,
        required=False,
    )

    escalation_team = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
    )

    automatic = serializers.BooleanField(
        required=False,
        default=False,
    )


def affected_sites_for(incident):
    """
    Return every site affected by the incident.

    The primary incident site is always included even if
    it is not explicitly present in affected_sites.
    """

    site_ids = set(
        incident.affected_sites.values_list(
            "id",
            flat=True,
        )
    )

    site_ids.add(
        incident.site_id
    )

    return list(
        Site.objects.filter(
            id__in=site_ids,
        ).order_by("name")
    )


def calculate_recommended_escalation(
    incident,
    affected_site_count,
    potentially_affected_customers,
    customer_report_count,
):
    """
    Determine an explainable maintenance escalation level.

    This is a prototype operational rule engine.

    Production thresholds should be calibrated with the ISP.
    """

    score = 0
    reasons = []

    if incident.severity == "critical":
        score += 3
        reasons.append(
            "Incident severity is critical."
        )
    else:
        score += 1

    if affected_site_count >= 3:
        score += 3
        reasons.append(
            "Three or more network sites are affected."
        )
    elif affected_site_count >= 2:
        score += 2
        reasons.append(
            "Multiple network sites are affected."
        )
    elif affected_site_count == 1:
        score += 1

    if potentially_affected_customers >= 100:
        score += 3
        reasons.append(
            "At least 100 customers may be affected."
        )
    elif potentially_affected_customers >= 25:
        score += 2
        reasons.append(
            "Customer impact is significant."
        )
    elif potentially_affected_customers > 0:
        score += 1

    if customer_report_count >= 10:
        score += 2
        reasons.append(
            "A high number of customer reports has been received."
        )
    elif customer_report_count > 0:
        score += 1
        reasons.append(
            "Customers are reporting service problems."
        )

    if score >= 8:
        level = Incident.EscalationLevel.LEVEL_3

        status = (
            Incident.EscalationStatus.ESCALATED
        )

        team = (
            "Senior Network Operations "
            "and Field Maintenance"
        )

        response = (
            "Immediate senior technical response required. "
            "Dispatch field maintenance and begin "
            "parallel network investigation."
        )

    elif score >= 5:
        level = Incident.EscalationLevel.LEVEL_2

        status = (
            Incident.EscalationStatus.ESCALATED
        )

        team = (
            "Regional Network Operations "
            "and Maintenance"
        )

        response = (
            "Escalate to regional maintenance. "
            "Begin investigation and prepare technician "
            "dispatch if remote recovery is unsuccessful."
        )

    elif score >= 2:
        level = Incident.EscalationLevel.LEVEL_1

        status = (
            Incident.EscalationStatus.ESCALATED
        )

        team = "Network Operations Centre"

        response = (
            "NOC investigation required. "
            "Continue enhanced monitoring before "
            "dispatching field maintenance."
        )

    else:
        level = Incident.EscalationLevel.NONE

        status = (
            Incident.EscalationStatus.NOT_ESCALATED
        )

        team = ""

        response = (
            "Continue automated monitoring."
        )

    if not reasons:
        reasons.append(
            "Current impact does not require escalation."
        )

    return {
        "score": score,
        "level": level,
        "level_label": dict(
            Incident.EscalationLevel.choices
        ).get(
            level,
            level,
        ),
        "status": status,
        "status_label": dict(
            Incident.EscalationStatus.choices
        ).get(
            status,
            status,
        ),
        "team": team,
        "reasons": reasons,
        "recommended_response": response,
    }


def build_incident_impact(incident):
    """
    Build one complete operational-impact view for an incident.
    """

    sites = affected_sites_for(
        incident
    )

    site_ids = [
        site.id
        for site in sites
    ]

    active_customers = (
        Customer.objects.filter(
            site_id__in=site_ids,
            is_active=True,
        )
    )

    sms_eligible_customers = (
        active_customers.filter(
            sms_opt_in=True,
        )
    )

    reports = (
        CustomerNetworkReport.objects.filter(
            incident=incident,
        )
    )

    notifications = (
        Notification.objects.filter(
            incident=incident,
        )
    )

    delivery_counts = Counter(
        notifications.values_list(
            "delivery_status",
            flat=True,
        )
    )

    affected_areas = sorted(
        {
            site.location
            for site in sites
            if site.location
        }
    )

    site_breakdown = []

    for site in sites:
        site_customers = (
            active_customers.filter(
                site=site,
            )
        )

        site_sms_customers = (
            site_customers.filter(
                sms_opt_in=True,
            )
        )

        site_reports = (
            reports.filter(
                site=site,
            )
        )

        site_breakdown.append(
            {
                "site_id": site.id,
                "site_name": site.name,
                "site_type": site.site_type,
                "site_type_label": (
                    site.get_site_type_display()
                ),
                "location": site.location,

                "potentially_affected_customers": (
                    site_customers.count()
                ),

                "sms_eligible_customers": (
                    site_sms_customers.count()
                ),

                "customer_reports": (
                    site_reports.count()
                ),
            }
        )

    reporting_customers = (
        reports.exclude(
            customer__isnull=True,
        )
        .values(
            "customer_id",
        )
        .distinct()
        .count()
    )

    recommended_escalation = (
        calculate_recommended_escalation(
            incident=incident,

            affected_site_count=len(
                sites
            ),

            potentially_affected_customers=(
                active_customers.count()
            ),

            customer_report_count=(
                reports.count()
            ),
        )
    )

    assigned_engineer = None

    if incident.assigned_to:
        assigned_engineer = (
            incident.assigned_to.get_full_name()
            or incident.assigned_to.username
        )

    return {
        "incident": incident.id,
        "title": incident.title,
        "severity": incident.severity,
        "status": incident.status,

        "network_impact": {
            "affected_site_count": len(
                sites
            ),

            "affected_area_count": len(
                affected_areas
            ),

            "affected_areas": (
                affected_areas
            ),

            "potentially_affected_customers": (
                active_customers.count()
            ),

            "sms_eligible_customers": (
                sms_eligible_customers.count()
            ),

            "customer_reports_received": (
                reports.count()
            ),

            "reporting_customers": (
                reporting_customers
            ),
        },

        "site_breakdown": (
            site_breakdown
        ),

        "maintenance": {
            "escalation_level": (
                incident.escalation_level
            ),

            "escalation_level_label": (
                incident.get_escalation_level_display()
            ),

            "escalation_status": (
                incident.escalation_status
            ),

            "escalation_status_label": (
                incident.get_escalation_status_display()
            ),

            "escalation_team": (
                incident.escalation_team
            ),

            "escalated_at": (
                incident.escalated_at
            ),

            "assigned_engineer": (
                assigned_engineer
            ),
        },

        "recommended_escalation": (
            recommended_escalation
        ),

        "communication": {
            "notification_records": (
                notifications.count()
            ),

            "not_sent": (
                delivery_counts.get(
                    Notification.DeliveryStatus.NOT_SENT,
                    0,
                )
            ),

            "dry_run": (
                delivery_counts.get(
                    Notification.DeliveryStatus.DRY_RUN,
                    0,
                )
            ),

            "queued": (
                delivery_counts.get(
                    Notification.DeliveryStatus.QUEUED,
                    0,
                )
            ),

            "sent": (
                delivery_counts.get(
                    Notification.DeliveryStatus.SENT,
                    0,
                )
            ),

            "delivered": (
                delivery_counts.get(
                    Notification.DeliveryStatus.DELIVERED,
                    0,
                )
            ),

            "failed": (
                delivery_counts.get(
                    Notification.DeliveryStatus.FAILED,
                    0,
                )
            ),
        },
    }


def apply_automatic_escalation(
    incident,
    actor=None,
):
    """
    Automatically apply the recommended escalation decision.
    """

    impact = build_incident_impact(
        incident
    )

    recommendation = (
        impact[
            "recommended_escalation"
        ]
    )

    previous_level = (
        incident.escalation_level
    )

    previous_status = (
        incident.escalation_status
    )

    previous_team = (
        incident.escalation_team
    )

    incident.escalation_level = (
        recommendation["level"]
    )

    incident.escalation_status = (
        recommendation["status"]
    )

    incident.escalation_team = (
        recommendation["team"]
    )

    if (
        recommendation["status"]
        != Incident.EscalationStatus.NOT_ESCALATED
    ):
        if incident.escalated_at is None:
            incident.escalated_at = (
                timezone.now()
            )
    else:
        incident.escalated_at = None

    incident.save(
        update_fields=[
            "escalation_level",
            "escalation_status",
            "escalation_team",
            "escalated_at",
            "updated_at",
        ]
    )

    changed = (
        previous_level
        != incident.escalation_level
        or previous_status
        != incident.escalation_status
        or previous_team
        != incident.escalation_team
    )

    if changed:
        IncidentEvent.objects.create(
            incident=incident,

            event_type=(
                IncidentEvent.EventType.ESCALATION
            ),

            message=(
                "Automatic escalation: "
                f"{incident.get_escalation_level_display()} "
                "to "
                f"{incident.escalation_team or 'monitoring only'}. "
                f"{recommendation['recommended_response']}"
            ),

            actor=actor,
        )

    return build_incident_impact(
        incident
    )


class IncidentImpactView(StaffAPIView):
    """
    GET:
    Show network, customer, communication and
    maintenance impact.

    POST:
    Apply automatic or operator-controlled escalation.
    """

    def get(
        self,
        request,
        incident_id,
    ):
        incident = get_object_or_404(
            Incident.objects.select_related(
                "site",
                "assigned_to",
            ).prefetch_related(
                "affected_sites",
            ),

            pk=incident_id,
        )

        return Response(
            build_incident_impact(
                incident
            )
        )

    def post(
        self,
        request,
        incident_id,
    ):
        incident = get_object_or_404(
            Incident,
            pk=incident_id,
        )

        serializer = EscalationSerializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        automatic = (
            serializer.validated_data.get(
                "automatic",
                False,
            )
        )

        if automatic:
            return Response(
                apply_automatic_escalation(
                    incident,
                    actor=request.user,
                )
            )

        if "escalation_level" in (
            serializer.validated_data
        ):
            incident.escalation_level = (
                serializer.validated_data[
                    "escalation_level"
                ]
            )

        if "escalation_status" in (
            serializer.validated_data
        ):
            incident.escalation_status = (
                serializer.validated_data[
                    "escalation_status"
                ]
            )

        if "escalation_team" in (
            serializer.validated_data
        ):
            incident.escalation_team = (
                serializer.validated_data[
                    "escalation_team"
                ].strip()
            )

        if (
            incident.escalation_status
            != Incident.EscalationStatus.NOT_ESCALATED
        ):
            if incident.escalated_at is None:
                incident.escalated_at = (
                    timezone.now()
                )
        else:
            incident.escalated_at = None

        incident.save()

        IncidentEvent.objects.create(
            incident=incident,

            event_type=(
                IncidentEvent.EventType.ESCALATION
            ),

            message=(
                "Incident escalation updated to "
                f"{incident.get_escalation_level_display()}. "
                f"Team: "
                f"{incident.escalation_team or 'Not assigned'}."
            ),

            actor=request.user,
        )

        return Response(
            build_incident_impact(
                incident
            )
        )