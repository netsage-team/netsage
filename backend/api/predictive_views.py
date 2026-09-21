from rest_framework.response import Response

from .notification_views import StaffAPIView
from .services.predictive_risk import network_risk_snapshot


class PredictiveRiskView(StaffAPIView):
    """
    Return the current predictive network-risk snapshot.

    This endpoint is used by the operations dashboard to show
    sites that are trending toward degradation or failure.
    """

    def get(self, request):
        snapshot = network_risk_snapshot()

        warnings = [
            site
            for site in snapshot
            if site["risk_level"]
            in {
                "medium",
                "high",
                "critical",
            }
        ]

        predicted_failures = [
            site
            for site in snapshot
            if site["predicted_failure"]
        ]

        highest_risk = (
            snapshot[0]
            if snapshot
            else None
        )

        return Response(
            {
                "site_count": len(snapshot),
                "warning_count": len(warnings),
                "predicted_failure_count": len(
                    predicted_failures
                ),
                "highest_risk": highest_risk,
                "warnings": warnings,
                "sites": snapshot,
            }
        )