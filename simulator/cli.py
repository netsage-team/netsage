"""
NetSage simulator CLI.

Usage:
    python -m simulator.cli generate --scenario mukono-uplink-fault --out readings.jsonl
    python -m simulator.cli detect --in readings.jsonl
    python -m simulator.cli demo --scenario mukono-uplink-fault
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, List

from simulator.detection import (
    Thresholds,
    check_recovery,
    detect_alerts_for_all_sites,
    group_alerts_into_incidents,
)
from simulator.generator import SCENARIOS
from simulator.models import Reading
from simulator.topology import SITES


def _readings_to_jsonl(readings_by_site: Dict[str, List[Reading]]) -> str:
    lines = []
    for site_id, readings in readings_by_site.items():
        for r in readings:
            lines.append(json.dumps(r.to_dict()))
    return "\n".join(lines)


def _jsonl_to_readings(text: str) -> Dict[str, List[Reading]]:
    from datetime import datetime
    out: Dict[str, List[Reading]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        r = Reading(
            site_id=d["site_id"],
            timestamp=datetime.fromisoformat(d["timestamp"].replace("Z", "+00:00")),
            latency_ms=d["latency_ms"],
            packet_loss_pct=d["packet_loss_pct"],
        )
        out.setdefault(r.site_id, []).append(r)
    return out


def cmd_generate(args: argparse.Namespace) -> None:
    scenario_fn = SCENARIOS[args.scenario]
    readings_by_site = scenario_fn(interval_s=args.interval)
    text = _readings_to_jsonl(readings_by_site)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text + "\n")
        print(f"Wrote readings for {len(readings_by_site)} sites to {args.out}", file=sys.stderr)
    else:
        print(text)


def cmd_detect(args: argparse.Namespace) -> None:
    with open(args.infile) as f:
        readings_by_site = _jsonl_to_readings(f.read())

    thresholds = Thresholds()
    alerts = detect_alerts_for_all_sites(readings_by_site, thresholds)
    incidents = group_alerts_into_incidents(alerts, thresholds)

    print(json.dumps([i.to_dict() for i in incidents], indent=2))


def cmd_demo(args: argparse.Namespace) -> None:
    scenario_fn = SCENARIOS[args.scenario]
    readings_by_site = scenario_fn(interval_s=args.interval)
    thresholds = Thresholds()

    print(f"=== Scenario: {args.scenario} ===")
    for site_id in readings_by_site:
        print(f"  {SITES[site_id].name}: {len(readings_by_site[site_id])} readings generated")

    alerts = detect_alerts_for_all_sites(readings_by_site, thresholds)
    print(f"\n=== Alerts detected: {len(alerts)} ===")
    for a in alerts:
        print(f"  [{a.site_id}] onset {a.started_at.isoformat()} - {a.reason}")

    incidents = group_alerts_into_incidents(alerts, thresholds)
    print(f"\n=== Incidents after grouping: {len(incidents)} ===")
    for inc in incidents:
        print(json.dumps(inc.to_dict(), indent=2))

    print("\n=== Recovery check (using tail of each affected site's data) ===")
    for inc in incidents:
        for alert in inc.alerts:
            site_readings = sorted(readings_by_site[alert.site_id], key=lambda r: r.timestamp)
            after = [r for r in site_readings if r.timestamp > alert.last_seen_at]
            state = check_recovery(alert.site_id, after, thresholds)
            print(f"  {alert.site_id}: {state.value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="NetSage telemetry simulator and detection demo")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate telemetry readings for a scenario")
    p_gen.add_argument("--scenario", choices=SCENARIOS.keys(), default="mukono-uplink-fault")
    p_gen.add_argument("--interval", type=int, default=30, help="Sample interval in seconds")
    p_gen.add_argument("--out", help="Output JSONL file (default: stdout)")
    p_gen.set_defaults(func=cmd_generate)

    p_det = sub.add_parser("detect", help="Run detection over a JSONL readings file")
    p_det.add_argument("--in", dest="infile", required=True, help="Input JSONL readings file")
    p_det.set_defaults(func=cmd_detect)

    p_demo = sub.add_parser("demo", help="Generate + detect + recovery check in one run")
    p_demo.add_argument("--scenario", choices=SCENARIOS.keys(), default="mukono-uplink-fault")
    p_demo.add_argument("--interval", type=int, default=30)
    p_demo.set_defaults(func=cmd_demo)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()