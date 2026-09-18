from rest_framework import serializers

from .models import Device, Site


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = [
            "id",
            "name",
            "code",
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