from unittest.mock import patch

from django.test import TestCase

from .models import Customer, CustomerNetworkReport, Incident, Site
from .services.customer_incident_updates import (
    STATUS_MESSAGES,
    notify_customers_of_incident_status,
)


class CustomerIncidentUpdatesTests(TestCase):
    def setUp(self):
        self.site = Site.objects.create(
            name="Test Site",
            site_type="branch",
        )

        self.customer = Customer.objects.create(
            site=self.site,
            name="Test Customer",
            phone_number="+256700000001",
            sms_opt_in=True,
            is_active=True,
        )

        self.incident = Incident.objects.create(
            site=self.site,
            title="Network outage",
            description="Customer reported an outage.",
            status=Incident.Status.OPEN,
        )

        self.report = CustomerNetworkReport.objects.create(
            sender_phone="+256700000001",
            message="My internet is down.",
            customer=self.customer,
            site=self.site,
            incident=self.incident,
            status=CustomerNetworkReport.Status.ACKNOWLEDGED,
        )

    @patch(
        "api.services.customer_incident_updates.send_sms"
    )
    def test_investigating_sends_update(self, mock_send_sms):
        self.incident.status = Incident.Status.INVESTIGATING

        count = notify_customers_of_incident_status(
            self.incident
        )

        self.assertEqual(count, 1)
        mock_send_sms.assert_called_once_with(
            STATUS_MESSAGES[
                Incident.Status.INVESTIGATING
            ],
            ["+256700000001"],
        )

    @patch(
        "api.services.customer_incident_updates.send_sms"
    )
    def test_monitoring_sends_update(self, mock_send_sms):
        self.incident.status = Incident.Status.MONITORING

        count = notify_customers_of_incident_status(
            self.incident
        )

        self.assertEqual(count, 1)
        mock_send_sms.assert_called_once_with(
            STATUS_MESSAGES[
                Incident.Status.MONITORING
            ],
            ["+256700000001"],
        )

    @patch(
        "api.services.customer_incident_updates.send_sms"
    )
    def test_resolved_sends_update(self, mock_send_sms):
        self.incident.status = Incident.Status.RESOLVED

        count = notify_customers_of_incident_status(
            self.incident
        )

        self.assertEqual(count, 1)
        mock_send_sms.assert_called_once_with(
            STATUS_MESSAGES[
                Incident.Status.RESOLVED
            ],
            ["+256700000001"],
        )

    @patch(
        "api.services.customer_incident_updates.send_sms"
    )
    def test_open_status_does_not_send_update(
        self,
        mock_send_sms,
    ):
        count = notify_customers_of_incident_status(
            self.incident
        )

        self.assertEqual(count, 0)
        mock_send_sms.assert_not_called()

    @patch(
        "api.services.customer_incident_updates.send_sms"
    )
    def test_inactive_or_opted_out_customers_do_not_receive_updates(
        self,
        mock_send_sms,
    ):
        self.customer.is_active = False
        self.customer.save(update_fields=["is_active"])

        count = notify_customers_of_incident_status(
            self.incident
        )

        self.assertEqual(count, 0)
        mock_send_sms.assert_not_called()

    @patch(
        "api.services.customer_incident_updates.send_sms"
    )
    def test_duplicate_reporter_numbers_are_sent_once(
        self,
        mock_send_sms,
    ):
        CustomerNetworkReport.objects.create(
            sender_phone="+256700000001",
            message="Another report from the same customer.",
            customer=self.customer,
            site=self.site,
            incident=self.incident,
            status=CustomerNetworkReport.Status.ACKNOWLEDGED,
        )

        self.incident.status = Incident.Status.INVESTIGATING

        count = notify_customers_of_incident_status(
            self.incident
        )

        self.assertEqual(count, 1)
        mock_send_sms.assert_called_once_with(
            STATUS_MESSAGES[
                Incident.Status.INVESTIGATING
            ],
            ["+256700000001"],
        )
