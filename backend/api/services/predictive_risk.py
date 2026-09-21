from statistics import mean

from ..models import Site, TelemetryReading


PREDICTION_WINDOW = 8


def _slope(values):
    """
    Calculate the direction and speed of change.

    Positive values mean the metric is increasing.
    Negative values mean it is improving.
    """
    if len(values) < 3:
        return 0.0

    x_values = list(range(len(values)))

    x_mean = mean(x_values)
    y_mean = mean(values)

    numerator = sum(
        (x - x_mean) * (y - y_mean)
        for x, y in zip(x_values, values)
    )

    denominator = sum(
        (x - x_mean) ** 2
        for x in x_values
    )

    if denominator == 0:
        return 0.0

    return numerator / denominator


def _risk_level(score):
    if score >= 80:
        return "critical"

    if score >= 60:
        return "high"

    if score >= 35:
        return "medium"

    return "low"


def analyse_site_risk(site):
    """
    Analyse recent telemetry for one site.

    The prototype uses explainable trend analysis rather than
    a trained production ML model.

    It considers:
    - latency
    - packet loss
    - reachability
    - recent metric trends
    """

    readings = list(
        TelemetryReading.objects.filter(
            device__site=site,
        )
        .select_related("device")
        .order_by(
            "-recorded_at",
            "-id",
        )[:PREDICTION_WINDOW]
    )

    readings.reverse()

    if len(readings) < 3:
        return {
            "site_id": site.id,
            "site_name": site.name,
            "location": site.location,
            "site_type": site.site_type,
            "risk_score": 0,
            "risk_level": "unknown",
            "predicted_failure": False,
            "latest_latency_ms": None,
            "latest_packet_loss_percent": None,
            "is_reachable": None,
            "latency_trend": 0.0,
            "packet_loss_trend": 0.0,
            "reasons": [
                "Insufficient recent telemetry for prediction."
            ],
            "recommended_action": (
                "Continue collecting telemetry."
            ),
            "reading_count": len(readings),
            "last_reading_at": (
                readings[-1].recorded_at
                if readings
                else None
            ),
        }

    latest = readings[-1]

    latencies = [
        reading.latency_ms
        for reading in readings
        if reading.latency_ms is not None
    ]

    packet_losses = [
        reading.packet_loss_percent
        for reading in readings
    ]

    latency_slope = _slope(latencies)
    loss_slope = _slope(packet_losses)

    score = 0
    reasons = []

    # --------------------------------------------------
    # Reachability
    # --------------------------------------------------

    if not latest.is_reachable:
        score += 45

        reasons.append(
            "Latest telemetry reports the device as unreachable."
        )

    # --------------------------------------------------
    # Current latency
    # --------------------------------------------------

    if latest.latency_ms is not None:
        if latest.latency_ms >= 150:
            score += 25

            reasons.append(
                "Latency is critically high at "
                f"{latest.latency_ms:.1f} ms."
            )

        elif latest.latency_ms >= 100:
            score += 15

            reasons.append(
                "Latency is elevated at "
                f"{latest.latency_ms:.1f} ms."
            )

    # --------------------------------------------------
    # Current packet loss
    # --------------------------------------------------

    if latest.packet_loss_percent >= 5:
        score += 25

        reasons.append(
            "Packet loss is high at "
            f"{latest.packet_loss_percent:.1f}%."
        )

    elif latest.packet_loss_percent >= 2:
        score += 10

        reasons.append(
            "Packet loss is elevated at "
            f"{latest.packet_loss_percent:.1f}%."
        )

    # --------------------------------------------------
    # Latency trend
    # --------------------------------------------------

    if latency_slope >= 12:
        score += 15

        reasons.append(
            "Latency is rising rapidly across recent readings."
        )

    elif latency_slope >= 5:
        score += 8

        reasons.append(
            "Latency shows a sustained upward trend."
        )

    # --------------------------------------------------
    # Packet-loss trend
    # --------------------------------------------------

    if loss_slope >= 1:
        score += 15

        reasons.append(
            "Packet loss is rising rapidly."
        )

    elif loss_slope >= 0.4:
        score += 8

        reasons.append(
            "Packet loss shows a sustained upward trend."
        )

    # --------------------------------------------------
    # Last three readings
    # --------------------------------------------------

    recent = readings[-3:]

    recent_latency = [
        item.latency_ms
        for item in recent
        if item.latency_ms is not None
    ]

    if (
        len(recent_latency) == 3
        and recent_latency[0]
        < recent_latency[1]
        < recent_latency[2]
    ):
        score += 7

        reasons.append(
            "Latency increased across the last three readings."
        )

    recent_loss = [
        item.packet_loss_percent
        for item in recent
    ]

    if (
        len(recent_loss) == 3
        and recent_loss[0]
        < recent_loss[1]
        < recent_loss[2]
    ):
        score += 7

        reasons.append(
            "Packet loss increased across the last three readings."
        )

    # Maximum possible risk is 100.
    score = min(score, 100)

    level = _risk_level(score)

    # A prediction means:
    # the site is still reachable,
    # but telemetry indicates high or critical risk.
    predicted_failure = (
        latest.is_reachable
        and level in {
            "high",
            "critical",
        }
    )

    # --------------------------------------------------
    # Automated response recommendation
    # --------------------------------------------------

    if level == "critical":
        action = (
            "Escalate immediately to network operations. "
            "Inspect the site and its upstream dependency."
        )

    elif level == "high":
        action = (
            "Start preventive investigation before service "
            "failure. Inspect the site and shared upstream "
            "connection."
        )

    elif level == "medium":
        action = (
            "Increase monitoring frequency and inspect the "
            "site if degradation continues."
        )

    else:
        action = (
            "No intervention required. Continue normal monitoring."
        )

    if not reasons:
        reasons.append(
            "Recent telemetry remains within expected limits."
        )

    return {
        "site_id": site.id,
        "site_name": site.name,
        "location": site.location,
        "site_type": site.site_type,
        "risk_score": score,
        "risk_level": level,
        "predicted_failure": predicted_failure,
        "latest_latency_ms": latest.latency_ms,
        "latest_packet_loss_percent": (
            latest.packet_loss_percent
        ),
        "is_reachable": latest.is_reachable,
        "latency_trend": round(
            latency_slope,
            2,
        ),
        "packet_loss_trend": round(
            loss_slope,
            2,
        ),
        "reasons": reasons,
        "recommended_action": action,
        "reading_count": len(readings),
        "last_reading_at": latest.recorded_at,
    }


def network_risk_snapshot():
    """
    Analyse all active sites and return highest-risk
    infrastructure first.
    """

    results = [
        analyse_site_risk(site)
        for site in Site.objects.filter(
            is_active=True,
        )
    ]

    return sorted(
        results,
        key=lambda item: item["risk_score"],
        reverse=True,
    )