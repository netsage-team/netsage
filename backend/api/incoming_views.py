from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import CustomerNetworkReport


@csrf_exempt
@require_POST
def incoming_sms_webhook(request):
    """Receive and store incoming customer SMS reports."""

    sender_phone = (
        request.POST.get("from")
        or ""
    ).strip()

    message = (
        request.POST.get("text")
        or ""
    ).strip()

    link_id = (
        request.POST.get("linkId")
        or ""
    ).strip()

    if not sender_phone or not message:
        return JsonResponse(
            {
                "ok": False,
                "detail": "Incoming SMS requires sender and message.",
            },
            status=400,
        )

    report = CustomerNetworkReport.objects.create(
        sender_phone=sender_phone,
        message=message,
        link_id=link_id,
    )

    return JsonResponse(
        {
            "ok": True,
            "report_id": report.pk,
        },
        status=201,
    )