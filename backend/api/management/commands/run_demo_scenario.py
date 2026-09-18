from django.core.management.base import BaseCommand

from api.services.simulator_adapter import (
    available_scenarios,
    run_simulator_scenario,
)


class Command(BaseCommand):
    help = (
        "Run a NetSage simulator scenario and persist its "
        "telemetry, alerts and incidents."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--scenario",
            choices=available_scenarios(),
            default="mukono-uplink-fault",
        )
        parser.add_argument(
            "--no-reset",
            action="store_true",
            help=(
                "Keep existing simulator records instead of "
                "resetting the dedicated demo sites first."
            ),
        )

    def handle(self, *args, **options):
        result = run_simulator_scenario(
            options["scenario"],
            reset=not options["no_reset"],
        )

        self.stdout.write(
            self.style.SUCCESS(
                "NetSage demo scenario complete."
            )
        )
        self.stdout.write(
            f"Scenario: {result.scenario}"
        )
        self.stdout.write(
            f"Sites: {result.sites}"
        )
        self.stdout.write(
            f"Devices: {result.devices}"
        )
        self.stdout.write(
            f"Telemetry readings: {result.readings}"
        )
        self.stdout.write(
            f"Alerts: {result.alerts}"
        )
        self.stdout.write(
            f"Incidents: {result.incidents}"
        )
