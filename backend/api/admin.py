from django.contrib import admin

from .models import (
    Alert,
    Customer,
    Device,
    Incident,
    Notification,
    Site,
    TelemetryReading,
)


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "location", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "code", "location")
    prepopulated_fields = {"code": ("name",)}


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "site",
        "device_type",
        "ip_address",
        "is_active",
    )
    list_filter = ("device_type", "is_active", "site")
    search_fields = ("name", "code", "site__name")
    list_select_related = ("site",)


@admin.register(TelemetryReading)
class TelemetryReadingAdmin(admin.ModelAdmin):
    list_display = (
        "device",
        "recorded_at",
        "is_reachable",
        "latency_ms",
        "packet_loss_percent",
        "is_simulated",
    )
    list_filter = ("is_reachable", "is_simulated")
    search_fields = ("device__name", "device__code")
    list_select_related = ("device",)
    date_hierarchy = "recorded_at"
    readonly_fields = ("received_at",)


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "site",
        "severity",
        "status",
        "assigned_to",
        "opened_at",
    )
    list_filter = ("status", "severity", "site")
    search_fields = ("title", "description", "site__name")
    list_select_related = ("site", "assigned_to")
    autocomplete_fields = ("assigned_to",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "device",
        "alert_type",
        "severity",
        "incident",
        "detected_at",
        "cleared_at",
    )
    list_filter = ("alert_type", "severity")
    search_fields = ("message", "device__name", "device__code")
    list_select_related = ("device", "incident")
    autocomplete_fields = ("device", "incident")
    raw_id_fields = ("reading",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "site",
        "phone_number",
        "sms_opt_in",
        "is_active",
    )
    list_filter = ("sms_opt_in", "is_active", "site")
    search_fields = ("name", "phone_number", "site__name")
    list_select_related = ("site",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "incident",
        "message_type",
        "approval_status",
        "delivery_status",
        "created_at",
    )
    list_filter = (
        "message_type",
        "approval_status",
        "delivery_status",
    )
    search_fields = (
        "customer__name",
        "recipient_phone",
        "provider_message_id",
    )
    list_select_related = ("customer", "incident")

    # SMS records are inspection-only here.
    # Approval and sending will use the application workflow.
    def get_readonly_fields(self, request, obj=None):
        return tuple(field.name for field in self.model._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = "NetSage Administration"
admin.site.site_title = "NetSage Admin"
admin.site.index_title = "Network operations"