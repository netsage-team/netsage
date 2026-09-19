from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Alert,
    CustomerNetworkReport,
    Incident,
    IncidentEvent,
    Notification,
    Severity,
)


User = get_user_model()


class EngineerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class IncidentEventSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(
        source="actor.username",
        read_only=True,
        default=None,
    )

    class Meta:
        model = IncidentEvent
        fields = [
            "id",
            "event_type",
            "message",
            "actor",
            "actor_name",
            "created_at",
        ]
        read_only_fields = fields


class IncidentSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source="site.name", read_only=True)
    timeline = IncidentEventSerializer(
        many=True,
        read_only=True,
    )
    affected_sites = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
    )
    affected_site_names = serializers.SlugRelatedField(
        source="affected_sites",
        many=True,
        read_only=True,
        slug_field="name",
    )
    assigned_to_name = serializers.CharField(
        source="assigned_to.username",
        read_only=True,
        default=None,
    )

    class Meta:
        model = Incident
        fields = [
            "id", "site", "site_name",
            "affected_sites", "affected_site_names",
            "shared_dependency", "probable_cause", "confidence_note",
            "title", "description",
            "severity", "status", "assigned_to", "assigned_to_name",
            "opened_at", "resolved_at", "recovery_verified_at",
            "resolution_notes", "timeline",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class AlertSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(source="device.name", read_only=True)
    site = serializers.IntegerField(source="device.site_id", read_only=True)

    class Meta:
        model = Alert
        fields = [
            "id", "device", "device_name", "site", "reading",
            "incident", "alert_type", "severity", "message",
            "detected_at", "cleared_at",
        ]
        read_only_fields = fields


class SiteFilterSerializer(serializers.Serializer):
    site = serializers.IntegerField(required=False, min_value=1)


class IncidentFilterSerializer(SiteFilterSerializer):
    status = serializers.ChoiceField(
        choices=Incident.Status.choices,
        required=False,
    )
    severity = serializers.ChoiceField(
        choices=Severity.choices,
        required=False,
    )
    assigned_to = serializers.IntegerField(required=False, min_value=1)


class AlertFilterSerializer(SiteFilterSerializer):
    device = serializers.IntegerField(required=False, min_value=1)
    incident = serializers.IntegerField(required=False, min_value=1)
    severity = serializers.ChoiceField(
        choices=Severity.choices,
        required=False,
    )
    cleared = serializers.BooleanField(required=False)


class IncidentNoteSerializer(serializers.Serializer):
    note = serializers.CharField(
        max_length=2000,
        trim_whitespace=True,
    )


class IncidentResolutionSerializer(serializers.Serializer):
    resolution_notes = serializers.CharField(
        max_length=2000,
        trim_whitespace=True,
    )


class IncidentUpdateSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True, is_staff=True),
        required=False,
        allow_null=True,
    )
    status = serializers.ChoiceField(
        choices=[Incident.Status.INVESTIGATING],
        required=False,
    )

    class Meta:
        model = Incident
        fields = ["assigned_to", "status", "resolution_notes"]

    def validate(self, attrs):
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({
                field: "This field cannot be changed here."
                for field in unknown
            })

        if not attrs:
            raise serializers.ValidationError("Provide at least one change.")

        if self.instance.status == Incident.Status.RESOLVED:
            raise serializers.ValidationError(
                "Resolved incidents cannot be edited here."
            )

        if "status" in attrs and self.instance.status not in (
            Incident.Status.OPEN,
            Incident.Status.INVESTIGATING,
        ):
            raise serializers.ValidationError({
                "status": "This incident is already being monitored for recovery."
            })

        return attrs

class CustomerReportSerializer(serializers.ModelSerializer):
    masked_sender = serializers.SerializerMethodField()
    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
        default=None,
    )
    site_id = serializers.IntegerField(
        source="site.id",
        read_only=True,
        default=None,
    )
    site_name = serializers.CharField(
        source="site.name",
        read_only=True,
        default=None,
    )
    site_type = serializers.CharField(
        source="site.site_type",
        read_only=True,
        default=None,
    )
    incident_id = serializers.IntegerField(
        source="incident.id",
        read_only=True,
        default=None,
    )
    incident_status = serializers.CharField(
        source="incident.status",
        read_only=True,
        default=None,
    )
    report_status = serializers.CharField(
        source="status",
        read_only=True,
    )
    acknowledgement_status = serializers.SerializerMethodField()
    received_at = serializers.DateTimeField(
        source="created_at",
        read_only=True,
    )
    latest_delivery_status = serializers.SerializerMethodField()

    class Meta:
        model = CustomerNetworkReport
        fields = [
            "id",
            "masked_sender",
            "customer_name",
            "site_id",
            "site_name",
            "site_type",
            "incident_id",
            "incident_status",
            "message",
            "report_status",
            "acknowledgement_status",
            "received_at",
            "latest_delivery_status",
        ]
        read_only_fields = fields

    def get_masked_sender(self, obj):
        phone = obj.sender_phone

        if len(phone) <= 4:
            return "*" * len(phone)

        return f"{phone[:4]}{'*' * (len(phone) - 7)}{phone[-3:]}"

    def get_acknowledgement_status(self, obj):
        if obj.status == CustomerNetworkReport.Status.ACKNOWLEDGED:
            return "acknowledged"

        return "not_acknowledged"

    def get_latest_delivery_status(self, obj):
        if obj.customer_id is None or obj.incident_id is None:
            return None

        notification = (
            Notification.objects
            .filter(
                customer_id=obj.customer_id,
                incident_id=obj.incident_id,
            )
            .order_by("-created_at", "-id")
            .first()
        )

        if notification is None:
            return None

        return notification.delivery_status