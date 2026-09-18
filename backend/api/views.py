from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Device, Site, TelemetryReading
from .serializers import (
    DeviceSerializer,
    SiteSerializer,
    TelemetryFilterSerializer,
    TelemetryReadingSerializer,
)


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({
        "status": "ok",
        "service": "NetSage API",
    })


class StandardPagination(PageNumberPagination):
    page_size = 25


class SiteViewSet(ReadOnlyModelViewSet):
    queryset = Site.objects.all().order_by("name", "id")
    serializer_class = SiteSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination


class DeviceViewSet(ReadOnlyModelViewSet):
    queryset = (
        Device.objects.select_related("site")
        .all()
        .order_by("name", "id")
    )
    serializer_class = DeviceSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination


class TelemetryReadingViewSet(ReadOnlyModelViewSet):
    serializer_class = TelemetryReadingSerializer
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        filters = TelemetryFilterSerializer(
            data=self.request.query_params,
        )
        filters.is_valid(raise_exception=True)

        queryset = (
            TelemetryReading.objects.select_related("device")
            .order_by("-recorded_at", "-id")
        )

        device_id = filters.validated_data.get("device")
        site_id = filters.validated_data.get("site")

        if device_id is not None:
            queryset = queryset.filter(device_id=device_id)

        if site_id is not None:
            queryset = queryset.filter(device__site_id=site_id)

        return queryset