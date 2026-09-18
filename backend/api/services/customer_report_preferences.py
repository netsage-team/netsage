from ..models import CustomerNetworkReport


def opt_out_customer_report_updates(phone_number):
    """Disable future updates for reports from a customer."""

    reports = CustomerNetworkReport.objects.filter(
        sender_phone=phone_number,
        updates_opted_in=True,
    )

    updated_count = reports.update(
        updates_opted_in=False,
    )

    return updated_count