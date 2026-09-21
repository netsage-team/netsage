from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Customer, Incident, Notification
from .services.sms import (
    SmsConfigurationError,
    SmsRecipientError,
    send_sms,
)

from .notification_serializers import (
    NotificationApprovalSerializer,
    NotificationDraftSerializer,
)


def affected_sites_for(incident):
    sites = list(
        incident.affected_sites.all().order_by("name")
    )

    if not sites:
        sites = [incident.site]

    return sites


def eligible_customers_for(incident):
    sites = affected_sites_for(incident)

    return (
        Customer.objects.filter(
            site__in=sites,
            is_active=True,
            sms_opt_in=True,
        )
        .select_related("site")
        .order_by("site__name", "name", "id")
    )


def mask_phone(phone):
    if len(phone) <= 7:
        return phone

    return f"{phone[:4]}****{phone[-3:]}"


class StaffAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]


class IncidentNotificationAudienceView(StaffAPIView):
    def get(self, request, incident_id):
        incident = get_object_or_404(
            Incident.objects.prefetch_related(
                "affected_sites",
            ),
            pk=incident_id,
        )

        sites = affected_sites_for(incident)
        customers = list(
            eligible_customers_for(incident)
        )

        site_summary = []

        for site in sites:
            recipient_count = sum(
                1
                for customer in customers
                if customer.site_id == site.id
            )

            site_summary.append({
                "id": site.id,
                "code": site.code,
                "name": site.name,
                "eligible_recipients": recipient_count,
            })

        return Response({
            "incident": {
                "id": incident.id,
                "title": incident.title,
                "status": incident.status,
            },
            "affected_sites": site_summary,
            "eligible_recipients": len(customers),
            "sms_mode": settings.NETSAGE_SMS_MODE,
            "recipients": [
                {
                    "id": customer.id,
                    "name": customer.name,
                    "site": customer.site_id,
                    "site_name": customer.site.name,
                    "phone": mask_phone(
                        customer.phone_number
                    ),
                }
                for customer in customers
            ],
        })


