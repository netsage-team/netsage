from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Incident, Site

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
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
            name="Auth Test Site",
            code="auth-test-site",
            location="Mukono",
        )
        self.incident = Incident.objects.create(
            site=self.site,
            title="Auth test incident",
        )

    def get_csrf_token(self):
        response = self.client.get(reverse("auth-csrf"))
        self.assertEqual(response.status_code, 200)
        return response.json()["csrfToken"]

    def login_as(self, username="operator", password="test-password-only"):
        return self.client.post(
            reverse("auth-login"),
            {"username": username, "password": password},
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.get_csrf_token(),
        )

    def test_login_requires_csrf(self):
        response = self.client.post(
            reverse("auth-login"),
            {"username": "operator", "password": "test-password-only"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_login_session_and_logout(self):
        response = self.login_as()
        self.assertEqual(response.status_code, 200)
        token = response.json()["csrfToken"]

        response = self.client.get(reverse("auth-me"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["id"], self.staff.pk)

        response = self.client.get(reverse("dashboard-summary"))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse("auth-logout"),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.client.get(reverse("auth-me")).status_code, 401
        )
        self.assertEqual(
            self.client.get(reverse("dashboard-summary")).status_code, 403
        )

    def test_wrong_password_is_rejected(self):
        response = self.login_as(password="wrong-password")
        self.assertEqual(response.status_code, 401)

    def test_nonstaff_login_is_rejected(self):
        response = self.login_as(username="viewer")
        self.assertEqual(response.status_code, 403)

    def test_inactive_account_is_rejected(self):
        self.staff.is_active = False
        self.staff.save()
        response = self.login_as()
        self.assertEqual(response.status_code, 401)

    def test_incident_update_requires_csrf(self):
        response = self.login_as()
        self.assertEqual(response.status_code, 200)
        token = response.json()["csrfToken"]
        url = reverse("incident-manage", args=[self.incident.pk])

        response = self.client.patch(
            url,
            {"status": "investigating"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.patch(
            url,
            {"status": "investigating"},
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, 200)
        self.incident.refresh_from_db()
        self.assertEqual(self.incident.status, "investigating")

    def test_untrusted_origin_is_rejected(self):
        response = self.client.post(
            reverse("auth-login"),
            {"username": "operator", "password": "test-password-only"},
            content_type="application/json",
            HTTP_X_CSRFTOKEN=self.get_csrf_token(),
            HTTP_ORIGIN="https://untrusted.example",
        )
        self.assertEqual(response.status_code, 403)
