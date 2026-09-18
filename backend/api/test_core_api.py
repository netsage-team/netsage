from django.contrib.auth import get_user_model
from django.core.management import call_command

from rest_framework.test import APITestCase

from .models import Device, Site, TelemetryReading


User = get_user_model()


class CoreAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="core-api-tester",
            password="test-password-only",
            is_staff=True,
        )

        self.mukono = Site.objects.create(
            name="Test Mukono",
            code="core-mukono",
            location="Mukono",
        )

        self.kampala = Site.objects.create(
            name="Test Kampala",
            code="core-kampala",
            location="Kampala",
        )

        self.router = Device.objects.create(
            site=self.mukono,
            name="Mukono Router",
            code="core-router",
        )

        self.switch = Device.objects.create(
            site=self.kampala,
            name="Kampala Switch",
            code="core-switch",
        )

        self.router_reading = TelemetryReading.objects.create(
            device=self.router,
            is_reachable=True,
            latency_ms=25,
            packet_loss_percent=0,
            is_simulated=True,
        )

        self.switch_reading = TelemetryReading.objects.create(
            device=self.switch,
            is_reachable=True,
            latency_ms=40,
            packet_loss_percent=1,
            is_simulated=True,
        )

    def authenticate(self):
        self.client.force_authenticate(user=self.user)

    def test_sites_require_authentication(self):
        response = self.client.get("/api/sites/")
        self.assertEqual(response.status_code, 403)

    def test_devices_require_authentication(self):
        response = self.client.get("/api/devices/")
        self.assertEqual(response.status_code, 403)

    def test_telemetry_requires_authentication(self):
        response = self.client.get("/api/telemetry/")
        self.assertEqual(response.status_code, 403)

    def test_authenticated_user_can_list_sites(self):
        self.authenticate()

        response = self.client.get("/api/sites/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_authenticated_user_can_list_devices(self):
        self.authenticate()

        response = self.client.get("/api/devices/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 2)

    def test_telemetry_can_filter_by_device(self):
        self.authenticate()

        response = self.client.get(
            "/api/telemetry/",
            {"device": self.router.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_telemetry_can_filter_by_site(self):
        self.authenticate()

        response = self.client.get(
            "/api/telemetry/",
            {"site": self.kampala.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)

    def test_invalid_telemetry_filter_returns_400(self):
        self.authenticate()

        response = self.client.get(
            "/api/telemetry/",
            {"site": "not-an-id"},
        )

        self.assertEqual(response.status_code, 400)


class DemoSeedTests(APITestCase):
    def test_seed_demo_is_repeatable(self):
        call_command("seed_demo")

        self.assertEqual(
            Site.objects.filter(
                code__in=["mukono-demo", "kampala-demo"]
            ).count(),
            2,
        )

        self.assertEqual(
            Device.objects.filter(
                code__in=[
                    "mukono-router-01",
                    "mukono-switch-01",
                    "kampala-router-01",
                ]
            ).count(),
            3,
        )

        call_command("seed_demo")

        self.assertEqual(
            Site.objects.filter(
                code__in=["mukono-demo", "kampala-demo"]
            ).count(),
            2,
        )

        self.assertEqual(
            Device.objects.filter(
                code__in=[
                    "mukono-router-01",
                    "mukono-switch-01",
                    "kampala-router-01",
                ]
            ).count(),
            3,
        )
