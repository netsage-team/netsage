import re

import africastalking
from africastalking.Service import AfricasTalkingException
from django.conf import settings


PHONE_PATTERN = re.compile(r"^\+[1-9][0-9]{7,14}$")


class SmsConfigurationError(Exception):
    """Raised when SMS configuration is unsafe or incomplete."""


class SmsRecipientError(Exception):
    """Raised when a requested recipient is not permitted."""


def _clean_recipients(recipients):
    cleaned = []

    for value in recipients:
        phone = str(value).strip()

        if not PHONE_PATTERN.fullmatch(phone):
            raise SmsRecipientError(
                f"Invalid international phone number: {phone}"
            )

        if phone not in cleaned:
            cleaned.append(phone)

    if not cleaned:
        raise SmsRecipientError(
            "At least one recipient is required."
        )

    return cleaned


def send_sms(message, recipients):
    """
    Send an SMS through the configured NetSage messaging mode.

    dry_run:
        Never contacts an external provider.

    sandbox:
        Uses Africa's Talking sandbox and permits only explicitly
        allowlisted test recipients.
    """
    message = str(message).strip()

    if not message:
        raise ValueError("SMS message cannot be empty.")

    recipients = _clean_recipients(recipients)

    mode = settings.NETSAGE_SMS_MODE

    if mode == "dry_run":
        return {
            "mode": "dry_run",
            "provider_message": (
                "Dry run only. No SMS was submitted."
            ),
            "recipients": [
                {
                    "number": phone,
                    "status": "DryRun",
                    "statusCode": 0,
                    "messageId": f"dryrun-{index}",
                    "cost": "UGX 0",
                }
                for index, phone in enumerate(
                    recipients,
                    start=1,
                )
            ],
        }

    if mode != "sandbox":
        raise SmsConfigurationError(
            "NetSage currently permits only dry_run or sandbox SMS mode."
        )

    username = settings.AFRICASTALKING_USERNAME
    api_key = settings.AFRICASTALKING_API_KEY

    if username != "sandbox":
        raise SmsConfigurationError(
            "Sandbox mode requires AFRICASTALKING_USERNAME=sandbox."
        )

    if not api_key:
        raise SmsConfigurationError(
            "Africa's Talking sandbox API key is not configured."
        )

    allowed = set(
        settings.AFRICASTALKING_TEST_RECIPIENTS
    )

    if not allowed:
        raise SmsConfigurationError(
            "Configure at least one test recipient before sandbox sending."
        )

    blocked = [
        phone
        for phone in recipients
        if phone not in allowed
    ]

    if blocked:
        raise SmsRecipientError(
            "Sandbox sending blocked for non-allowlisted recipient(s): "
            + ", ".join(blocked)
        )

    africastalking.initialize(
        username,
        api_key,
    )

    sms = africastalking.SMS

    sender_id = (
        settings.AFRICASTALKING_SENDER_ID
        or None
    )

    try:
        response = sms.send(
            message,
            recipients,
            sender_id=sender_id,
        )
    except AfricasTalkingException as exc:
        message_text = str(exc)

        if "authentication is invalid" in message_text.lower():
            raise SmsConfigurationError(
                "Africa's Talking rejected the sandbox credentials. "
                "Confirm that the API key was generated from the "
                "Sandbox dashboard and try again."
            ) from exc

        raise SmsConfigurationError(
            f"Africa's Talking sandbox request failed: {message_text}"
        ) from exc

    return {
        "mode": "sandbox",
        "provider_message": (
            response.get(
                "SMSMessageData",
                {},
            ).get("Message", "")
        ),
        "recipients": (
            response.get(
                "SMSMessageData",
                {},
            ).get("Recipients", [])
        ),
        "raw": response,
    }
