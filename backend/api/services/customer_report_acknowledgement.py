from ..models import CustomerNetworkReport
from .sms import (
    SmsConfigurationError,
    SmsRecipientError,
    send_sms,
)


ACKNOWLEDGEMENT_MESSAGE = (
    "NetSage: We received your network report. "
    "Our team is checking the issue. Thank you for letting us know."
)


def acknowledge_customer_report(report):
    """Send an automatic acknowledgement for a customer report."""

    if report.customer is None:
        return False

    try:
        send_sms(
            ACKNOWLEDGEMENT_MESSAGE,
            [report.sender_phone],
        )
    except (
        SmsConfigurationError,
        SmsRecipientError,
        ValueError,
    ):
        return False

    report.status = CustomerNetworkReport.Status.ACKNOWLEDGED
    report.save(
        update_fields=["status", "updated_at"]
    )

    return True