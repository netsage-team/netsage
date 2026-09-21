from ..models import CustomerNetworkReport, Incident
from .sms import (
    SmsConfigurationError,
    SmsRecipientError,
    send_sms,
)


STATUS_MESSAGES = {
    Incident.Status.INVESTIGATING: (
        "NetSage: Your reported network issue is now being "
        "investigated by our team."
    ),
    Incident.Status.MONITORING: (
        "NetSage: Service recovery has been detected for your "
        "reported network issue. We are monitoring the connection."
    ),
    Incident.Status.RESOLVED: (
        "NetSage: Your reported network issue has been resolved. "
        "Thank you for reporting it."
    ),
}


def notify_customers_of_incident_status(incident):
    """Send an automatic progress update to customers who reported an incident."""

    message = STATUS_MESSAGES.get(incident.status)

    if not message:
        return 0

    reports = (
        CustomerNetworkReport.objects
        .select_related("customer")
        .filter(
            incident=incident,
            customer__isnull=False,
            customer__is_active=True,
            customer__sms_opt_in=True,
        )
    )

    recipients = list(
        dict.fromkeys(
            report.sender_phone
            for report in reports
        )
    )

    if not recipients:
        return 0

    try:
        send_sms(message, recipients)
    except (
        SmsConfigurationError,
        SmsRecipientError,
        ValueError,
    ):
        return 0

    return len(recipients)
