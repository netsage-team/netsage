from django.urls import reverse

from rest_framework.test import APITestCase

from .models import (
    Customer,
    Incident,
    Notification,
    Site,
)


class SmsDeliveryCallbackTests(APITestCase):
    def setUp(self):
        self.site = Site.objects.create(
            name="Callback Test Site",
            code="callback-test-site",
            location="Mukono",
        )

        self.customer = Customer.objects.create(
            site=self.site,
            name="Callback Customer",
            phone_number="+256700000001",
            sms_opt_in=True,
            is_active=True,
        )

        self.incident = Incident.objects.create(
            site=self.site,
            title="Callback test incident",
        )

        self.notification = Notification.objects.create(
            incident=self.incident,
            customer=self.customer,
            recipient_phone=self.customer.phone_number,
            message_type=Notification.MessageType.OUTAGE,
            message="Test SMS",
            approval_status=Notification.ApprovalStatus.APPROVED,
            delivery_status=Notification.DeliveryStatus.SENT,
            provider_message_id="ATXid-test-123",
        )

    def test_success_callback_marks_notification_delivered(self):
        response = self.client.post(
            reverse("sms-delivery-report"),
            {
                "id": "ATXid-test-123",
                "status": "Success",
                "phoneNumber": "+256700000001",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.notification.refresh_from_db()

        self.assertEqual(
            self.notification.delivery_status,
            Notification.DeliveryStatus.DELIVERED,
        )
        self.assertIsNotNone(
            self.notification.delivered_at,
        )

    def test_failed_callback_marks_notification_failed(self):
        response = self.client.post(
            reverse("sms-delivery-report"),
            {
                "id": "ATXid-test-123",
                "status": "Failed",
                "phoneNumber": "+256700000001",
                "failureReason": "Test failure",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.notification.refresh_from_db()

        self.assertEqual(
            self.notification.delivery_status,
            Notification.DeliveryStatus.FAILED,
        )
        self.assertEqual(
            self.notification.error_message,
            "Test failure",
        )

    def test_unknown_message_id_returns_safe_success(self):
        response = self.client.post(
            reverse("sms-delivery-report"),
            {
                "id": "unknown-message",
                "status": "Success",
                "phoneNumber": "+256700000001",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["matched"])

    def test_missing_required_callback_fields_is_rejected(self):
        response = self.client.post(
            reverse("sms-delivery-report"),
            {
                "phoneNumber": "+256700000001",
            },
        )

        self.assertEqual(response.status_code, 400)
