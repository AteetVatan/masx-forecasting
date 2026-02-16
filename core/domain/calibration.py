from __future__ import annotations

from dataclasses import dataclass, field

from core.domain.constants import DoctrineDomain
from core.domain.forecast_models import Forecast, Outcome
from core.domain.scoring import brier_score


@dataclass
class CalibrationBin:
    bin_center: float
    predicted_avg: float
    hit_rate: float
    count: int


@dataclass
class CalibrationReport:
    bins: list[CalibrationBin] = field(default_factory=list)
    domain_scores: dict[str, float] = field(default_factory=dict)
    agent_scores: dict[str, float] = field(default_factory=dict)


def build_calibration_report(
    forecasts: list[Forecast],
    outcomes: list[Outcome],
    *,
    num_bins: int = 10,
) -> CalibrationReport:
    outcome_map = {o.forecast_id: o.resolved for o in outcomes}
    matched = _match_pairs(forecasts, outcome_map)
    bins = _compute_bins(matched, num_bins=num_bins)
    domain_scores = _scores_by_domain(matched)
    agent_scores = _scores_by_agent(matched)
    return CalibrationReport(
        bins=bins,
        domain_scores=domain_scores,
        agent_scores=agent_scores,
    )


def _match_pairs(
    forecasts: list[Forecast],
    outcome_map: dict[str, bool],
) -> list[tuple[Forecast, bool]]:
    return [
        (fc, outcome_map[fc.id])
        for fc in forecasts
        if fc.id in outcome_map
    ]


def _compute_bins(
    matched: list[tuple[Forecast, bool]],
    *,
    num_bins: int = 10,
) -> list[CalibrationBin]:
    buckets: dict[int, list[tuple[float, bool]]] = {}
    for fc, outcome in matched:
        idx = min(int(fc.probability * num_bins), num_bins - 1)
        buckets.setdefault(idx, []).append((fc.probability, outcome))

    result: list[CalibrationBin] = []
    for idx in sorted(buckets):
        items = buckets[idx]
        count = len(items)
        predicted_avg = sum(p for p, _ in items) / count
        hit_rate = sum(1.0 for _, o in items if o) / count
        result.append(CalibrationBin(
            bin_center=(idx + 0.5) / num_bins,
            predicted_avg=round(predicted_avg, 4),
            hit_rate=round(hit_rate, 4),
            count=count,
        ))
    return result


def _scores_by_domain(
    matched: list[tuple[Forecast, bool]],
) -> dict[str, float]:
    groups: dict[str, list[float]] = {}
    for fc, outcome in matched:
        score = brier_score(fc.probability, outcome=outcome)
        groups.setdefault(fc.domain.value, []).append(score)
    return {
        domain: round(sum(scores) / len(scores), 6)
        for domain, scores in groups.items()
    }


def _scores_by_agent(
    matched: list[tuple[Forecast, bool]],
) -> dict[str, float]:
    groups: dict[str, list[float]] = {}
    for fc, outcome in matched:
        score = brier_score(fc.probability, outcome=outcome)
        for agent in fc.doctrine_agents_used:
            groups.setdefault(agent, []).append(score)
    return {
        agent: round(sum(scores) / len(scores), 6)
        for agent, scores in groups.items()
    }