class IncidentNotificationDraftView(StaffAPIView):
    def get(self, request, incident_id):
        incident = get_object_or_404(
            Incident,
            pk=incident_id,
        )

        message_type = request.query_params.get(
            "message_type",
            Notification.MessageType.OUTAGE,
        )

        if message_type not in Notification.MessageType.values:
            return Response(
                {"detail": "Invalid message type."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notifications = list(
            Notification.objects.filter(
                incident=incident,
                message_type=message_type,
                delivery_status=(
                    Notification.DeliveryStatus.NOT_SENT
                ),
            )
            .select_related("approved_by")
            .order_by("id")
        )

        if not notifications:
            return Response({
                "exists": False,
                "incident": incident.id,
                "message_type": message_type,
                "message": "",
                "recipient_count": 0,
                "approval_status": None,
                "approved_by": None,
                "approved_at": None,
                "delivery_status": None,
            })

        first = notifications[0]

        return Response({
            "exists": True,
            "incident": incident.id,
            "message_type": message_type,
            "message": first.message,
            "recipient_count": len(notifications),
            "approval_status": first.approval_status,
            "approved_by": (
                first.approved_by.username
                if first.approved_by
                else None
            ),
            "approved_at": first.approved_at,
            "delivery_status": first.delivery_status,
        })

    def post(self, request, incident_id):
        incident = get_object_or_404(
            Incident.objects.prefetch_related(
                "affected_sites",
            ),
            pk=incident_id,
        )

        serializer = NotificationDraftSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        message_type = serializer.validated_data[
            "message_type"
        ]
        message = serializer.validated_data[
            "message"
        ]

        customers = list(
            eligible_customers_for(incident)
        )

        if not customers:
            return Response(
                {
                    "detail": (
                        "There are no active SMS-opted-in "
                        "customers for the affected sites."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            # An edited unsent draft replaces the previous
            # unsent version while preserving send history.
            Notification.objects.filter(
                incident=incident,
                message_type=message_type,
                delivery_status=(
                    Notification.DeliveryStatus.NOT_SENT
                ),
            ).delete()

            notifications = [
                Notification(
                    incident=incident,
                    customer=customer,
                    recipient_phone=(
                        customer.phone_number
                    ),
                    message_type=message_type,
                    message=message,
                    approval_status=(
                        Notification.ApprovalStatus.PENDING
                    ),
                    delivery_status=(
                        Notification.DeliveryStatus.NOT_SENT
                    ),
                )
                for customer in customers
            ]

            Notification.objects.bulk_create(
                notifications
            )

        return Response(
            {
                "incident": incident.id,
                "message_type": message_type,
                "message": message,
                "character_count": len(message),
                "recipient_count": len(customers),
                "approval_status": (
                    Notification.ApprovalStatus.PENDING
                ),
                "delivery_status": (
                    Notification.DeliveryStatus.NOT_SENT
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class IncidentNotificationApproveView(StaffAPIView):
    def post(self, request, incident_id):
        incident = get_object_or_404(
            Incident,
            pk=incident_id,
        )

        serializer = NotificationApprovalSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        message_type = serializer.validated_data[
            "message_type"
        ]

        with transaction.atomic():
            notifications = list(
                Notification.objects.select_for_update()
                .filter(
                    incident=incident,
                    message_type=message_type,
                    delivery_status=(
                        Notification.DeliveryStatus.NOT_SENT
                    ),
                )
                .order_by("id")
            )

            if not notifications:
                return Response(
                    {
                        "detail": (
                            "No unsent draft exists for "
                            "this message type."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            approved_at = timezone.now()

            for notification in notifications:
                notification.approval_status = (
                    Notification.ApprovalStatus.APPROVED
                )
                notification.approved_by = request.user
                notification.approved_at = approved_at

            Notification.objects.bulk_update(
                notifications,
                [
                    "approval_status",
                    "approved_by",
                    "approved_at",
                    "updated_at",
                ],
            )

        return Response({
            "incident": incident.id,
            "message_type": message_type,
            "approval_status": (
                Notification.ApprovalStatus.APPROVED
            ),
            "approved_by": request.user.username,
            "approved_at": approved_at,
            "recipient_count": len(notifications),
        })


class IncidentNotificationSendView(StaffAPIView):
    def post(self, request, incident_id):
        incident = get_object_or_404(
            Incident,
            pk=incident_id,
        )

        serializer = NotificationApprovalSerializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        message_type = serializer.validated_data[
            "message_type"
        ]

        with transaction.atomic():
            notifications = list(
                Notification.objects.select_for_update()
                .filter(
                    incident=incident,
                    message_type=message_type,
                    approval_status=(
                        Notification.ApprovalStatus.APPROVED
                    ),
                    delivery_status=(
                        Notification.DeliveryStatus.NOT_SENT
                    ),
                )
                .select_related(
                    "customer",
                    "customer__site",
                )
                .order_by("id")
            )

            if not notifications:
                return Response(
                    {
                        "detail": (
                            "No approved unsent notifications "
                            "exist for this message type."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            messages = {
                item.message
                for item in notifications
            }

            if len(messages) != 1:
                return Response(
                    {
                        "detail": (
                            "Recipients do not share one approved "
                            "message. Save a new draft first."
                        )
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            message = notifications[0].message
            recipients = [
                item.recipient_phone
                for item in notifications
            ]

            try:
                result = send_sms(
                    message,
                    recipients,
                )
            except (
                SmsConfigurationError,
                SmsRecipientError,
                ValueError,
            ) as exc:
                return Response(
                    {"detail": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            provider_results = {
                item.get("number"): item
                for item in result.get(
                    "recipients",
                    []
                )
            }

            now = timezone.now()

            dry_run_count = 0
            submitted_count = 0
            failed_count = 0

            for notification in notifications:
                provider = provider_results.get(
                    notification.recipient_phone,
                    {},
                )

                notification.provider_message_id = str(
                    provider.get(
                        "messageId",
                        "",
                    )
                    or ""
                )

                notification.error_message = ""

                if result["mode"] == "dry_run":
                    notification.delivery_status = (
                        Notification.DeliveryStatus.DRY_RUN
                    )
                    # Deliberately do not set sent_at:
                    # nothing left NetSage.
                    dry_run_count += 1
                    continue

                provider_status = str(
                    provider.get(
                        "status",
                        "",
                    )
                ).strip()

                status_code = provider.get(
                    "statusCode"
                )

                accepted = (
                    provider_status.lower()
                    in {
                        "success",
                        "sent",
                        "queued",
                    }
                    or status_code in {100, 101, 102}
                )

                if accepted:
                    notification.delivery_status = (
                        Notification.DeliveryStatus.SENT
                    )
                    notification.sent_at = now
                    submitted_count += 1
                else:
                    notification.delivery_status = (
                        Notification.DeliveryStatus.FAILED
                    )
                    notification.error_message = (
                        provider_status
                        or "Provider did not accept the message."
                    )
                    failed_count += 1

            Notification.objects.bulk_update(
                notifications,
                [
                    "delivery_status",
                    "provider_message_id",
                    "sent_at",
                    "error_message",
                    "updated_at",
                ],
            )

        return Response({
            "incident": incident.id,
            "message_type": message_type,
            "mode": result["mode"],
            "recipient_count": len(notifications),
            "dry_run_count": dry_run_count,
            "submitted_count": submitted_count,
            "failed_count": failed_count,
            "provider_message": result.get(
                "provider_message",
                "",
            ),
        })


class IncidentNotificationHistoryView(StaffAPIView):
    def get(self, request, incident_id):
        incident = get_object_or_404(
            Incident,
            pk=incident_id,
        )

        message_type = request.query_params.get(
            "message_type",
            Notification.MessageType.OUTAGE,
        )

        if message_type not in Notification.MessageType.values:
            return Response(
                {"detail": "Invalid message type."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        notifications = list(
            Notification.objects.filter(
                incident=incident,
                message_type=message_type,
            )
            .select_related(
                "customer",
                "customer__site",
                "approved_by",
            )
            .order_by(
                "customer__site__name",
                "customer__name",
                "id",
            )
        )

        return Response({
            "incident": incident.id,
            "message_type": message_type,
            "sms_mode": settings.NETSAGE_SMS_MODE,
            "recipient_count": len(notifications),
            "notifications": [
                {
                    "id": item.id,
                    "customer": item.customer.name,
                    "site": item.customer.site.name,
                    "phone": mask_phone(
                        item.recipient_phone
                    ),
                    "approval_status": (
                        item.approval_status
                    ),
                    "delivery_status": (
                        item.delivery_status
                    ),
                    "provider_message_id": (
                        item.provider_message_id
                    ),
                    "approved_by": (
                        item.approved_by.username
                        if item.approved_by
                        else None
                    ),
                    "approved_at": item.approved_at,
                    "sent_at": item.sent_at,
                    "delivered_at": item.delivered_at,
                    "error_message": item.error_message,
                }
                for item in notifications
            ],
        })
