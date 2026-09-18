from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from api.models import Site, Device, TelemetryReading


class Command(BaseCommand):
    help = "Create demo sites, devices and initial simulated readings."

    @transaction.atomic
    def handle(self, *args, **options):
        sites = [
            ("mukono-demo", "Mukono Demo Site", "Mukono, Uganda", [
                ("mukono-router-01", "Mukono Demo Router", "router", 25),
                ("mukono-switch-01", "Mukono Demo Switch", "switch", 12),
            ]),
            ("kampala-demo", "Kampala Demo Site", "Kampala, Uganda", [
                ("kampala-router-01", "Kampala Demo Router", "router", 20),
            ]),
        ]

        for code, name, location, devices in sites:
            site, _ = Site.objects.get_or_create(
                code=code,
                defaults={
                    "name": name,
                    "location": location,
                    "description": "Simulated site for the NetSage demo.",
                    "is_active": True,
                },
            )

            for device_code, device_name, kind, latency in devices:
                device, _ = Device.objects.get_or_create(
                    code=device_code,
                    defaults={
                        "site": site,
                        "name": device_name,
                        "device_type": kind,
                        "is_active": True,
                    },
                )

                if device.site_id != site.pk:
                    raise CommandError(
                        f"{device_code} belongs to another site. "
                        "Demo changes rolled back."
                    )

                if not device.readings.exists():
                    TelemetryReading.objects.create(
                        device=device,
                        is_reachable=True,
                        latency_ms=latency,
                        packet_loss_percent=0,
                        is_simulated=True,
                    )

                self.stdout.write(
                    f"{site.code}: {device.code} "
                    f"(site ID {site.pk}, device ID {device.pk})"
                )

        self.stdout.write(self.style.SUCCESS(
            "Demo setup complete. Existing records preserved."
        ))
