from django.core.management import call_command
from django.test import TestCase

from .models import Alert, Device, Incident, Site, TelemetryReading
from .services.simulator_adapter import run_simulator_scenario


SIMULATOR_SITE_CODES = {
    "site-mukono-central",
    "site-ucu-area",
    "site-seeta",
}


class SimulatorIntegrationTests(TestCase):
    def simulator_readings(self):
        return TelemetryReading.objects.filter(
            device__site__code__in=SIMULATOR_SITE_CODES,
            is_simulated=True,
        )

    def test_shared_uplink_scenario_persists_full_demo(self):
        result = run_simulator_scenario(
            "mukono-uplink-fault",
        )

        self.assertEqual(result.sites, 3)
        self.assertEqual(result.devices, 3)
        self.assertEqual(result.readings, 108)
        self.assertEqual(result.alerts, 3)
        self.assertEqual(result.incidents, 1)

        self.assertEqual(
            Site.objects.filter(
                code__in=SIMULATOR_SITE_CODES,
            ).count(),
            3,
        )

        self.assertEqual(
            Device.objects.filter(
                site__code__in=SIMULATOR_SITE_CODES,
            ).count(),
            3,
        )

        self.assertEqual(
            self.simulator_readings().count(),
            108,
        )

        self.assertEqual(
            Alert.objects.filter(
                device__site__code__in=SIMULATOR_SITE_CODES,
            ).count(),
            3,
        )

        incident = Incident.objects.get(
            shared_dependency="uplink-mukono",
        )

        self.assertEqual(
            set(
                incident.affected_sites.values_list(
                    "code",
                    flat=True,
                )
            ),
            SIMULATOR_SITE_CODES,
        )

        self.assertEqual(
            incident.alerts.count(),
            3,
        )

        self.assertTrue(incident.probable_cause)
        self.assertTrue(incident.confidence_note)

    def test_scenario_reset_makes_rehearsal_repeatable(self):
        run_simulator_scenario(
            "mukono-uplink-fault",
        )
        run_simulator_scenario(
            "mukono-uplink-fault",
        )

        self.assertEqual(
            self.simulator_readings().count(),
            108,
        )

        self.assertEqual(
            Alert.objects.filter(
                device__site__code__in=SIMULATOR_SITE_CODES,
            ).count(),
            3,
        )

        self.assertEqual(
            Incident.objects.filter(
                shared_dependency="uplink-mukono",
            ).count(),
            1,
        )

    def test_short_blip_does_not_create_false_incident(self):
        result = run_simulator_scenario(
            "single-site-blip",
        )

        self.assertEqual(result.readings, 66)
        self.assertEqual(result.alerts, 0)
        self.assertEqual(result.incidents, 0)

    def test_management_command_runs_scenario(self):
        call_command(
            "run_demo_scenario",
            scenario="mukono-uplink-fault",
        )

        self.assertEqual(
            Incident.objects.filter(
                shared_dependency="uplink-mukono",
            ).count(),
            1,
        )
