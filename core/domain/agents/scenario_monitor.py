from __future__ import annotations

import logging
from datetime import UTC, datetime

from core.domain.constants import ScenarioStatus
from core.domain.forecast_models import Evidence, Scenario, Signpost

logger = logging.getLogger(__name__)


def update_signpost(
    signpost: Signpost,
    new_evidence: list[Evidence],
    *,
    threshold: float = 0.5,
) -> Signpost:
    relevant = [
        e for e in new_evidence
        if signpost.indicator.lower() in e.snippet.lower()
    ]
    if not relevant:
        return signpost

    avg_relevance = sum(e.relevance_score for e in relevant) / len(relevant)
    new_status = _determine_status(avg_relevance, threshold)

    return Signpost(
        id=signpost.id,
        description=signpost.description,
        scenario_id=signpost.scenario_id,
        indicator=signpost.indicator,
        current_status=new_status,
        last_checked=datetime.now(UTC),
    )


def update_scenario_weights(
    scenarios: list[Scenario],
    new_evidence: list[Evidence],
    *,
    signal_threshold: float = 0.5,
) -> list[Scenario]:
    updated: list[Scenario] = []
    for scenario in scenarios:
        new_signposts = [
            update_signpost(sp, new_evidence, threshold=signal_threshold)
            for sp in scenario.signposts
        ]
        weight_adjustment = _calc_weight_adjustment(new_signposts)
        new_weight = max(0.01, min(0.99, scenario.probability_weight + weight_adjustment))
        updated.append(scenario.model_copy(update={
            "signposts": new_signposts,
            "probability_weight": round(new_weight, 4),
        }))

    return _normalize_weights(updated)


def check_scenario_alerts(scenarios: list[Scenario]) -> list[str]:
    alerts: list[str] = []
    for s in scenarios:
        if s.probability_weight > 0.5:
            alerts.append(f"Scenario '{s.title}' is dominant (P={s.probability_weight:.0%})")
        confirmed = [sp for sp in s.signposts if sp.current_status == "confirmed"]
        if confirmed:
            alerts.append(
                f"Scenario '{s.title}' has {len(confirmed)} confirmed signpost(s)"
            )
    return alerts


def _determine_status(
    avg_relevance: float,
    threshold: float,
) -> str:
    if avg_relevance >= threshold:
        return "confirmed"
    if avg_relevance >= threshold * 0.5:
        return "emerging"
    return "not_seen"


def _calc_weight_adjustment(signposts: list[Signpost]) -> float:
    if not signposts:
        return 0.0
    confirmed = sum(1 for sp in signposts if sp.current_status == "confirmed")
    emerging = sum(1 for sp in signposts if sp.current_status == "emerging")
    return (confirmed * 0.05 + emerging * 0.02)


def _normalize_weights(scenarios: list[Scenario]) -> list[Scenario]:
    total = sum(s.probability_weight for s in scenarios)
    if total == 0:
        equal = round(1.0 / len(scenarios), 4)
        return [s.model_copy(update={"probability_weight": equal}) for s in scenarios]
    return [
        s.model_copy(update={"probability_weight": round(s.probability_weight / total, 4)})
        for s in scenarios
    ]
