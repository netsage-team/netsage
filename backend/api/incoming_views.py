from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import CustomerNetworkReport
from .services.customer_report_acknowledgement import (
    acknowledge_customer_report,
)
from .services.customer_reports import (
    match_customer_report_to_incident,
)


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

    match_customer_report_to_incident(report)

    acknowledge_customer_report(report)

    return JsonResponse(
        {
            "ok": True,
            "report_id": report.pk,
        },
        status=201,
    )