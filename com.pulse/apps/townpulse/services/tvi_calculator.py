from __future__ import annotations


def grade_from_score(score: float) -> str:
    if score < 30:
        return "danger"
    if score < 60:
        return "warning"
    return "safe"


def calculate_bus_interval_score(
    bus_route_count: int | None,
    avg_interval: float | None,
    nearest_stop_m: int | None,
    stops_1km: int | None,
) -> float:
    if bus_route_count is None:
        return 0.5
    if bus_route_count == 0 or (stops_1km is not None and stops_1km == 0):
        return 0.0
    if nearest_stop_m is not None and nearest_stop_m > 1000:
        return 0.0
    if avg_interval is None:
        return 0.5
    if avg_interval <= 20:
        return 1.0
    if avg_interval >= 60:
        return 0.2
    return max(0.2, 1.0 - (avg_interval - 20) / 50)


def calculate_vacancy_score(vacancy_rate: float) -> float:
    return min(1.0, max(0.0, vacancy_rate / 0.3))


def normalize_min_max(value: float, vmin: float, vmax: float) -> float:
    if vmax <= vmin:
        return 0.5
    return max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))


def calculate_pop_decline_raw(
    pop_change_rate: float,
    elderly_rate: float,
    youth_ratio: float,
    net_migration: int,
    households: int,
) -> float:
    migration_factor = abs(net_migration) / max(households, 1)
    return (
        abs(min(pop_change_rate, 0)) * 0.35
        + elderly_rate * 0.25
        + (1 - youth_ratio) * 0.2
        + migration_factor * 0.2
    )


def calculate_tvi(pop_decline_norm: float, vacancy_score: float, bus_score: float) -> float:
    composite = pop_decline_norm * 0.70 + vacancy_score * 0.20 + bus_score * 0.10
    return round(composite * 100, 1)


def simulate_tvi_gain(prescription_code: str, current_tvi: float, vacancy_rate: float, bus_score: float) -> tuple[float, float]:
    gains = {
        "VACANT_BUYBACK": (3.0, 8.0),
        "DRT": (2.0, 6.0),
        "INCENTIVE": (1.5, 5.0),
        "SOC_COMPLEX": (1.0, 4.0),
        "ELDERLY_CARE": (0.8, 3.0),
    }
    base_min, base_max = gains.get(prescription_code, (1.0, 3.0))
    if prescription_code == "INCENTIVE":
        gamma = 1.0 + (1 - bus_score) * 0.3
        return base_min * gamma, min(15.0, base_max * gamma)
    if prescription_code == "SOC_COMPLEX":
        factor = 1.0 + vacancy_rate
        return base_min * factor, min(12.0, base_max * factor)
    return base_min, base_max
