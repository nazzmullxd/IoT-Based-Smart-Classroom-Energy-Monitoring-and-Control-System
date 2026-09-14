def energy_wh(power_w: float, runtime_seconds: float) -> float:
    """Estimate energy from nominal power and runtime; no meter is involved."""
    return power_w * runtime_seconds / 3600.0


def saving_percentage(conventional_wh: float, smart_wh: float) -> float:
    if conventional_wh <= 0:
        return 0.0
    return (conventional_wh - smart_wh) / conventional_wh * 100.0
