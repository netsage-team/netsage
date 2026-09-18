
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Customer, CustomerNetworkReport, Incident, Site


class IncomingSMSTests(APITestCase):
    def setUp(self):
        self.site = Site.objects.create(
            name="Test Mukono",
            code="incoming-mukono",
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

    def test_incoming_sms_creates_customer_network_report(self):
        response = self.client.post(
            reverse("incoming-sms-webhook"),
            {
                "from": "+256700123456",
                "text": "Internet is not working.",
                "linkId": "test-link-123",
            },
        )

        self.assertEqual(response.status_code, 201)

        report = CustomerNetworkReport.objects.get(
            pk=response.json()["report_id"]
        )

        self.assertEqual(report.sender_phone, "+256700123456")
        self.assertEqual(report.message, "Internet is not working.")
        self.assertEqual(report.link_id, "test-link-123")
        self.assertEqual(report.customer, self.customer)
        self.assertEqual(report.site, self.site)
        self.assertEqual(report.incident, self.incident)
        self.assertEqual(
            report.status,
            CustomerNetworkReport.Status.MATCHED,
        )

