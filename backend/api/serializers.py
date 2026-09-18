from rest_framework import serializers

from .models import Device, Site, TelemetryReading


class SiteSerializer(serializers.ModelSerializer):
    site_type_label = serializers.CharField(
        source="get_site_type_display",
        read_only=True,
    )

    class Meta:
        model = Site
        fields = [
            "id",
            "name",
            "code",
            "site_type",
            "site_type_label",
            "location",
            "description",
            "is_active",
        ]


class DeviceSerializer(serializers.ModelSerializer):
    site_name = serializers.CharField(
        source="site.name",
        read_only=True,
    )

    class Meta:
        model = Device
        fields = [
            "id",
            "name",
            "code",
            "site",
            "site_name",
            "device_type",
            "ip_address",
            "is_active",
        ]


class TelemetryReadingSerializer(serializers.ModelSerializer):
    device_name = serializers.CharField(
        source="device.name",
        read_only=True,
    )
    device_code = serializers.CharField(
        source="device.code",
        read_only=True,
    )
    site = serializers.IntegerField(
        source="device.site_id",
        read_only=True,
    )

    class Meta:
        model = TelemetryReading
        fields = [
            "id",
            "device",
            "device_name",
            "device_code",
            "site",
            "recorded_at",
            "received_at",
            "is_reachable",
            "latency_ms",
            "packet_loss_percent",
            "is_simulated",
        ]


class TelemetryFilterSerializer(serializers.Serializer):
    device = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    site = serializers.IntegerField(
        required=False,
        min_value=1,
    )