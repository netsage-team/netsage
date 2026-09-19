import sys
from pathlib import Path

from django.utils import timezone

from api.models import TelemetryReading


PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from simulator.detection import (  # noqa: E402
    RecoveryState,
    Thresholds,
    check_recovery,
)
from simulator.models import Reading  # noqa: E402


def _state_value(state):
    return getattr(state, "value", str(state))


def evaluate_incident_recovery(incident):
    """
    Evaluate sustained recovery for every site affected by an incident.

    Simulated demo telemetry is evaluated relative to its own latest
    timestamp so a completed static rehearsal can still demonstrate
    recovery.

    Non-simulated telemetry is evaluated relative to the real current
    time, preserving stale-data protection for real monitoring.
    """
    affected_sites = list(
        incident.affected_sites.all().order_by("id")
    )

    if not affected_sites:
        affected_sites = [incident.site]

    thresholds = Thresholds()
    site_results = []

    for site in affected_sites:
        incident_device_ids = list(
            incident.alerts.filter(
                device__site=site,
            ).values_list(
                "device_id",
                flat=True,
            )
        )

        readings_qs = TelemetryReading.objects.filter(
            device__site=site,
            recorded_at__gte=incident.opened_at,
        )

        if incident_device_ids:
            readings_qs = readings_qs.filter(
                device_id__in=incident_device_ids,
            )

        database_readings = list(
            readings_qs.select_related("device").order_by(
                "recorded_at",
                "id",
            )
        )

        simulator_readings = [
            Reading(
                site_id=site.code,
                timestamp=reading.recorded_at,
                latency_ms=(
                    float(reading.latency_ms)
                    if reading.latency_ms is not None
                    else None
                ),
                packet_loss_pct=float(
                    reading.packet_loss_percent
                ),
            )
            for reading in database_readings
        ]

        if database_readings and all(
            reading.is_simulated
            for reading in database_readings
        ):
            reference_time = database_readings[-1].recorded_at
            reference_mode = "simulated"
        else:
            reference_time = timezone.now()
            reference_mode = "live"

        state = check_recovery(
            site.code,
            simulator_readings,
            thresholds,
            now=reference_time,
        )

        site_results.append({
            "site_id": site.id,
            "site_code": site.code,
            "site_name": site.name,
            "state": _state_value(state),
            "reading_count": len(database_readings),
            "reference_mode": reference_mode,
        })

    recovered = bool(site_results) and all(
        result["state"] == _state_value(
            RecoveryState.RECOVERED
        )
        for result in site_results
    )

    return {
        "recovered": recovered,
        "sites": site_results,
    }
