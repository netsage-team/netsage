"""
Stdlib-only tests (no pytest dependency needed) so these run in any
teammate's venv without touching requirements.txt.
"""

import unittest
from datetime import datetime, timedelta, timezone

from simulator.detection import Thresholds, check_recovery, detect_sustained_fault, group_alerts_into_incidents, detect_alerts_for_all_sites
from simulator.models import Reading, RecoveryState
from simulator.generator import scenario_mukono_uplink_fault, scenario_single_site_blip


def _reading(site_id, t, latency, loss):
    return Reading(site_id=site_id, timestamp=t, latency_ms=latency, packet_loss_pct=loss)


class TestSustainedFaultDetection(unittest.TestCase):
    def setUp(self):
        self.thresholds = Thresholds(sustained_duration_s=90, interval_s=30)
        self.start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def test_no_alert_when_healthy(self):
        readings = [_reading("s1", self.start + timedelta(seconds=30 * i), 20, 0.1) for i in range(5)]
        self.assertIsNone(detect_sustained_fault("s1", readings, self.thresholds))

    def test_no_alert_for_brief_blip(self):
        readings = [
            _reading("s1", self.start, 20, 0.1),
            _reading("s1", self.start + timedelta(seconds=30), 300, 10),
            _reading("s1", self.start + timedelta(seconds=60), 300, 10),
            _reading("s1", self.start + timedelta(seconds=90), 20, 0.1),
        ]
        self.assertIsNone(detect_sustained_fault("s1", readings, self.thresholds))

    def test_alert_for_sustained_degradation(self):
        readings = [
            _reading("s1", self.start + timedelta(seconds=30 * i), 300, 10) for i in range(5)
        ]
        alert = detect_sustained_fault("s1", readings, self.thresholds)
        self.assertIsNotNone(alert)
        self.assertEqual(alert.site_id, "s1")
        self.assertGreaterEqual((alert.last_seen_at - alert.started_at).total_seconds(), 90)


class TestGrouping(unittest.TestCase):
    def test_shared_uplink_fault_produces_one_incident_not_three(self):
        readings_by_site = scenario_mukono_uplink_fault()
        thresholds = Thresholds()
        alerts = detect_alerts_for_all_sites(readings_by_site, thresholds)
        self.assertEqual(len(alerts), 3, "expected all three sites to alert")

        incidents = group_alerts_into_incidents(alerts, thresholds)
        self.assertEqual(len(incidents), 1, "correlated alerts must group into ONE incident, not duplicates")
        self.assertEqual(incidents[0].shared_dependency, "uplink-mukono")
        self.assertEqual(len(incidents[0].alerts), 3)

    def test_control_scenario_does_not_over_trigger(self):
        readings_by_site = scenario_single_site_blip()
        thresholds = Thresholds()
        alerts = detect_alerts_for_all_sites(readings_by_site, thresholds)
        self.assertEqual(len(alerts), 0, "a brief blip below sustained_duration_s must not alert")


class TestRecovery(unittest.TestCase):
    def setUp(self):
        self.thresholds = Thresholds(recovery_duration_s=180, interval_s=30, sustained_duration_s=90)
        self.start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def test_recovered_after_sustained_healthy_window(self):
        readings = [_reading("s1", self.start + timedelta(seconds=30 * i), 20, 0.1) for i in range(8)]
        state = check_recovery("s1", readings, self.thresholds, now=readings[-1].timestamp)
        self.assertEqual(state, RecoveryState.RECOVERED)

    def test_not_yet_when_healthy_window_too_short(self):
        readings = [_reading("s1", self.start + timedelta(seconds=30 * i), 20, 0.1) for i in range(3)]
        state = check_recovery("s1", readings, self.thresholds, now=readings[-1].timestamp)
        self.assertEqual(state, RecoveryState.NOT_YET)

    def test_no_data_is_unknown_not_recovered(self):
        state = check_recovery("s1", [], self.thresholds, now=self.start)
        self.assertEqual(state, RecoveryState.UNKNOWN_STALE_DATA)

    def test_stale_data_is_unknown_not_recovered_and_not_outage(self):
        readings = [_reading("s1", self.start, 20, 0.1)]
        far_future = self.start + timedelta(hours=2)
        state = check_recovery("s1", readings, self.thresholds, now=far_future)
        self.assertEqual(state, RecoveryState.UNKNOWN_STALE_DATA)

    def test_gap_inside_window_restarts_the_healthy_run(self):
        readings = [
            _reading("s1", self.start, 20, 0.1),
            _reading("s1", self.start + timedelta(seconds=30), 20, 0.1),
            _reading("s1", self.start + timedelta(minutes=20), 20, 0.1),
            _reading("s1", self.start + timedelta(minutes=20, seconds=30), 20, 0.1),
        ]
        state = check_recovery("s1", readings, self.thresholds, now=readings[-1].timestamp)
        self.assertEqual(state, RecoveryState.NOT_YET)


if __name__ == "__main__":
    unittest.main()