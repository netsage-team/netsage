from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Customer, CustomerNetworkReport, Site

class IncomingSMSTests(APITestCase):
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
        self.assertEqual(
            report.status,
            CustomerNetworkReport.Status.RECEIVED,
        )

    def test_stop_disables_customer_report_updates(self):
        site = Site.objects.create(
            name="STOP Test Site",
            code="stop-test-site",
            location="Mukono",
        )

        customer = Customer.objects.create(
            site=site,
            name="STOP Customer",
            phone_number="+256700123456",
            sms_opt_in=True,
            is_active=True,
        )

        report = CustomerNetworkReport.objects.create(
            sender_phone=customer.phone_number,
            customer=customer,
            site=site,
            message="Internet is not working.",
            status=CustomerNetworkReport.Status.ACKNOWLEDGED,
            updates_opted_in=True,
        )

        response = self.client.post(
            reverse("incoming-sms-webhook"),
            {
                "from": customer.phone_number,
                "text": "STOP",
            },
        )

        self.assertEqual(response.status_code, 200)

        report.refresh_from_db()

        self.assertFalse(
            report.updates_opted_in
        )

        self.assertEqual(
            CustomerNetworkReport.objects.count(),
            1,
        )