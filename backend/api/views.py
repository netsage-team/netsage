from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Device, Site
from .serializers import DeviceSerializer, SiteSerializer


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