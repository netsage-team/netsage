from django.urls import reverse
from rest_framework.test import APITestCase

from .models import CustomerNetworkReport


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