from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse

from rest_framework.test import APITestCase

from .models import (
    Customer,
    Incident,
    Notification,
    Site,
)


User = get_user_model()


@override_settings(
    NETSAGE_SMS_MODE="dry_run",
    AFRICASTALKING_USERNAME="sandbox",
    AFRICASTALKING_API_KEY="",
    AFRICASTALKING_TEST_RECIPIENTS=[],
)
class NotificationSendTests(APITestCase):
    def setUp(self):
        self.operator = User.objects.create_user(
            username="sms-operator",
            password="test-password-only",
            is_staff=True,
        )

        self.client.force_authenticate(
            user=self.operator,
        )

        self.site = Site.objects.create(
            name="SMS Test Site",
            code="sms-test-site",
            location="Mukono",
        )

        self.incident = Incident.objects.create(
            site=self.site,
            title="SMS test incident",
        )

        self.customer_a = Customer.objects.create(
            site=self.site,
            name="SMS Customer A",
            phone_number="+256700000001",
            sms_opt_in=True,
            is_active=True,
        )

        self.customer_b = Customer.objects.create(
            site=self.site,
            name="SMS Customer B",
            phone_number="+256700000002",
            sms_opt_in=True,
            is_active=True,
        )

    def create_draft(self):
        return self.client.post(
            reverse(
                "notification-draft",
                args=[self.incident.pk],
            ),
            {
                "message_type": "outage",
                "message": "NetSage dry run test.",
            },
            format="json",
        )

    def approve(self):
        return self.client.post(
            reverse(
                "notification-approve",
                args=[self.incident.pk],
            ),
            {"message_type": "outage"},
            format="json",
        )

    def test_unapproved_message_cannot_be_sent(self):
        self.create_draft()

        response = self.client.post(
            reverse(
                "notification-send",
                args=[self.incident.pk],
            ),
            {"message_type": "outage"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_dry_run_never_marks_message_as_sent(self):
        self.create_draft()
        self.approve()

        response = self.client.post(
            reverse(
                "notification-send",
                args=[self.incident.pk],
            ),
            {"message_type": "outage"},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
            response.data,
        )

        self.assertEqual(
            response.data["mode"],
            "dry_run",
        )
        self.assertEqual(
            response.data["dry_run_count"],
            2,
        )

        notifications = Notification.objects.all()

        self.assertFalse(
            notifications.exclude(
                delivery_status=(
                    Notification.DeliveryStatus.DRY_RUN
                )
            ).exists()
        )

        self.assertFalse(
            notifications.filter(
                sent_at__isnull=False
            ).exists()
        )

    def test_history_reports_dry_run_truthfully(self):
        self.create_draft()
        self.approve()

        self.client.post(
            reverse(
                "notification-send",
                args=[self.incident.pk],
            ),
            {"message_type": "outage"},
            format="json",
        )

        response = self.client.get(
            reverse(
                "notification-history",
                args=[self.incident.pk],
            ),
            {"message_type": "outage"},
        )

        self.assertEqual(
            response.status_code,
            200,
            response.data,
        )

        self.assertEqual(
            response.data["recipient_count"],
            2,
        )

        statuses = {
            item["delivery_status"]
            for item in response.data[
                "notifications"
            ]
        }

        self.assertEqual(
            statuses,
            {"dry_run"},
        )
