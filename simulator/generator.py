"""
Repeatable telemetry generator.

A "scenario" is a timeline of phases per site. Each phase has a duration
(in samples) and a reading profile (baseline + jitter, or degraded
baseline + jitter). Using a seeded random generator makes runs
reproducible, which matters for a demo you'll rehearse more than once.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from simulator.models import Reading
from simulator.topology import SITES, UPLINK_MUKONO


@dataclass
class Phase:
    label: str
    num_samples: int
    latency_base_ms: float
    latency_jitter_ms: float
    packet_loss_base_pct: float
    packet_loss_jitter_pct: float


def _sample(rng: random.Random, base: float, jitter: float, floor: float = 0.0) -> float:
    return max(floor, rng.gauss(base, jitter))


def generate_site_readings(
    rng: random.Random,
    site_id: str,
    start_time: datetime,
    interval_s: int,
    phases: List[Phase],
) -> List[Reading]:
    readings: List[Reading] = []
    t = start_time
    for phase in phases:
        for _ in range(phase.num_samples):
            readings.append(
                Reading(
                    site_id=site_id,
                    timestamp=t,
                    latency_ms=_sample(rng, phase.latency_base_ms, phase.latency_jitter_ms, floor=1.0),
                    packet_loss_pct=min(
                        100.0,
                        _sample(rng, phase.packet_loss_base_pct, phase.packet_loss_jitter_pct, floor=0.0),
                    ),
                )
            )
            t = t + timedelta(seconds=interval_s)
    return readings


HEALTHY_PHASE = lambda n: Phase("healthy", n, latency_base_ms=25, latency_jitter_ms=4,
                                 packet_loss_base_pct=0.2, packet_loss_jitter_pct=0.2)
DEGRADED_PHASE = lambda n: Phase("degraded", n, latency_base_ms=260, latency_jitter_ms=25,
                                  packet_loss_base_pct=9.0, packet_loss_jitter_pct=2.0)


def scenario_mukono_uplink_fault(
    interval_s: int = 30,
    healthy_before: int = 10,
    degraded_for: int = 12,
    healthy_after: int = 14,
    seed: int = 42,
) -> Dict[str, List[Reading]]:
    """
    Simulated shared Mukono uplink problem: Mukono Central, UCU Area and
    Seeta all degrade at roughly the same time because they share the
    Mukono uplink, then all recover.
    """
    start = datetime.now(timezone.utc)
    phases = [HEALTHY_PHASE(healthy_before), DEGRADED_PHASE(degraded_for), HEALTHY_PHASE(healthy_after)]

    out: Dict[str, List[Reading]] = {}
    for site_index, site_id in enumerate(SITES):
        # Use a stable integer offset instead of Python's randomized
        # string hash so demo telemetry is reproducible across processes.
        site_rng = random.Random(seed + site_index)
        out[site_id] = generate_site_readings(site_rng, site_id, start, interval_s, phases)
    return out


def scenario_single_site_blip(
    interval_s: int = 30,
    healthy_before: int = 10,
    degraded_for: int = 2,
    healthy_after: int = 10,
    seed: int = 7,
) -> Dict[str, List[Reading]]:
    """
    Control scenario: only Seeta has a short degradation that should NOT
    last long enough to cross the sustained-fault threshold, and should
    NOT be grouped with anything.
    """
    rng = random.Random(seed)
    start = datetime.now(timezone.utc)
    phases = [HEALTHY_PHASE(healthy_before), DEGRADED_PHASE(degraded_for), HEALTHY_PHASE(healthy_after)]

    out: Dict[str, List[Reading]] = {}
    for site_id in SITES:
        if site_id == "site-seeta":
            out[site_id] = generate_site_readings(rng, site_id, start, interval_s, phases)
        else:
            out[site_id] = generate_site_readings(
                rng, site_id, start, interval_s, [HEALTHY_PHASE(healthy_before + degraded_for + healthy_after)]
            )
    return out


SCENARIOS = {
    "mukono-uplink-fault": scenario_mukono_uplink_fault,
    "single-site-blip": scenario_single_site_blip,
}