from unittest.mock import patch

from django.test import TestCase

from .models import (
    Customer,
    CustomerNetworkReport,
    Incident,
    Notification,
    Site,
)
from .services.customer_report_updates import (
    send_report_progress_update,
    send_report_recovery_update,
)

class CustomerReportProgressUpdateTests(TestCase):
    def setUp(self):
        self.site = Site.objects.create(
            name="Test Mukono",
            code="progress-mukono",
            location="Mukono",
        )

        self.customer = Customer.objects.create(
            site=self.site,
            name="Progress Customer",
            phone_number="+256700123456",
            sms_opt_in=True,
            is_active=True,
        )

        self.incident = Incident.objects.create(
            site=self.site,
            title="Mukono network issue",
            description="Network degradation in Mukono.",
            status=Incident.Status.INVESTIGATING,
        )

        self.report = CustomerNetworkReport.objects.create(
            sender_phone=self.customer.phone_number,
            customer=self.customer,
            site=self.site,
            incident=self.incident,
            message="Internet is slow.",
            status=CustomerNetworkReport.Status.ACKNOWLEDGED,
            updates_opted_in=True,
        )

    @patch(
        "api.services.customer_report_updates.send_sms"
    )
    def test_linked_report_receives_progress_update(
        self,
        mock_send_sms,
    ):
        mock_send_sms.return_value = {
            "mode": "dry_run",
            "recipients": [
                {
                    "number": self.customer.phone_number,
                    "status": "DryRun",
                }
            ],
        }

        message = (
            "NetSage: Engineers are continuing to investigate "
            "the network issue affecting Mukono Central. "
            "We will send another update when more information "
            "is available. Ref: INC-1."
        )

        notifications = send_report_progress_update(
            self.incident,
            message,
        )

        self.assertEqual(len(notifications), 1)

        notification = Notification.objects.get(
            incident=self.incident,
            customer=self.customer,
            message_type=Notification.MessageType.UPDATE,
        )

        self.assertEqual(
            notification.delivery_status,
            Notification.DeliveryStatus.DRY_RUN,
        )

        mock_send_sms.assert_called_once_with(
            message,
            [self.customer.phone_number],
        )
    @patch(
        "api.services.customer_report_updates.send_sms"
    )
    def test_unlinked_report_does_not_receive_progress_update(
        self,
        mock_send_sms,
    ):
        other_site = Site.objects.create(
            name="Other Site",
            code="other-site",
            location="Kampala",
        )

        other_customer = Customer.objects.create(
            site=other_site,
            name="Other Customer",
            phone_number="+256700123456",
            sms_opt_in=True,
            is_active=True,
        )

        CustomerNetworkReport.objects.create(
            sender_phone=other_customer.phone_number,
            customer=other_customer,
            site=other_site,
            message="Internet is down.",
            status=CustomerNetworkReport.Status.ACKNOWLEDGED,
            updates_opted_in=True,
        )

        message = (
            "NetSage: Engineers are continuing to investigate "
            "the network issue affecting Mukono Central."
        )

        notifications = send_report_progress_update(
            self.incident,
            message,
        )

        self.assertEqual(len(notifications), 1)

        self.assertEqual(
            notifications[0].customer,
            self.customer,
        )

        self.assertNotEqual(
            notifications[0].customer,
            other_customer,
        )

        mock_send_sms.assert_called_once_with(
            message,
            [self.customer.phone_number],
        )

    @patch(
        "api.services.customer_report_updates.send_sms"
    )
    def test_report_linked_to_another_incident_does_not_receive_update(
        self,
        mock_send_sms,
    ):
        other_incident = Incident.objects.create(
            site=self.site,
            title="Another Mukono issue",
            description="A separate network issue.",
            status=Incident.Status.INVESTIGATING,
        )

        CustomerNetworkReport.objects.create(
            sender_phone=self.customer.phone_number,
            customer=self.customer,
            site=self.site,
            incident=other_incident,
            message="Another problem.",
            status=CustomerNetworkReport.Status.ACKNOWLEDGED,
            updates_opted_in=True,
        )

        message = (
            "NetSage: Engineers are continuing to investigate "
            "the network issue affecting Mukono Central."
        )

        notifications = send_report_progress_update(
            self.incident,
            message,
        )

        self.assertEqual(len(notifications), 1)

        self.assertEqual(
            notifications[0].customer,
            self.customer,
        )

        mock_send_sms.assert_called_once_with(
            message,
            [self.customer.phone_number],
        )

    @patch(
        "api.services.customer_report_updates.send_sms"
    )
    def test_duplicate_progress_update_is_not_sent_twice(
        self,
        mock_send_sms,
    ):
        mock_send_sms.return_value = {
            "mode": "dry_run",
            "recipients": [
                {
                    "number": self.customer.phone_number,
                    "status": "DryRun",
                }
            ],
        }

        message = (
            "NetSage: Engineers are continuing to investigate "
            "the network issue affecting Mukono Central. "
            "Ref: INC-1."
        )

        first_notifications = send_report_progress_update(
            self.incident,
            message,
        )

        second_notifications = send_report_progress_update(
            self.incident,
            message,
        )

        self.assertEqual(len(first_notifications), 1)
        self.assertEqual(len(second_notifications), 0)

        self.assertEqual(
            Notification.objects.filter(
                incident=self.incident,
                customer=self.customer,
                message_type=Notification.MessageType.UPDATE,
                message=message,
            ).count(),
            1,
        )

        mock_send_sms.assert_called_once_with(
            message,
            [self.customer.phone_number],
        )

    @patch(
        "api.services.customer_report_updates.send_sms"
    )
    def test_stop_prevents_future_progress_updates(
        self,
        mock_send_sms,
    ):
        self.report.updates_opted_in = False
        self.report.save(update_fields=["updates_opted_in"])

        message = (
            "NetSage: Engineers are continuing to investigate "
            "the network issue affecting Mukono Central. "
            "Ref: INC-1."
        )

        notifications = send_report_progress_update(
            self.incident,
            message,
        )

        self.assertEqual(len(notifications), 0)

        mock_send_sms.assert_not_called()

        self.assertFalse(
            CustomerNetworkReport.objects.get(
                pk=self.report.pk
            ).updates_opted_in
        )

    def test_stop_disables_updates_for_reporting_relationship(self):
        from .services.customer_report_preferences import (
            opt_out_customer_report_updates,
        )

        updated_count = opt_out_customer_report_updates(
            self.customer.phone_number,
        )

        self.assertEqual(updated_count, 1)

        self.report.refresh_from_db()

        self.assertFalse(
            self.report.updates_opted_in
        )

        self.assertEqual(
            self.report.message,
            "Internet is slow.",
        )

        self.assertEqual(
            self.report.customer,
            self.customer,
        )

        self.assertEqual(
            self.report.incident,
            self.incident,
        )

    @patch(
        "api.services.customer_report_updates.send_sms"
    )
    def test_recovery_update_not_sent_before_verification(
        self,
        mock_send_sms,
    ):
        message = (
            "NetSage: Service in Mukono Central has recovered. "
            "Our team is monitoring the connection to confirm "
            "stability. Ref: INC-1."
        )

        notifications = send_report_recovery_update(
            self.incident,
            message,
        )

        self.assertEqual(len(notifications), 0)

        mock_send_sms.assert_not_called()

        self.assertEqual(
            Notification.objects.filter(
                incident=self.incident,
                customer=self.customer,
                message_type=Notification.MessageType.RECOVERY,
            ).count(),
            0,
        )

    @patch(
        "api.services.customer_report_updates.send_sms"
    )
    def test_verified_recovery_sends_recovery_update(
        self,
        mock_send_sms,
    ):
        from django.utils import timezone

        self.incident.status = Incident.Status.MONITORING
        self.incident.recovery_verified_at = timezone.now()
        self.incident.save(
            update_fields=[
                "status",
                "recovery_verified_at",
            ]
        )

        mock_send_sms.return_value = {
            "mode": "dry_run",
            "recipients": [
                {
                    "number": self.customer.phone_number,
                    "status": "DryRun",
                }
            ],
        }

        message = (
            "NetSage: Service in Mukono Central has recovered. "
            "Our team is monitoring the connection to confirm "
            "stability. Ref: INC-1."
        )

        notifications = send_report_recovery_update(
            self.incident,
            message,
        )

        self.assertEqual(len(notifications), 1)

        notification = Notification.objects.get(
            incident=self.incident,
            customer=self.customer,
            message_type=Notification.MessageType.RECOVERY,
        )

        self.assertEqual(
            notification.delivery_status,
            Notification.DeliveryStatus.DRY_RUN,
        )

        mock_send_sms.assert_called_once_with(
            message,
            [self.customer.phone_number],
        )

    @patch(
        "api.services.customer_report_updates.send_sms"
    )
    def test_duplicate_recovery_update_is_not_sent_twice(
        self,
        mock_send_sms,
    ):
        from django.utils import timezone

        self.incident.status = Incident.Status.MONITORING
        self.incident.recovery_verified_at = timezone.now()
        self.incident.save(
            update_fields=[
                "status",
                "recovery_verified_at",
            ]
        )

        mock_send_sms.return_value = {
            "mode": "dry_run",
            "recipients": [
                {
                    "number": self.customer.phone_number,
                    "status": "DryRun",
                }
            ],
        }

        message = (
            "NetSage: Service in Mukono Central has recovered. "
            "Our team is monitoring the connection to confirm "
            "stability. Ref: INC-1."
        )

        first_notifications = send_report_recovery_update(
            self.incident,
            message,
        )

        second_notifications = send_report_recovery_update(
            self.incident,
            message,
        )

        self.assertEqual(len(first_notifications), 1)
        self.assertEqual(len(second_notifications), 0)

        self.assertEqual(
            Notification.objects.filter(
                incident=self.incident,
                customer=self.customer,
                message_type=Notification.MessageType.RECOVERY,
                message=message,
            ).count(),
            1,
        )

        mock_send_sms.assert_called_once_with(
            message,
            [self.customer.phone_number],
        )

    @patch(
        "api.services.customer_report_updates.send_sms"
    )
    def test_progress_update_failure_is_recorded(
        self,
        mock_send_sms,
    ):
        mock_send_sms.side_effect = ValueError(
            "SMS provider unavailable."
        )

        message = (
            "NetSage: Engineers are continuing to investigate "
            "the network issue affecting Mukono Central. "
            "Ref: INC-1."
        )

        notifications = send_report_progress_update(
            self.incident,
            message,
        )

        self.assertEqual(len(notifications), 1)

        notification = notifications[0]

        self.assertEqual(
            notification.delivery_status,
            Notification.DeliveryStatus.FAILED,
        )

        self.assertEqual(
            notification.error_message,
            "SMS provider unavailable.",
        )

    @patch(
        "api.services.customer_report_updates.send_sms"
    )
    def test_resolved_incident_does_not_send_progress_update(
        self,
        mock_send_sms,
    ):
        self.incident.status = Incident.Status.RESOLVED
        self.incident.save(
            update_fields=["status"]
        )

        message = (
            "NetSage: Engineers are continuing to investigate "
            "the network issue affecting Mukono Central. "
            "Ref: INC-1."
        )

        notifications = send_report_progress_update(
            self.incident,
            message,
        )

        self.assertEqual(len(notifications), 0)

        mock_send_sms.assert_not_called()

        self.assertEqual(
            Notification.objects.filter(
                incident=self.incident,
                customer=self.customer,
                message_type=Notification.MessageType.UPDATE,
            ).count(),
            0,
        )
    @patch(
        "api.services.customer_report_updates.send_sms"
    )
    def test_multiple_reports_from_same_customer_send_one_update(
        self,
        mock_send_sms,
    ):
        CustomerNetworkReport.objects.create(
            sender_phone=self.customer.phone_number,
            customer=self.customer,
            site=self.site,
            incident=self.incident,
            message="Internet is very slow.",
            status=CustomerNetworkReport.Status.ACKNOWLEDGED,
            updates_opted_in=True,
        )

        mock_send_sms.return_value = {
            "mode": "dry_run",
            "recipients": [
                {
                    "number": self.customer.phone_number,
                    "status": "DryRun",
                }
            ],
        }

        message = (
            "NetSage: Engineers are continuing to investigate "
            "the network issue affecting Mukono Central. "
            "Ref: INC-1."
        )

        notifications = send_report_progress_update(
            self.incident,
            message,
        )

        self.assertEqual(len(notifications), 1)

        self.assertEqual(
            notifications[0].customer,
            self.customer,
        )

        mock_send_sms.assert_called_once_with(
            message,
            [self.customer.phone_number],
        )