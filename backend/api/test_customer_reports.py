from django.test import TestCase

from .models import Customer, CustomerNetworkReport, Incident, Site
from .services.customer_reports import match_customer_report_to_incident


class CustomerReportMatchingTests(TestCase):
    def setUp(self):
        self.site = Site.objects.create(
            name="Test Mukono",
            code="report-mukono",
            location="Mukono",
        )

        self.customer = Customer.objects.create(
            site=self.site,
            name="Test Customer",
            phone_number="+256700123456",
            sms_opt_in=True,
            is_active=True,
        )

        self.incident = Incident.objects.create(
            site=self.site,
            title="Mukono network outage",
            description="Customer service degradation in Mukono.",
            status=Incident.Status.OPEN,
        )

        self.incident.affected_sites.set([self.site])

    def test_report_matches_customer_site_and_incident(self):
        report = CustomerNetworkReport.objects.create(
            sender_phone=self.customer.phone_number,
            message="Internet is not working.",
        )

        matched_report = match_customer_report_to_incident(report)

        self.assertEqual(matched_report.customer, self.customer)
        self.assertEqual(matched_report.site, self.site)
        self.assertEqual(matched_report.incident, self.incident)
        self.assertEqual(
            matched_report.status,
            CustomerNetworkReport.Status.MATCHED,
        )

    def test_unknown_customer_report_is_not_matched(self):
        report = CustomerNetworkReport.objects.create(
            sender_phone="+256701999999",
            message="Internet is not working.",
        )

        matched_report = match_customer_report_to_incident(report)

        self.assertIsNone(matched_report.customer)
        self.assertIsNone(matched_report.site)
        self.assertIsNone(matched_report.incident)
        self.assertEqual(
            matched_report.status,
            CustomerNetworkReport.Status.RECEIVED,
        )