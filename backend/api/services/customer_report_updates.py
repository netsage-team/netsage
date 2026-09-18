from django.db.models import Q

from ..models import CustomerNetworkReport, Incident, Notification

from .sms import (
    SmsConfigurationError,
    SmsRecipientError,
    send_sms,
)


def get_report_update_recipients(incident):
    """Return unique customers who reported an issue linked to this incident."""

    reports = (
        CustomerNetworkReport.objects
        .filter(
            incident=incident,
            customer__isnull=False,
            customer__is_active=True,
            updates_opted_in=True,
        )
        .select_related("customer", "site")
        .order_by("customer__id", "id")
    )

    unique_reports = {}
    for report in reports:
        unique_reports.setdefault(
            report.customer_id,
            report,
        )

    return list(unique_reports.values())


def send_report_progress_update(incident, message):
    """Send a progress update to incident reporters."""

    if incident.status == Incident.Status.RESOLVED:
        return []

    reports = get_report_update_recipients(incident)
    notifications = []

    for report in reports:
        already_sent = Notification.objects.filter(
            incident=incident,
            customer=report.customer,
            message_type=Notification.MessageType.UPDATE,
            message=message,
            delivery_status__in=[
                Notification.DeliveryStatus.DRY_RUN,
                Notification.DeliveryStatus.SENT,
                Notification.DeliveryStatus.DELIVERED,
            ],
        ).exists()

        if already_sent:
            continue

        notifications.append(
            Notification(
                incident=incident,
                customer=report.customer,
                recipient_phone=report.customer.phone_number,
                message_type=Notification.MessageType.UPDATE,
                message=message,
                approval_status=(
                    Notification.ApprovalStatus.APPROVED
                ),
                delivery_status=(
                    Notification.DeliveryStatus.NOT_SENT
                ),
            )
        )

    if not notifications:
        return []

    Notification.objects.bulk_create(notifications)

    recipients = [
        notification.recipient_phone
        for notification in notifications
    ]

    try:
        result = send_sms(
            message,
            recipients,
        )
    except (
        SmsConfigurationError,
        SmsRecipientError,
        ValueError,
    ) as exc:
        for notification in notifications:
            notification.delivery_status = (
                Notification.DeliveryStatus.FAILED
            )
            notification.error_message = str(exc)

        Notification.objects.bulk_update(
            notifications,
            [
                "delivery_status",
                "error_message",
                "updated_at",
            ],
        )

        return notifications

    provider_results = {
        item.get("number"): item
        for item in result.get("recipients", [])
    }

    for notification in notifications:
        provider = provider_results.get(
            notification.recipient_phone,
            {},
        )

        notification.provider_message_id = str(
            provider.get("messageId", "") or ""
        )

        if result["mode"] == "dry_run":
            notification.delivery_status = (
                Notification.DeliveryStatus.DRY_RUN
            )
            continue

        provider_status = str(
            provider.get("status", "")
        ).strip()

        status_code = provider.get("statusCode")

        accepted = (
            provider_status.lower()
            in {
                "success",
                "sent",
                "queued",
            }
            or status_code in {100, 101, 102}
        )

        if accepted:
            notification.delivery_status = (
                Notification.DeliveryStatus.SENT
            )
        else:
            notification.delivery_status = (
                Notification.DeliveryStatus.FAILED
            )
            notification.error_message = (
                provider_status
                or "Provider did not accept the message."
            )

    Notification.objects.bulk_update(
        notifications,
        [
            "delivery_status",
            "provider_message_id",
            "error_message",
            "updated_at",
        ],
    )

    return notifications

def send_report_recovery_update(incident, message):
    """Send a recovery update to incident reporters."""

    if (
        incident.status
        not in {
            Incident.Status.MONITORING,
            Incident.Status.RESOLVED,
        }
        or incident.recovery_verified_at is None
    ):
        return []

    reports = get_report_update_recipients(incident)

    notifications = []

    for report in reports:
        already_sent = Notification.objects.filter(
            incident=incident,
            customer=report.customer,
            message_type=Notification.MessageType.RECOVERY,
            message=message,
            delivery_status__in=[
                Notification.DeliveryStatus.DRY_RUN,
                Notification.DeliveryStatus.SENT,
                Notification.DeliveryStatus.DELIVERED,
            ],
        ).exists()

        if already_sent:
            continue

        notifications.append(
            Notification(
                incident=incident,
                customer=report.customer,
                recipient_phone=report.customer.phone_number,
                message_type=Notification.MessageType.RECOVERY,
                message=message,
                approval_status=(
                    Notification.ApprovalStatus.APPROVED
                ),
                delivery_status=(
                    Notification.DeliveryStatus.NOT_SENT
                ),
            )
        )

    if not notifications:
        return []

    Notification.objects.bulk_create(notifications)

    recipients = [
        notification.recipient_phone
        for notification in notifications
    ]

    try:
        result = send_sms(
            message,
            recipients,
        )
    except (
        SmsConfigurationError,
        SmsRecipientError,
        ValueError,
    ) as exc:
        for notification in notifications:
            notification.delivery_status = (
                Notification.DeliveryStatus.FAILED
            )
            notification.error_message = str(exc)

        Notification.objects.bulk_update(
            notifications,
            [
                "delivery_status",
                "error_message",
                "updated_at",
            ],
        )

        return notifications

    provider_results = {
        item.get("number"): item
        for item in result.get("recipients", [])
    }

    for notification in notifications:
        provider = provider_results.get(
            notification.recipient_phone,
            {},
        )

        notification.provider_message_id = str(
            provider.get("messageId", "") or ""
        )

        if result["mode"] == "dry_run":
            notification.delivery_status = (
                Notification.DeliveryStatus.DRY_RUN
            )
            continue

        provider_status = str(
            provider.get("status", "")
        ).strip()

        status_code = provider.get("statusCode")

        accepted = (
            provider_status.lower()
            in {
                "success",
                "sent",
                "queued",
            }
            or status_code in {100, 101, 102}
        )

        if accepted:
            notification.delivery_status = (
                Notification.DeliveryStatus.SENT
            )
        else:
            notification.delivery_status = (
                Notification.DeliveryStatus.FAILED
            )
            notification.error_message = (
                provider_status
                or "Provider did not accept the message."
            )

    Notification.objects.bulk_update(
        notifications,
        [
            "delivery_status",
            "provider_message_id",
            "error_message",
            "updated_at",
        ],
    )

    return notifications