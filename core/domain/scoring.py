from __future__ import annotations

import math

from core.domain.exceptions import ScoringError
from core.domain.forecast_models import BrierDecomposition, Forecast, Outcome


def brier_score(probability: float, *, outcome: bool) -> float:
    if not 0.0 <= probability <= 1.0:
        msg = f"Probability must be in [0, 1], got {probability}"
        raise ScoringError(msg)
    actual = 1.0 if outcome else 0.0
    return (probability - actual) ** 2


def brier_decomposition(
    forecasts: list[Forecast],
    outcomes: list[Outcome],
) -> BrierDecomposition:
    if not forecasts or len(forecasts) != len(outcomes):
        msg = "Forecasts and outcomes must be non-empty and equal length"
        raise ScoringError(msg)
    outcome_map = {o.forecast_id: o.resolved for o in outcomes}
    pairs = _build_probability_outcome_pairs(forecasts, outcome_map)
    return _compute_decomposition(pairs)


def _build_probability_outcome_pairs(
    forecasts: list[Forecast],
    outcome_map: dict[str, bool],
) -> list[tuple[float, float]]:
    pairs: list[tuple[float, float]] = []
    for fc in forecasts:
        if fc.id not in outcome_map:
            continue
        actual = 1.0 if outcome_map[fc.id] else 0.0
        pairs.append((fc.probability, actual))
    return pairs


def _compute_decomposition(
    pairs: list[tuple[float, float]],
) -> BrierDecomposition:
    n = len(pairs)
    if n == 0:
        msg = "No matched forecast-outcome pairs"
        raise ScoringError(msg)

    base_rate = sum(actual for _, actual in pairs) / n
    uncertainty = base_rate * (1.0 - base_rate)

    bins = _bin_forecasts(pairs)
    reliability = _calc_reliability(bins, n)
    resolution = _calc_resolution(bins, n, base_rate)
    overall = reliability - resolution + uncertainty

    return BrierDecomposition(
        reliability=round(reliability, 6),
        resolution=round(resolution, 6),
        uncertainty=round(uncertainty, 6),
        overall=round(overall, 6),
    )


def _bin_forecasts(
    pairs: list[tuple[float, float]],
    *,
    num_bins: int = 10,
) -> dict[int, list[tuple[float, float]]]:
    bins: dict[int, list[tuple[float, float]]] = {}
    for prob, actual in pairs:
        idx = min(int(prob * num_bins), num_bins - 1)
        bins.setdefault(idx, []).append((prob, actual))
    return bins


def _calc_reliability(
    bins: dict[int, list[tuple[float, float]]],
    n: int,
) -> float:
    total = 0.0
    for items in bins.values():
        nk = len(items)
        avg_prob = sum(p for p, _ in items) / nk
        avg_outcome = sum(a for _, a in items) / nk
        total += nk * (avg_prob - avg_outcome) ** 2
    return total / n


def _calc_resolution(
    bins: dict[int, list[tuple[float, float]]],
    n: int,
    base_rate: float,
) -> float:
    total = 0.0
    for items in bins.values():
        nk = len(items)
        avg_outcome = sum(a for _, a in items) / nk
        total += nk * (avg_outcome - base_rate) ** 2
    return total / n
