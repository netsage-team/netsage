"""
Pure Python detection functions - no I/O, no Django, no network calls.

  1. configurable sustained-fault detection
  2. grouping related alerts using timing + shared network dependencies
  3. recovery checks that never mistake missing/stale data for recovery
     (or automatically assume an outage)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from simulator.models import Alert, HealthState, Incident, Reading, RecoveryState
from simulator.topology import SITES, sites_sharing_dependency


@dataclass
class Thresholds:
    """
    Configurable, illustrative thresholds - NOT validated against a real
    network. Agree real starting values with network engineers before
    trusting them for anything beyond the demo.
    """
    latency_threshold_ms: float = 150.0
    packet_loss_threshold_pct: float = 5.0
    sustained_duration_s: int = 90
    interval_s: int = 30
    staleness_multiplier: float = 3.0
    recovery_duration_s: int = 180
    grouping_window_s: int = 120


def classify_reading(reading: Reading, thresholds: Thresholds) -> HealthState:
    if (
        reading.latency_ms > thresholds.latency_threshold_ms
        or reading.packet_loss_pct > thresholds.packet_loss_threshold_pct
    ):
        return HealthState.DEGRADED
    return HealthState.HEALTHY


def detect_sustained_fault(
    site_id: str,
    readings: List[Reading],
    thresholds: Thresholds,
) -> Optional[Alert]:
    readings = sorted(readings, key=lambda r: r.timestamp)
    max_gap = timedelta(seconds=thresholds.interval_s * thresholds.staleness_multiplier)
    min_duration = timedelta(seconds=thresholds.sustained_duration_s)

    run: List[Reading] = []
    for r in readings:
        state = classify_reading(r, thresholds)
        if state == HealthState.DEGRADED:
            if run and (r.timestamp - run[-1].timestamp) > max_gap:
                run = [r]
            else:
                run.append(r)
            if run[-1].timestamp - run[0].timestamp >= min_duration:
                return Alert(
                    site_id=site_id,
                    started_at=run[0].timestamp,
                    last_seen_at=run[-1].timestamp,
                    evidence=list(run),
                    reason=(
                        f"latency > {thresholds.latency_threshold_ms}ms or "
                        f"packet loss > {thresholds.packet_loss_threshold_pct}% "
                        f"sustained for >= {thresholds.sustained_duration_s}s"
                    ),
                )
        else:
            run = []
    return None


def detect_alerts_for_all_sites(
    readings_by_site: Dict[str, List[Reading]],
    thresholds: Thresholds,
) -> List[Alert]:
    alerts = []
    for site_id, readings in readings_by_site.items():
        alert = detect_sustained_fault(site_id, readings, thresholds)
        if alert:
            alerts.append(alert)
    return alerts


def group_alerts_into_incidents(
    alerts: List[Alert],
    thresholds: Thresholds,
) -> List[Incident]:
    remaining = sorted(alerts, key=lambda a: a.started_at)
    incidents: List[Incident] = []
    used = set()

    for i, alert in enumerate(remaining):
        if id(alert) in used:
            continue
        site = SITES.get(alert.site_id)
        candidate_dependency = site.depends_on[0] if site and site.depends_on else None

        group = [alert]
        used.add(id(alert))

        if candidate_dependency:
            for other in remaining[i + 1:]:
                if id(other) in used:
                    continue
                other_site = SITES.get(other.site_id)
                shares_dependency = other_site and candidate_dependency in other_site.depends_on
                within_window = abs((other.started_at - alert.started_at).total_seconds()) <= thresholds.grouping_window_s
                if shares_dependency and within_window:
                    group.append(other)
                    used.add(id(other))

        affected_sites = sorted({a.site_id for a in group})
        if len(group) > 1 and candidate_dependency:
            probable_cause = (
                f"Shared dependency '{candidate_dependency}' "
                f"(affects {len(affected_sites)} of {len(sites_sharing_dependency(candidate_dependency))} "
                f"sites on this dependency)"
            )
            confidence_note = (
                "Suggestion only, based on correlated timing across sites sharing this "
                "dependency - not a confirmed root cause. An engineer should verify."
            )
            shared_dependency = candidate_dependency
        else:
            probable_cause = f"Localised issue at {affected_sites[0]} - no correlated sites found"
            confidence_note = "Suggestion only, based on a single site's readings."
            shared_dependency = None

        incidents.append(
            Incident(
                incident_id=f"incident-{group[0].site_id}-{int(group[0].started_at.timestamp())}",
                alerts=group,
                shared_dependency=shared_dependency,
                probable_cause=probable_cause,
                confidence_note=confidence_note,
                opened_at=min(a.started_at for a in group),
            )
        )

    return incidents


def check_recovery(
    site_id: str,
    readings_after_alert: List[Reading],
    thresholds: Thresholds,
    now: Optional[datetime] = None,
) -> RecoveryState:
    if not readings_after_alert:
        return RecoveryState.UNKNOWN_STALE_DATA

    readings = sorted(readings_after_alert, key=lambda r: r.timestamp)
    reference_time = now or readings[-1].timestamp
    max_gap = timedelta(seconds=thresholds.interval_s * thresholds.staleness_multiplier)

    if reference_time - readings[-1].timestamp > max_gap:
        return RecoveryState.UNKNOWN_STALE_DATA

    run: List[Reading] = []
    for r in readings:
        state = classify_reading(r, thresholds)
        if state == HealthState.HEALTHY:
            if run and (r.timestamp - run[-1].timestamp) > max_gap:
                run = [r]
            else:
                run.append(r)
        else:
            run = []

    if run and (run[-1].timestamp - run[0].timestamp) >= timedelta(seconds=thresholds.recovery_duration_s):
        return RecoveryState.RECOVERED
    return RecoveryState.NOT_YET