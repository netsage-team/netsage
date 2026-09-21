from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase

from .models import Site


User = get_user_model()


class SiteTypeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tower-test-user",
            password="test-password-only",
        )
        self.client.force_authenticate(user=self.user)

    def test_site_defaults_to_other(self):
        site = Site.objects.create(
            name="Generic Site",
            code="generic-site",
            location="Uganda",
        )

        self.assertEqual(
            site.site_type,
            Site.SiteType.OTHER,
        )

    def test_site_api_exposes_tower_type_and_label(self):
        site = Site.objects.create(
            name="Mukono Tower Test",
            code="mukono-tower-test",
            site_type=Site.SiteType.TOWER,
            location="Mukono, Uganda",
        )

        response = self.client.get(
            reverse("site-list"),
            {"page_size": 200},
        )

        self.assertEqual(response.status_code, 200)

        row = next(
            item
            for item in response.data["results"]
            if item["id"] == site.id
        )

        self.assertEqual(row["site_type"], "tower")
        self.assertEqual(row["site_type_label"], "Tower")
