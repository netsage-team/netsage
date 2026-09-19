from django.test import SimpleTestCase, override_settings

from .services.sms import (
    SmsConfigurationError,
    SmsRecipientError,
    send_sms,
)


class SmsServiceTests(SimpleTestCase):
    @override_settings(
        NETSAGE_SMS_MODE="dry_run",
        AFRICASTALKING_USERNAME="sandbox",
        AFRICASTALKING_API_KEY="",
        AFRICASTALKING_TEST_RECIPIENTS=[],
    )
    def test_dry_run_never_requires_provider_credentials(self):
        result = send_sms(
            "NetSage test message.",
            ["+256700000001"],
        )

        self.assertEqual(
            result["mode"],
            "dry_run",
        )
        self.assertEqual(
            result["recipients"][0]["status"],
            "DryRun",
        )

    @override_settings(
        NETSAGE_SMS_MODE="sandbox",
        AFRICASTALKING_USERNAME="sandbox",
        AFRICASTALKING_API_KEY="",
        AFRICASTALKING_TEST_RECIPIENTS=[
            "+256700000001",
        ],
    )
    def test_sandbox_requires_api_key(self):
        with self.assertRaises(
            SmsConfigurationError
        ):
            send_sms(
                "NetSage test message.",
                ["+256700000001"],
            )

    @override_settings(
        NETSAGE_SMS_MODE="sandbox",
        AFRICASTALKING_USERNAME="sandbox",
        AFRICASTALKING_API_KEY="test-key",
        AFRICASTALKING_TEST_RECIPIENTS=[
            "+256700000001",
        ],
    )
    def test_sandbox_blocks_recipient_not_on_allowlist(self):
        with self.assertRaises(
            SmsRecipientError
        ):
            send_sms(
                "NetSage test message.",
                ["+256700000002"],
            )

    @override_settings(
        NETSAGE_SMS_MODE="dry_run",
    )
    def test_invalid_phone_number_is_rejected(self):
        with self.assertRaises(
            SmsRecipientError
        ):
            send_sms(
                "NetSage test message.",
                ["0700000001"],
            )

    @override_settings(
        NETSAGE_SMS_MODE="dry_run",
    )
    def test_empty_message_is_rejected(self):
        with self.assertRaises(ValueError):
            send_sms(
                "   ",
                ["+256700000001"],
            )
