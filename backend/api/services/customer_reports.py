from django.db.models import Q

from ..models import Customer, CustomerNetworkReport, Incident


def match_customer_report(report):
    """Match a customer network report to its customer and site."""

    customer = (
        Customer.objects
        .filter(
            phone_number=report.sender_phone,
            is_active=True,
        )
        .select_related("site")
        .first()
    )

    if customer is None:
        return None

    report.customer = customer
    report.site = customer.site
    report.save(
        update_fields=["customer", "site", "updated_at"]
    )

    return customer


def find_active_incident(site):
    """Find an active incident affecting the customer's site."""

    return (
        Incident.objects
        .filter(
            status__in=[
                Incident.Status.OPEN,
                Incident.Status.INVESTIGATING,
                Incident.Status.MONITORING,
            ],
        )
        .filter(
            Q(site=site) | Q(affected_sites=site)
        )
        .distinct()
        .order_by("-opened_at", "-id")
        .first()
    )


def match_customer_report_to_incident(report):
    """Match a customer report to its customer, site, and incident."""

    customer = match_customer_report(report)

    if customer is None:
        return report

    incident = find_active_incident(customer.site)

    if incident is None:
        return report

    report.incident = incident
    report.status = CustomerNetworkReport.Status.MATCHED
    report.save(
        update_fields=["incident", "status", "updated_at"]
    )

    return report