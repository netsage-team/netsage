from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase

from .models import (
    Customer,
    Incident,
    Notification,
    Site,
)


User = get_user_model()


class NotificationWorkflowTests(APITestCase):
    def setUp(self):
        self.operator = User.objects.create_user(
            username="notification-operator",
            password="test-password-only",
            is_staff=True,
        )

        self.client.force_authenticate(
            user=self.operator,
        )

        self.site_a = Site.objects.create(
            name="Mukono Test",
            code="notification-mukono",
            location="Mukono",
        )

        self.site_b = Site.objects.create(
            name="Seeta Test",
            code="notification-seeta",
            location="Seeta",
        )

        self.unrelated_site = Site.objects.create(
            name="Unrelated Test",
            code="notification-unrelated",
            location="Kampala",
        )

        self.incident = Incident.objects.create(
            site=self.site_a,
            title="Notification test incident",
        )

        self.incident.affected_sites.set([
            self.site_a,
            self.site_b,
        ])

        self.customer_a = Customer.objects.create(
            site=self.site_a,
            name="Eligible A",
            phone_number="+256700000001",
            sms_opt_in=True,
            is_active=True,
        )

        self.customer_b = Customer.objects.create(
            site=self.site_b,
            name="Eligible B",
            phone_number="+256700000002",
            sms_opt_in=True,
            is_active=True,
        )

        Customer.objects.create(
            site=self.site_a,
            name="Opted out",
            phone_number="+256700000003",
            sms_opt_in=False,
            is_active=True,
        )

        Customer.objects.create(
            site=self.site_b,
            name="Inactive",
            phone_number="+256700000004",
            sms_opt_in=True,
            is_active=False,
        )

        Customer.objects.create(
            site=self.unrelated_site,
            name="Other site",
            phone_number="+256700000005",
            sms_opt_in=True,
            is_active=True,
        )

    def draft_payload(self, message="Service issue update."):
        return {
            "message_type": "outage",
            "message": message,
        }

    def test_audience_contains_only_eligible_affected_customers(self):
        response = self.client.get(
            reverse(
                "notification-audience",
                args=[self.incident.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
            response.data,
        )

        self.assertEqual(
            response.data["eligible_recipients"],
            2,
        )

        names = {
            recipient["name"]
            for recipient in response.data["recipients"]
        }

        self.assertEqual(
            names,
            {"Eligible A", "Eligible B"},
        )

    def test_draft_creates_one_pending_notification_per_recipient(self):
        response = self.client.post(
            reverse(
                "notification-draft",
                args=[self.incident.pk],
            ),
            self.draft_payload(),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
            response.data,
        )

        self.assertEqual(
            Notification.objects.count(),
            2,
        )

        self.assertFalse(
            Notification.objects.exclude(
                approval_status=(
                    Notification.ApprovalStatus.PENDING
                ),
                delivery_status=(
                    Notification.DeliveryStatus.NOT_SENT
                ),
            ).exists()
        )

    def test_editing_unsent_draft_does_not_duplicate_recipients(self):
        url = reverse(
            "notification-draft",
            args=[self.incident.pk],
        )

        self.client.post(
            url,
            self.draft_payload("First draft."),
            format="json",
        )

        response = self.client.post(
            url,
            self.draft_payload("Edited draft."),
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
            response.data,
        )

        self.assertEqual(
            Notification.objects.count(),
            2,
        )

        self.assertFalse(
            Notification.objects.exclude(
                message="Edited draft."
            ).exists()
        )

    def test_operator_can_approve_existing_unsent_draft(self):
        self.client.post(
            reverse(
                "notification-draft",
                args=[self.incident.pk],
            ),
            self.draft_payload(),
            format="json",
        )

        response = self.client.post(
            reverse(
                "notification-approve",
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

        self.assertFalse(
            Notification.objects.exclude(
                approval_status=(
                    Notification.ApprovalStatus.APPROVED
                ),
                approved_by=self.operator,
            ).exists()
        )

    def test_nonstaff_cannot_access_notification_audience(self):
        user = User.objects.create_user(
            username="nonstaff",
            password="test-password-only",
        )

        self.client.force_authenticate(
            user=user,
        )

        response = self.client.get(
            reverse(
                "notification-audience",
                args=[self.incident.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )


class NotificationDraftStatusTests(NotificationWorkflowTests):
    def test_unsent_draft_can_be_loaded_again(self):
        self.client.post(
            reverse(
                "notification-draft",
                args=[self.incident.pk],
            ),
            {
                "message_type": "outage",
                "message": "Persistent customer update.",
            },
            format="json",
        )

        response = self.client.get(
            reverse(
                "notification-draft",
                args=[self.incident.pk],
            ),
            {"message_type": "outage"},
        )

        self.assertEqual(
            response.status_code,
            200,
            response.data,
        )
        self.assertTrue(response.data["exists"])
        self.assertEqual(
            response.data["message"],
            "Persistent customer update.",
        )
        self.assertEqual(
            response.data["recipient_count"],
            2,
        )

    def test_missing_draft_returns_clean_empty_state(self):
        response = self.client.get(
            reverse(
                "notification-draft",
                args=[self.incident.pk],
            ),
            {"message_type": "recovery"},
        )

        self.assertEqual(
            response.status_code,
            200,
            response.data,
        )
        self.assertFalse(response.data["exists"])
        self.assertEqual(
            response.data["recipient_count"],
            0,
        )
