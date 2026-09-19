from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import Notification


DELIVERED_STATUSES = {
    "success",
    "delivered",
}

FAILED_STATUSES = {
    "failed",
    "rejected",
    "expired",
}

SENT_STATUSES = {
    "sent",
    "submitted",
}

QUEUED_STATUSES = {
    "buffered",
    "queued",
}


@csrf_exempt
@require_POST
def sms_delivery_report(request):
    """
    Receive Africa's Talking SMS delivery reports.

    Africa's Talking posts form-encoded delivery reports containing
    values such as:
    id, status, phoneNumber, networkCode and failureReason.
    """

    message_id = (
        request.POST.get("id")
        or request.POST.get("messageId")
        or ""
    ).strip()

    provider_status = (
        request.POST.get("status")
        or ""
    ).strip()

    phone_number = (
        request.POST.get("phoneNumber")
        or ""
    ).strip()

    failure_reason = (
        request.POST.get("failureReason")
        or ""
    ).strip()

    if not message_id or not provider_status:
        return JsonResponse(
            {
                "ok": False,
                "detail": (
                    "Delivery report requires "
                    "message ID and status."
                ),
            },
            status=400,
        )

    with transaction.atomic():
        notification = (
            Notification.objects.select_for_update()
            .filter(
                provider_message_id=message_id,
            )
            .first()
        )

        if notification is None:
            # Return 200 so the provider does not keep retrying
            # a delivery report we cannot match.
            return JsonResponse({
                "ok": True,
                "matched": False,
            })

        normalized = provider_status.lower()

        if normalized in DELIVERED_STATUSES:
            notification.delivery_status = (
                Notification.DeliveryStatus.DELIVERED
            )
            notification.delivered_at = timezone.now()
            notification.error_message = ""

        elif normalized in FAILED_STATUSES:
            notification.delivery_status = (
                Notification.DeliveryStatus.FAILED
            )
            notification.error_message = (
                failure_reason
                or f"Provider status: {provider_status}"
            )

        elif normalized in QUEUED_STATUSES:
            notification.delivery_status = (
                Notification.DeliveryStatus.QUEUED
            )

        elif normalized in SENT_STATUSES:
            notification.delivery_status = (
                Notification.DeliveryStatus.SENT
            )

        else:
            # Unknown statuses should not destroy the existing state.
            return JsonResponse({
                "ok": True,
                "matched": True,
                "updated": False,
                "status": provider_status,
            })

        notification.save(
            update_fields=[
                "delivery_status",
                "delivered_at",
                "error_message",
                "updated_at",
            ]
        )

    return JsonResponse({
        "ok": True,
        "matched": True,
        "updated": True,
        "message_id": message_id,
        "phone_number": phone_number,
        "status": provider_status,
    })
