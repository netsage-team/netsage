from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APITestCase

from .models import (
    Alert,
    Customer,
    CustomerNetworkReport,
    Device,
    Incident,
    Site,
)


User = get_user_model()


class OperationsAPITests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="operator",
            password="test-password-only",
            is_staff=True,
        )

        self.viewer = User.objects.create_user(
            username="viewer",
            password="test-password-only",
        )

        self.site = Site.objects.create(
            name="Test Mukono",
            code="test-mukono",
            location="Mukono",
        )

        self.other_site = Site.objects.create(
            name="Test Kampala",
            code="test-kampala",
            location="Kampala",
        )

        self.device = Device.objects.create(
            site=self.site,
            name="Test Router",
            code="test-router",
        )

        self.incident = Incident.objects.create(
            site=self.site,
            title="Test uplink issue",
            severity="critical",
        )

        self.other_incident = Incident.objects.create(
            site=self.other_site,
            title="Other site issue",
        )

        self.alert = Alert.objects.create(
            device=self.device,
            incident=self.incident,
            alert_type="device_down",
            severity="critical",
            message="Simulated unreachable device",
        )

        self.client.force_authenticate(user=self.staff)

    def manage_url(self):
        return reverse(
            "incident-manage",
            args=[self.incident.pk],
        )

    def test_anonymous_access_is_blocked(self):
        self.client.force_authenticate(user=None)

        endpoint_names = [
            "incident-list",
            "alert-list",
            "engineer-list",
            "dashboard-summary",
        ]

        for name in endpoint_names:
            with self.subTest(endpoint=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 403)

    def test_nonstaff_cannot_manage_incident(self):
        self.client.force_authenticate(user=self.viewer)

        response = self.client.patch(
            self.manage_url(),
            {"status": "investigating"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, "open")

    def test_staff_can_assign_and_investigate(self):
        response = self.client.patch(
            self.manage_url(),
            {
                "assigned_to": self.staff.pk,
                "status": "investigating",
                "resolution_notes": "Checking the uplink.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200, response.data)

        self.incident.refresh_from_db()

        self.assertEqual(
            self.incident.assigned_to_id,
            self.staff.pk,
        )
        self.assertEqual(
            self.incident.status,
            "investigating",
        )
        self.assertEqual(
            self.incident.resolution_notes,
            "Checking the uplink.",
        )

    def test_nonstaff_cannot_be_assigned(self):
        response = self.client.patch(
            self.manage_url(),
            {"assigned_to": self.viewer.pk},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.incident.refresh_from_db()
        self.assertIsNone(self.incident.assigned_to_id)

    def test_manual_resolution_is_rejected(self):
        response = self.client.patch(
            self.manage_url(),
            {"status": "resolved"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, "open")
        self.assertIsNone(self.incident.resolved_at)

    def test_recovery_timestamp_cannot_be_forged(self):
        response = self.client.patch(
            self.manage_url(),
            {
                "recovery_verified_at": timezone.now().isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.incident.refresh_from_db()
        self.assertIsNone(self.incident.recovery_verified_at)

    def test_monitoring_cannot_return_to_investigating(self):
        self.incident.status = "monitoring"
        self.incident.save()

        response = self.client.patch(
            self.manage_url(),
            {"status": "investigating"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, "monitoring")

    def test_incident_site_filter(self):
        response = self.client.get(
            reverse("incident-list"),
            {"site": self.site.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["id"],
            self.incident.pk,
        )

    def test_invalid_filter_returns_400(self):
        response = self.client.get(
            reverse("incident-list"),
            {"site": "invalid"},
        )

        self.assertEqual(response.status_code, 400)

    def test_cleared_alert_filter(self):
        response = self.client.get(
            reverse("alert-list"),
            {"cleared": "false"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

        self.alert.cleared_at = timezone.now()
        self.alert.save()

        response = self.client.get(
            reverse("alert-list"),
            {"cleared": "false"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

        response = self.client.get(
            reverse("alert-list"),
            {"cleared": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_dashboard_summary_is_scoped_to_site(self):
        response = self.client.get(
            reverse("dashboard-summary"),
            {"site": self.site.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["sites_total"], 1)
        self.assertEqual(response.data["devices_total"], 1)
        self.assertEqual(response.data["incidents_active"], 1)
        self.assertEqual(response.data["incidents_unassigned"], 1)
        self.assertEqual(response.data["alerts_critical"], 1)
        self.assertEqual(
            response.data["incidents_by_status"]["open"],
            1,
        )

    def test_engineer_list_excludes_nonstaff(self):
        response = self.client.get(reverse("engineer-list"))

        self.assertEqual(response.status_code, 200)

        engineer_ids = [
            item["id"]
            for item in response.data["results"]
        ]

        self.assertIn(self.staff.pk, engineer_ids)
        self.assertNotIn(self.viewer.pk, engineer_ids)

class CustomerReportsAPITests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username="reports-operator",
            password="test-password-only",
            is_staff=True,
        )

        self.viewer = User.objects.create_user(
            username="reports-viewer",
            password="test-password-only",
        )

        self.site = Site.objects.create(
            name="Reports Mukono",
            code="reports-mukono",
            location="Mukono",
            site_type=Site.SiteType.TOWER,
        )

        self.customer = Customer.objects.create(
            site=self.site,
            name="Reports Customer",
            phone_number="+256700123456",
            sms_opt_in=True,
            is_active=True,
        )

        self.incident = Incident.objects.create(
            site=self.site,
            title="Reports network outage",
            status=Incident.Status.OPEN,
        )

        self.report = CustomerNetworkReport.objects.create(
            sender_phone=self.customer.phone_number,
            customer=self.customer,
            site=self.site,
            incident=self.incident,
            message="Internet is not working.",
            status=CustomerNetworkReport.Status.MATCHED,
        )

        self.client.force_authenticate(user=self.staff)

    def test_staff_can_list_customer_reports(self):
        response = self.client.get(
            reverse("customer-report-list")
        )

        self.assertEqual(
            response.status_code,
            200,
            response.data,
        )

    def test_anonymous_access_is_blocked(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(
            reverse("customer-report-list")
        )

        self.assertEqual(response.status_code, 403)

    def test_nonstaff_access_is_blocked(self):
        self.client.force_authenticate(user=self.viewer)

        response = self.client.get(
            reverse("customer-report-list")
        )

        self.assertEqual(response.status_code, 403)

    def test_customer_report_serializes_masked_sender_and_context(self):
        response = self.client.get(
            reverse("customer-report-list")
        )

        self.assertEqual(response.status_code, 200, response.data)

        report = response.data["results"][0]

        self.assertEqual(report["masked_sender"], "+256******456")
        self.assertEqual(report["customer_name"], "Reports Customer")
        self.assertEqual(report["site_id"], self.site.id)
        self.assertEqual(report["site_name"], "Reports Mukono")
        self.assertEqual(report["site_type"], "tower")
        self.assertEqual(report["incident_id"], self.incident.id)
        self.assertEqual(report["incident_status"], "open")
        self.assertEqual(report["message"], "Internet is not working.")
        self.assertEqual(report["report_status"], "matched")
        self.assertEqual(report["acknowledgement_status"], "not_acknowledged")
        self.assertNotIn(self.customer.phone_number, str(report))

    def test_unknown_sender_is_safe(self):
        report = CustomerNetworkReport.objects.create(
            sender_phone="+256701987654",
            message="No internet at my location.",
            status=CustomerNetworkReport.Status.RECEIVED,
        )

        response = self.client.get(
            reverse("customer-report-list")
        )

        self.assertEqual(response.status_code, 200, response.data)

        reports = response.data["results"]
        unknown_report = next(
            item for item in reports
            if item["id"] == report.id
        )

        self.assertEqual(
            unknown_report["masked_sender"],
            "+256******654",
        )
        self.assertIsNone(unknown_report["customer_name"])
        self.assertIsNone(unknown_report["site_id"])
        self.assertIsNone(unknown_report["site_name"])
        self.assertIsNone(unknown_report["incident_id"])
        self.assertEqual(
            unknown_report["report_status"],
            "received",
        )
        self.assertNotIn(
            report.sender_phone,
            str(unknown_report),
        )
    def test_customer_reports_are_newest_first(self):
        older_report = CustomerNetworkReport.objects.create(
            sender_phone="+256701111111",
            message="Older network report.",
            status=CustomerNetworkReport.Status.RECEIVED,
        )

        newer_report = CustomerNetworkReport.objects.create(
            sender_phone="+256702222222",
            message="Newer network report.",
            status=CustomerNetworkReport.Status.RECEIVED,
        )

        response = self.client.get(
            reverse("customer-report-list")
        )

        self.assertEqual(response.status_code, 200, response.data)

        reports = response.data["results"]

        self.assertEqual(reports[0]["id"], newer_report.id)
        self.assertEqual(reports[1]["id"], older_report.id)