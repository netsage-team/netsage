from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from api.models import Customer, Site


DEMO_CUSTOMERS = {
    "site-mukono-central": [
        {
            "name": "Mukono Demo Customer A",
            "phone_number": "+256700100001",
            "sms_opt_in": True,
            "is_active": True,
        },
        {
            "name": "Mukono Demo Customer B",
            "phone_number": "+256700100002",
            "sms_opt_in": True,
            "is_active": True,
        },
    ],
    "site-ucu-area": [
        {
            "name": "UCU Demo Customer A",
            "phone_number": "+256700200001",
            "sms_opt_in": True,
            "is_active": True,
        },
        {
            "name": "UCU Demo Customer B",
            "phone_number": "+256700200002",
            "sms_opt_in": True,
            "is_active": True,
        },
    ],
    "site-seeta": [
        {
            "name": "Seeta Demo Customer A",
            "phone_number": "+256700300001",
            "sms_opt_in": True,
            "is_active": True,
        },
        {
            "name": "Seeta Demo Customer B",
            "phone_number": "+256700300002",
            "sms_opt_in": True,
            "is_active": True,
        },
        {
            "name": "Seeta Inactive Demo Customer",
            "phone_number": "+256700300003",
            "sms_opt_in": True,
            "is_active": False,
        },
    ],
}


class Command(BaseCommand):
    help = (
        "Create repeatable fictional customers for the "
        "NetSage notification demo."
    )

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for site_code, customers in DEMO_CUSTOMERS.items():
            try:
                site = Site.objects.get(
                    code=site_code,
                )
            except Site.DoesNotExist as exc:
                raise CommandError(
                    f"Missing demo site {site_code}. "
                    "Run the network demo scenario first."
                ) from exc

            for values in customers:
                customer, created = (
                    Customer.objects.update_or_create(
                        site=site,
                        phone_number=(
                            values["phone_number"]
                        ),
                        defaults={
                            "name": values["name"],
                            "sms_opt_in": (
                                values["sms_opt_in"]
                            ),
                            "is_active": (
                                values["is_active"]
                            ),
                        },
                    )
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

                self.stdout.write(
                    f"{site.name}: "
                    f"{customer.name} "
                    f"(opt-in={customer.sms_opt_in}, "
                    f"active={customer.is_active})"
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Notification demo customers ready. "
                f"Created: {created_count}; "
                f"updated: {updated_count}."
            )
        )
