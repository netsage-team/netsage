from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Alert, Incident, Severity


User = get_user_model()


class EngineerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class IncidentSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(source="site.name", read_only=True)
    assigned_to_name = serializers.CharField(
        source="assigned_to.username",
        read_only=True,
        default=None,
    )

    class Meta:
        model = Incident
        fields = [
            "id", "site", "site_name", "title", "description",
            "severity", "status", "assigned_to", "assigned_to_name",
            "opened_at", "resolved_at", "recovery_verified_at",
            "resolution_notes", "created_at", "updated_at",
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