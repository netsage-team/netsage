from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase

from .models import Incident, IncidentEvent, Site
from .services.simulator_adapter import run_simulator_scenario


User = get_user_model()


class IncidentTimelineTests(APITestCase):
    def setUp(self):
        self.operator = User.objects.create_user(
            username="operator",
            password="test-password-only",
            is_staff=True,
        )

        self.engineer = User.objects.create_user(
            username="engineer",
            password="test-password-only",
            is_staff=True,
        )

        self.site = Site.objects.create(
            name="Timeline Test Site",
            code="timeline-test-site",
            location="Mukono",
        )

        self.incident = Incident.objects.create(
            site=self.site,
            title="Timeline test incident",
        )

        self.client.force_authenticate(
            user=self.operator,
        )

    def test_assignment_and_investigation_are_recorded(self):
        response = self.client.patch(
            reverse(
                "incident-manage",
                args=[self.incident.pk],
            ),
            {
                "assigned_to": self.engineer.pk,
                "status": "investigating",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
            response.data,
        )

        events = list(
            self.incident.timeline.values_list(
                "event_type",
                flat=True,
            )
        )

        self.assertIn(
            IncidentEvent.EventType.ASSIGNMENT,
            events,
        )
        self.assertIn(
            IncidentEvent.EventType.STATUS,
            events,
        )

        self.incident.refresh_from_db()
        self.assertEqual(
            self.incident.assigned_to_id,
            self.engineer.pk,
        )
        self.assertEqual(
            self.incident.status,
            Incident.Status.INVESTIGATING,
        )

    def test_staff_can_add_investigation_note(self):
        response = self.client.post(
            reverse(
                "incident-notes",
                args=[self.incident.pk],
            ),
            {
                "note": (
                    "Checking the Mukono uplink and "
                    "upstream connectivity."
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201,
            response.data,
        )

        event = self.incident.timeline.get()

        self.assertEqual(
            event.event_type,
            IncidentEvent.EventType.NOTE,
        )
        self.assertEqual(
            event.actor_id,
            self.operator.pk,
        )
        self.assertIn(
            "Mukono uplink",
            event.message,
        )

    def test_empty_note_is_rejected(self):
        response = self.client.post(
            reverse(
                "incident-notes",
                args=[self.incident.pk],
            ),
            {"note": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            IncidentEvent.objects.exists()
        )


class SimulatorIncidentTimelineTests(APITestCase):
    def test_simulator_creates_detected_event(self):
        run_simulator_scenario(
            "mukono-uplink-fault",
        )

        incident = Incident.objects.get(
            shared_dependency="uplink-mukono",
        )

        event = incident.timeline.get()

        self.assertEqual(
            event.event_type,
            IncidentEvent.EventType.DETECTED,
        )
        self.assertIsNone(event.actor)


class IncidentRecoveryWorkflowTests(APITestCase):
    def setUp(self):
        self.operator = User.objects.create_user(
            username="recovery-engineer",
            password="test-password-only",
            is_staff=True,
        )

        self.client.force_authenticate(
            user=self.operator,
        )

        run_simulator_scenario(
            "mukono-uplink-fault",
        )

        self.incident = Incident.objects.get(
            shared_dependency="uplink-mukono",
        )

        self.incident.assigned_to = self.operator
        self.incident.status = Incident.Status.INVESTIGATING
        self.incident.save(
            update_fields=[
                "assigned_to",
                "status",
                "updated_at",
            ]
        )

    def test_sustained_recovery_moves_incident_to_monitoring(self):
        response = self.client.post(
            reverse(
                "incident-verify-recovery",
                args=[self.incident.pk],
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
            response.data,
        )

        self.incident.refresh_from_db()

        self.assertEqual(
            self.incident.status,
            Incident.Status.MONITORING,
        )

        self.assertIsNotNone(
            self.incident.recovery_verified_at
        )

        self.assertTrue(
            self.incident.timeline.filter(
                event_type=IncidentEvent.EventType.RECOVERY,
            ).exists()
        )

        self.assertTrue(
            response.data["recovery"]["recovered"]
        )

    def test_resolving_monitoring_incident_clears_alerts(self):
        verify_response = self.client.post(
            reverse(
                "incident-verify-recovery",
                args=[self.incident.pk],
            ),
            {},
            format="json",
        )

        self.assertEqual(
            verify_response.status_code,
            200,
            verify_response.data,
        )

        response = self.client.post(
            reverse(
                "incident-resolve-incident",
                args=[self.incident.pk],
            ),
            {
                "resolution_notes": (
                    "Shared uplink recovered and remained "
                    "healthy during the monitoring window."
                )
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200,
            response.data,
        )

        self.incident.refresh_from_db()

        self.assertEqual(
            self.incident.status,
            Incident.Status.RESOLVED,
        )

        self.assertIsNotNone(
            self.incident.resolved_at
        )

        self.assertFalse(
            self.incident.alerts.filter(
                cleared_at__isnull=True,
            ).exists()
        )

        self.assertTrue(
            self.incident.timeline.filter(
                event_type=IncidentEvent.EventType.RESOLVED,
            ).exists()
        )

    def test_incident_cannot_resolve_before_recovery_monitoring(self):
        response = self.client.post(
            reverse(
                "incident-resolve-incident",
                args=[self.incident.pk],
            ),
            {
                "resolution_notes": (
                    "Attempting premature resolution."
                )
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.incident.refresh_from_db()

        self.assertEqual(
            self.incident.status,
            Incident.Status.INVESTIGATING,
        )
