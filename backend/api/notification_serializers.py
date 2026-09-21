from rest_framework import serializers

from .models import Notification


class NotificationDraftSerializer(serializers.Serializer):
    message_type = serializers.ChoiceField(
        choices=Notification.MessageType.choices,
    )
    message = serializers.CharField(
        max_length=480,
        trim_whitespace=True,
    )


class NotificationApprovalSerializer(serializers.Serializer):
    message_type = serializers.ChoiceField(
        choices=Notification.MessageType.choices,
    )
