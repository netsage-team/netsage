"""Bridge the standalone NetSage simulator into the Django data model."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from django.db import transaction
from django.db.models import Q

from api.models import (
    Alert,
    Device,
    Incident,
    IncidentEvent,
    Notification,
    Severity,
    Site,
    TelemetryReading,
)


# manage.py lives inside backend/, while simulator/ lives at project root.
PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulator.detection import (  # noqa: E402
    Thresholds,
    detect_alerts_for_all_sites,
    group_alerts_into_incidents,
)
from simulator.generator import SCENARIOS  # noqa: E402
from simulator.topology import SITES  # noqa: E402


@dataclass(frozen=True)
class DemoRunResult:
    scenario: str
    sites: int
    devices: int
    readings: int
    alerts: int
    incidents: int


def available_scenarios() -> tuple[str, ...]:
    return tuple(SCENARIOS.keys())


def _device_code(site_code: str) -> str:
    return f"{site_code}-router"


def _ensure_demo_topology():
    site_map = {}
    device_map = {}

    for site_code, simulator_site in SITES.items():
        site, _ = Site.objects.update_or_create(
            code=site_code,
            defaults={
                "name": simulator_site.name,
                "location": f"{simulator_site.name}, Uganda",
                "description": (
                    "Simulator-backed NetSage demonstration site."
                ),
                "is_active": True,
            },
        )

        device, _ = Device.objects.update_or_create(
            code=_device_code(site_code),
            defaults={
                "site": site,
                "name": f"{simulator_site.name} Router",
                "device_type": Device.DeviceType.ROUTER,
                "is_active": True,
            },
        )

        site_map[site_code] = site
        device_map[site_code] = device

    return site_map, device_map


def _reset_previous_demo_records(site_codes):
    """
    Remove generated operational records only for the dedicated simulator sites.

    The Site and Device rows remain so their database IDs stay stable between
    rehearsals.
    """
    incident_ids = list(
        Incident.objects.filter(
            Q(site__code__in=site_codes)
            | Q(affected_sites__code__in=site_codes)
        )
        .values_list("id", flat=True)
        .distinct()
    )

    if incident_ids:
        Notification.objects.filter(
            incident_id__in=incident_ids,
        ).delete()

    Alert.objects.filter(
        Q(device__site__code__in=site_codes)
        | Q(incident_id__in=incident_ids)
    ).delete()

    if incident_ids:
        Incident.objects.filter(id__in=incident_ids).delete()

    TelemetryReading.objects.filter(
        device__site__code__in=site_codes,
        is_simulated=True,
    ).delete()


def _alert_type(simulator_alert, thresholds):
    latency_triggered = any(
        reading.latency_ms > thresholds.latency_threshold_ms
        for reading in simulator_alert.evidence
    )

    if latency_triggered:
        return Alert.AlertType.HIGH_LATENCY

    return Alert.AlertType.PACKET_LOSS


def _severity(simulator_alert):
    max_latency = max(
        reading.latency_ms
        for reading in simulator_alert.evidence
    )
    max_packet_loss = max(
        reading.packet_loss_pct
        for reading in simulator_alert.evidence
    )

    if max_latency >= 250 or max_packet_loss >= 10:
        return Severity.CRITICAL

    return Severity.WARNING


@transaction.atomic
def run_simulator_scenario(
    scenario: str = "mukono-uplink-fault",
    *,
    reset: bool = True,
) -> DemoRunResult:
    if scenario not in SCENARIOS:
        raise ValueError(
            f"Unknown scenario {scenario!r}. "
            f"Choose from: {', '.join(available_scenarios())}"
        )

    site_map, device_map = _ensure_demo_topology()
    site_codes = tuple(site_map.keys())

    if reset:
        _reset_previous_demo_records(site_codes)

    readings_by_site = SCENARIOS[scenario]()
    thresholds = Thresholds()

    stored_readings = {}
    reading_count = 0

    for site_code, simulator_readings in readings_by_site.items():
        device = device_map[site_code]

        for simulator_reading in simulator_readings:
            reading = TelemetryReading.objects.create(
                device=device,
                recorded_at=simulator_reading.timestamp,
                is_reachable=simulator_reading.packet_loss_pct < 100,
                latency_ms=simulator_reading.latency_ms,
                packet_loss_percent=simulator_reading.packet_loss_pct,
                is_simulated=True,
            )

            stored_readings[
                (site_code, simulator_reading.timestamp)
            ] = reading
            reading_count += 1

    simulator_alerts = detect_alerts_for_all_sites(
        readings_by_site,
        thresholds,
    )

    alert_map = {}

    for simulator_alert in simulator_alerts:
        evidence_reading = simulator_alert.evidence[-1]
        database_reading = stored_readings[
            (
                simulator_alert.site_id,
                evidence_reading.timestamp,
            )
        ]

        alert = Alert.objects.create(
            device=device_map[simulator_alert.site_id],
            reading=database_reading,
            alert_type=_alert_type(
                simulator_alert,
                thresholds,
            ),
            severity=_severity(simulator_alert),
            message=simulator_alert.reason,
            detected_at=simulator_alert.started_at,
        )

        alert_map[simulator_alert.site_id] = alert

    simulator_incidents = group_alerts_into_incidents(
        simulator_alerts,
        thresholds,
    )

    for simulator_incident in simulator_incidents:
        affected_codes = sorted({
            alert.site_id
            for alert in simulator_incident.alerts
        })
        affected_sites = [
            site_map[site_code]
            for site_code in affected_codes
        ]

        anchor_site = affected_sites[0]

        if len(affected_sites) > 1:
            title = (
                "Correlated network degradation affecting "
                + ", ".join(site.name for site in affected_sites)
            )
            severity = Severity.CRITICAL
        else:
            title = (
                f"Network degradation at {anchor_site.name}"
            )
            severity = Severity.WARNING

        incident = Incident.objects.create(
            site=anchor_site,
            title=title,
            description=(
                "Automatically created from sustained simulated "
                "network degradation."
            ),
            severity=severity,
            status=Incident.Status.OPEN,
            shared_dependency=(
                simulator_incident.shared_dependency or ""
            ),
            probable_cause=simulator_incident.probable_cause,
            confidence_note=simulator_incident.confidence_note,
            opened_at=simulator_incident.opened_at,
        )

        incident.affected_sites.set(affected_sites)

        IncidentEvent.objects.create(
            incident=incident,
            event_type=IncidentEvent.EventType.DETECTED,
            message=(
                "Incident automatically detected from sustained "
                "correlated network degradation."
            ),
        )

        for simulator_alert in simulator_incident.alerts:
            alert = alert_map[simulator_alert.site_id]
            alert.incident = incident
            alert.save(update_fields=["incident"])

    return DemoRunResult(
        scenario=scenario,
        sites=len(site_map),
        devices=len(device_map),
        readings=reading_count,
        alerts=len(simulator_alerts),
        incidents=len(simulator_incidents),
    )
