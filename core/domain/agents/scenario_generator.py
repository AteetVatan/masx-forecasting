from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from core.domain.agents.ports import DoctrineAgentPort
from core.domain.constants import DoctrineDomain, ScenarioStatus
from core.domain.forecast_models import Evidence, Scenario, Signpost
from core.llm.ports import LLMClientPort

logger = logging.getLogger(__name__)


def generate_scenarios(
    topic: str,
    evidence: list[Evidence],
    *,
    llm: LLMClientPort,
    doctrine_agents: list[DoctrineAgentPort],
    domain: DoctrineDomain | None = None,
    num_scenarios: int = 4,
) -> list[Scenario]:
    prompt = _build_scenario_prompt(topic, evidence, num_scenarios)
    raw = llm.call(prompt)
    scenarios = _parse_scenarios(raw, topic, domain, num_scenarios)
    return scenarios


def _build_scenario_prompt(
    topic: str,
    evidence: list[Evidence],
    num_scenarios: int,
) -> str:
    evidence_str = "\n".join(
        f"- {e.snippet}" for e in evidence[:8]
    ) or "No evidence provided."
    return (
        "You are a strategic scenario planner using Shell International's "
        "methodology.\n\n"
        f"Topic: {topic}\n\n"
        f"Evidence:\n{evidence_str}\n\n"
        f"Generate {num_scenarios} plausible future scenarios. "
        "For each scenario provide:\n"
        "1. Title (one line)\n"
        "2. Narrative (2-3 sentences)\n"
        "3. Probability weight (0.0-1.0, should roughly sum to 1)\n"
        "4. Key assumptions (2-3 bullet points)\n"
        "5. Early warning signals (2-3 observable indicators)\n\n"
        "Format each scenario clearly with headers."
    )


def _parse_scenarios(
    raw: str,
    topic: str,
    domain: DoctrineDomain | None,
    num_scenarios: int,
) -> list[Scenario]:
    timestamp = datetime.now(UTC).strftime("%Y%m%d")
    scenarios: list[Scenario] = []
    sections = raw.split("\n\n")

    weight = round(1.0 / max(num_scenarios, 1), 2)
    for i, section in enumerate(sections[:num_scenarios]):
        if not section.strip():
            continue
        scenario_id = f"sc_{timestamp}_{uuid.uuid4().hex[:6]}"
        lines = section.strip().split("\n")
        title = lines[0].strip().lstrip("#- ") if lines else f"Scenario {i + 1}"

        scenarios.append(Scenario(
            id=scenario_id,
            title=title,
            narrative=section.strip(),
            probability_weight=weight,
            domain=domain,
            status=ScenarioStatus.ACTIVE,
        ))
    return scenarios if scenarios else [_fallback_scenario(topic, domain)]


def _fallback_scenario(
    topic: str,
    domain: DoctrineDomain | None,
) -> Scenario:
    return Scenario(
        id=f"sc_{datetime.now(UTC).strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}",
        title=f"Baseline: {topic}",
        narrative="Status quo continues with no major disruption.",
        probability_weight=1.0,
        domain=domain,
        status=ScenarioStatus.ACTIVE,
    )
