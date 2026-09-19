"""
Pure-Python data structures shared across the simulator and detection logic.

These are intentionally plain dataclasses (no Django models here) so that:
  - Phionah can develop and test detection logic without the backend running.
  - Grace can look at `.to_dict()` output to help shape docs/api-contract.md.
  - Nothing here assumes SQLite/Postgres, Django REST Framework, etc.

Units (agree these with Grace before wiring up real ingestion):
  - timestamps: UTC, ISO 8601, timezone-aware (see `utc_now`)
  - latency: milliseconds (float)
  - packet_loss: percentage, 0-100 (float)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(ts: datetime) -> str:
    """Render a UTC timestamp the way it should cross the wire: ISO 8601 with 'Z'."""
    return ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


class HealthState(str, Enum):
    """Per-reading classification against configured thresholds."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"


class RecoveryState(str, Enum):
    """
    Result of a recovery check. Deliberately three-valued:
    telemetry gaps must never silently become RECOVERED or STALE->OUTAGE.
    """
    RECOVERED = "recovered"          # fresh, sustained healthy readings for the required window
    NOT_YET = "not_yet"              # still degraded, or healthy window too short so far
    UNKNOWN_STALE_DATA = "unknown_stale_data"  # missing/stale telemetry - cannot confirm either way


@dataclass
class Site:
    site_id: str
    name: str
    depends_on: List[str] = field(default_factory=list)


@dataclass
class Reading:
    site_id: str
    timestamp: datetime
    latency_ms: float
    packet_loss_pct: float

    def to_dict(self) -> dict:
        return {
            "site_id": self.site_id,
            "timestamp": iso(self.timestamp),
            "latency_ms": round(self.latency_ms, 2),
            "packet_loss_pct": round(self.packet_loss_pct, 2),
        }


@dataclass
class Alert:
    """A sustained-fault detection for a single site, with the evidence behind it."""
    site_id: str
    started_at: datetime
    last_seen_at: datetime
    evidence: List[Reading]
    reason: str

    def to_dict(self) -> dict:
        return {
            "site_id": self.site_id,
            "started_at": iso(self.started_at),
            "last_seen_at": iso(self.last_seen_at),
            "reason": self.reason,
            "evidence": [r.to_dict() for r in self.evidence],
        }


@dataclass
class Incident:
    """
    One or more Alerts grouped together because they share timing and a
    network dependency. `probable_cause` is a suggestion, not a diagnosis -
    it must always be phrased and consumed as such.
    """
    incident_id: str
    alerts: List[Alert]
    shared_dependency: Optional[str]
    probable_cause: str
    confidence_note: str
    opened_at: datetime
    recovery_state: RecoveryState = RecoveryState.NOT_YET

    def to_dict(self) -> dict:
        return {
            "incident_id": self.incident_id,
            "opened_at": iso(self.opened_at),
            "affected_sites": sorted({a.site_id for a in self.alerts}),
            "shared_dependency": self.shared_dependency,
            "probable_cause": self.probable_cause,
            "confidence_note": self.confidence_note,
            "recovery_state": self.recovery_state.value,
            "alerts": [a.to_dict() for a in self.alerts],
        }