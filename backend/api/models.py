from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Severity(models.TextChoices):
    WARNING = "warning", "Warning"
    CRITICAL = "critical", "Critical"


class Site(TimeStampedModel):
    """A physical or logical service location monitored by NetSage."""

    class SiteType(models.TextChoices):
        TOWER = "tower", "Tower"
        POP = "pop", "Point of presence"
        DATA_CENTER = "data_center", "Data centre"
        EXCHANGE = "exchange", "Exchange"
        OTHER = "other", "Other"

    name = models.CharField(max_length=120)
    code = models.SlugField(max_length=50, unique=True)
    site_type = models.CharField(
        max_length=20,
        choices=SiteType.choices,
        default=SiteType.OTHER,
    )
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Device(TimeStampedModel):
    """Network equipment belonging to a site."""

    class DeviceType(models.TextChoices):
        ROUTER = "router", "Router"
        SWITCH = "switch", "Switch"
        ACCESS_POINT = "access_point", "Access point"
        OTHER = "other", "Other"

    site = models.ForeignKey(
        Site,
        on_delete=models.PROTECT,
        related_name="devices",
    )
    name = models.CharField(max_length=120)
    code = models.SlugField(max_length=80, unique=True)
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.ROUTER,
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.site.name})"


class TelemetryReading(models.Model):
    """One measurement collected from a device."""

    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="readings",
    )
    recorded_at = models.DateTimeField(default=timezone.now)
    received_at = models.DateTimeField(auto_now_add=True)
    is_reachable = models.BooleanField()

    # A timeout has no latency value; do not record it as zero.
    latency_ms = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    packet_loss_percent = models.FloatField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
    )
    is_simulated = models.BooleanField(default=True)

    class Meta:
        ordering = ["-recorded_at", "-id"]
        indexes = [
            models.Index(fields=["device", "-recorded_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(latency_ms__isnull=True)
                    | models.Q(latency_ms__gte=0)
                ),
                name="telemetry_latency_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    packet_loss_percent__gte=0,
                    packet_loss_percent__lte=100,
                ),
                name="telemetry_packet_loss_range",
            ),
        ]

    def __str__(self):
        return f"{self.device.code} at {self.recorded_at}"


class Incident(TimeStampedModel):
    """A service issue that can group multiple device alerts."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        MONITORING = "monitoring", "Monitoring recovery"
        RESOLVED = "resolved", "Resolved"

    site = models.ForeignKey(
        Site,
        on_delete=models.PROTECT,
        related_name="incidents",
    )

    # The primary/anchor site keeps existing API compatibility.
    # affected_sites represents correlated multi-site incidents.
    affected_sites = models.ManyToManyField(
        Site,
        related_name="affected_incidents",
        blank=True,
    )
    shared_dependency = models.CharField(
        max_length=120,
        blank=True,
    )
    probable_cause = models.TextField(blank=True)
    confidence_note = models.TextField(blank=True)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.WARNING,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_incidents",
    )
    opened_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)
    recovery_verified_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-opened_at", "-id"]

    def __str__(self):
        return f"{self.title} ({self.status})"


class Alert(TimeStampedModel):
    """A detected problem, optionally grouped into an incident."""

    class AlertType(models.TextChoices):
        DEVICE_DOWN = "device_down", "Device unreachable"
        HIGH_LATENCY = "high_latency", "High latency"
        PACKET_LOSS = "packet_loss", "Packet loss"

    device = models.ForeignKey(
        Device,
        on_delete=models.PROTECT,
        related_name="alerts",
    )
    reading = models.ForeignKey(
        TelemetryReading,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts",
    )
    incident = models.ForeignKey(
        Incident,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="alerts",
    )
    alert_type = models.CharField(
        max_length=30,
        choices=AlertType.choices,
    )
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.WARNING,
    )
    message = models.TextField()
    detected_at = models.DateTimeField(default=timezone.now)
    cleared_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-detected_at", "-id"]

    def __str__(self):
        return f"{self.device.code}: {self.alert_type}"


class IncidentEvent(models.Model):
    """An auditable activity recorded against an incident."""

    class EventType(models.TextChoices):
        DETECTED = "detected", "Incident detected"
        ASSIGNMENT = "assignment", "Engineer assignment"
        STATUS = "status", "Status change"
        NOTE = "note", "Investigation note"
        RECOVERY = "recovery", "Recovery update"
        RESOLVED = "resolved", "Incident resolved"

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name="timeline",
    )
    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
    )
    message = models.TextField()
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incident_events",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self):
        return f"{self.incident_id}: {self.event_type}"


class Customer(TimeStampedModel):
    """A customer receiving service from one site in the pilot."""

    site = models.ForeignKey(
        Site,
        on_delete=models.PROTECT,
        related_name="customers",
    )
    name = models.CharField(max_length=120)
    phone_number = models.CharField(
        max_length=16,
        validators=[
            RegexValidator(
                regex=r"^\+[1-9][0-9]{7,14}$",
                message=(
                    "Use international format, for example +256700123456."
                ),
            ),
        ],
    )
    sms_opt_in = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["site", "phone_number"],
                name="unique_customer_phone_per_site",
            ),
        ]

    def __str__(self):
        return self.name


class Notification(TimeStampedModel):
    """One SMS for one customer, with approval and delivery tracking."""

    class MessageType(models.TextChoices):
        OUTAGE = "outage", "Outage notice"
        UPDATE = "update", "Progress update"
        RECOVERY = "recovery", "Service restored"

    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class DeliveryStatus(models.TextChoices):
        NOT_SENT = "not_sent", "Not sent"
        DRY_RUN = "dry_run", "Dry run only"
        QUEUED = "queued", "Queued"
        SENT = "sent", "Accepted by SMS provider"
        DELIVERED = "delivered", "Delivered"
        FAILED = "failed", "Failed"

    incident = models.ForeignKey(
        Incident,
        on_delete=models.PROTECT,
        related_name="notifications",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="notifications",
    )

    # Keep the actual destination even if the customer's number changes.
    recipient_phone = models.CharField(
        max_length=16,
        validators=[
            RegexValidator(
                regex=r"^\+[1-9][0-9]{7,14}$",
                message="Use an international phone number.",
            ),
        ],
    )
    message_type = models.CharField(
        max_length=20,
        choices=MessageType.choices,
    )
    message = models.TextField()

    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_notifications",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    delivery_status = models.CharField(
        max_length=20,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.NOT_SENT,
    )
    provider_message_id = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"SMS #{self.pk}: {self.delivery_status}"