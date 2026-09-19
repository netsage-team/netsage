# NetSage Simulator

This folder contains the network telemetry simulator and detection logic for the part of the project completed so far.

The simulator generates repeatable network readings for a small site topology, detects sustained degradation, groups related alerts into incidents, and checks whether a site has recovered without incorrectly treating stale or missing telemetry as healthy.

## What this module does

- Generates telemetry for multiple sites sharing a dependency
- Simulates both shared uplink failures and short single-site blips
- Detects sustained latency and packet-loss faults
- Groups related alerts into one incident when they share the same dependency
- Performs conservative recovery checks that refuse to mark stale data as recovered
- Exposes a CLI for demo, generation, and detection workflows

## Module structure

```text
simulator/
├── __init__.py
├── README.md
├── cli.py
├── detection.py
├── generator.py
├── models.py
├── topology.py
├── example_payloads/
│   ├── alert.json
│   ├── incident.json
│   └── telemetry_reading.json
└── tests/
    └── test_detection.py
```

## Topology

The demo topology models three sites sharing the same uplink:

- Mukono Central
- UCU Area
- Seeta

The key example scenario is a shared uplink problem affecting all three sites at roughly the same time.

## Quick start

From the project root:

```bash
.venv/bin/python -m simulator.cli demo --scenario mukono-uplink-fault
.venv/bin/python -m simulator.cli demo --scenario single-site-blip
.venv/bin/python -m simulator.cli generate --scenario mukono-uplink-fault --out readings.jsonl
.venv/bin/python -m simulator.cli detect --in readings.jsonl
```

Run the tests:

```bash
.venv/bin/python -m unittest simulator.tests.test_detection -v
```

## Scenarios

### mukono-uplink-fault
This is the main shared-dependency scenario. All three sites degrade together, which should trigger three alerts that then collapse into one grouped incident.

### single-site-blip
This is the negative control. A short blip on one site is too brief to stay above the sustained fault threshold, so no alert should be created.

## Detection logic

The core logic lives in `simulator/detection.py` and includes:

- `classify_reading()` to mark readings as healthy or degraded
- `detect_sustained_fault()` to identify alerts lasting long enough to matter
- `group_alerts_into_incidents()` to combine alerts that share a dependency
- `check_recovery()` to determine whether a site has truly recovered

## Thresholds

The default thresholds are defined in `Thresholds` and are intentionally illustrative rather than production-validated.

```python
latency_threshold_ms = 150.0
packet_loss_threshold_pct = 5.0
sustained_duration_s = 90
interval_s = 30
staleness_multiplier = 3.0
recovery_duration_s = 180
grouping_window_s = 120
```

These values are useful for demoing the logic, but they should be agreed with the network team before being treated as real operating thresholds.

## Recovery behavior

The recovery check is conservative by design:

- it returns `recovered` only after a sustained healthy window
- it returns `not_yet` while a site is still degraded or has not recovered long enough
- it returns `unknown_stale_data` when the data is missing or too stale to trust

This avoids false recovery signals caused by incomplete or stale telemetry.

## Example payloads

The `example_payloads/` directory contains sample real outputs from this simulator:

- `telemetry_reading.json` — one input telemetry reading
- `alert.json` — one site-level sustained fault alert
- `incident.json` — one grouped incident generated from the shared uplink failure

## Notes

This part of the project is intentionally standalone. It does not depend on the Django backend, SQLite database, or the frontend. It is built to be demoable, testable, and easy to integrate later once the broader API and database contract are agreed.

## Summary

This simulator demonstrates a working proof-of-concept for network outage detection and incident grouping in a controlled environment. It is a strong foundation for the wider NetSage system and provides a repeatable way to validate the monitoring logic before full production integration.
