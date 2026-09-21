from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from api.models import Device, Site, TelemetryReading
from api.services.predictive_risk import analyse_site_risk


class Command(BaseCommand):
    help = (
        "Create worsening but still reachable telemetry for "
        "Mukono Central to demonstrate predictive warning."
    )

    def handle(self, *args, **options):
        site = Site.objects.filter(
            name="Mukono Central",
        ).first()

        if site is None:
            self.stderr.write(
                self.style.ERROR(
                    "Mukono Central was not found. "
                    "Run seed_demo first."
                )
            )
            return

        device = Device.objects.filter(
            site=site,
            is_active=True,
        ).first()

        if device is None:
            self.stderr.write(
                self.style.ERROR(
                    "No active device was found for "
                    "Mukono Central."
                )
            )
            return

        now = timezone.now()

        telemetry = [
            (45.0, 0.8),
            (58.0, 1.2),
            (72.0, 1.8),
            (88.0, 2.4),
            (105.0, 3.1),
            (121.0, 3.8),
            (137.0, 4.4),
            (145.0, 4.8),
        ]

        for index, (latency, loss) in enumerate(
            telemetry
        ):
            TelemetryReading.objects.create(
                device=device,
                recorded_at=(
                    now
                    - timedelta(
                        minutes=(
                            len(telemetry) - index
                        )
                    )
                ),
                is_reachable=True,
                latency_ms=latency,
                packet_loss_percent=loss,
                is_simulated=True,
            )

        result = analyse_site_risk(site)

        self.stdout.write(
            self.style.SUCCESS(
                "Predictive warning telemetry created."
            )
        )

        self.stdout.write(
            f"Site: {result['site_name']}"
        )

        self.stdout.write(
            f"Risk score: "
            f"{result['risk_score']}/100"
        )

        self.stdout.write(
            f"Risk level: "
            f"{result['risk_level']}"
        )

        self.stdout.write(
            f"Predicted failure: "
            f"{result['predicted_failure']}"
        )

        self.stdout.write(
            "Reasons:"
        )

        for reason in result["reasons"]:
            self.stdout.write(
                f"  - {reason}"
            )

        self.stdout.write(
            "Recommended action: "
            f"{result['recommended_action']}"
        )