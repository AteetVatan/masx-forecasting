from __future__ import annotations

import logging
import uuid
from datetime import UTC, date, datetime

from core.domain.agents.doctrine_council import CouncilResult, run_doctrine_council
from core.domain.agents.ports import DoctrineAgentPort, EvidenceRetrievalPort
from core.domain.agents.question_generator import generate_strategic_questions
from core.domain.constants import DoctrineDomain, ForecastStatus
from core.domain.exceptions import ForecastError
from core.domain.forecast_models import Evidence, Forecast
from core.llm.ports import LLMClientPort

logger = logging.getLogger(__name__)


def generate_forecast(
    event: str,
    *,
    horizon: date,
    domain: DoctrineDomain,
    llm: LLMClientPort,
    evidence_port: EvidenceRetrievalPort,
    doctrine_agents: list[DoctrineAgentPort],
    base_rate: float | None = None,
) -> Forecast:
    evidence = _retrieve_evidence(event, evidence_port)
    questions = _generate_questions(event, evidence, llm)
    council = _run_council(questions, evidence, doctrine_agents)
    probability = _estimate_probability(
        event, council, llm, base_rate=base_rate,
    )
    return _build_forecast(
        event, horizon, domain, probability,
        evidence, questions, council, doctrine_agents,
        base_rate=base_rate,
    )


def _retrieve_evidence(
    event: str,
    port: EvidenceRetrievalPort,
) -> list[Evidence]:
    try:
        return port.retrieve(event, top_k=10)
    except Exception as e:
        logger.warning("Evidence retrieval failed: %s", e)
        return []


def _generate_questions(
    event: str,
    evidence: list[Evidence],
    llm: LLMClientPort,
) -> list[str]:
    return generate_strategic_questions(
        event, evidence, llm_call=llm.call, max_questions=8,
    )


def _run_council(
    questions: list[str],
    evidence: list[Evidence],
    agents: list[DoctrineAgentPort],
) -> CouncilResult:
    return run_doctrine_council(questions, evidence, agents)


def _estimate_probability(
    event: str,
    council: CouncilResult,
    llm: LLMClientPort,
    *,
    base_rate: float | None,
) -> float:
    prompt = _build_probability_prompt(event, council, base_rate)
    raw = llm.call(prompt)
    return _parse_probability(raw)


def _build_probability_prompt(
    event: str,
    council: CouncilResult,
    base_rate: float | None,
) -> str:
    base_rate_str = (
        f"The reference-class base rate is {base_rate:.0%}.\n"
        if base_rate is not None else ""
    )
    return (
        "You are a calibrated probabilistic forecaster trained in "
        "superforecasting methodology.\n\n"
        f"Event: {event}\n\n"
        f"{base_rate_str}"
        f"Doctrine council analysis:\n{council.synthesis}\n\n"
        "Provide your probability estimate as a single decimal (0.00-1.00). "
        "Think step by step: outside view first, then inside view adjustments. "
        "Respond with ONLY the number."
    )


def _parse_probability(raw: str) -> float:
    cleaned = raw.strip().strip("%")
    try:
        value = float(cleaned)
        if value > 1.0:
            value = value / 100.0
        return max(0.01, min(0.99, value))
    except ValueError as e:
        msg = f"Failed to parse probability from LLM: {raw!r}"
        raise ForecastError(msg) from e


def _build_forecast(
    event: str,
    horizon: date,
    domain: DoctrineDomain,
    probability: float,
    evidence: list[Evidence],
    questions: list[str],
    council: CouncilResult,
    doctrine_agents: list[DoctrineAgentPort],
    *,
    base_rate: float | None,
) -> Forecast:
    return Forecast(
        id=f"fc_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
        event=event,
        horizon=horizon,
        probability=probability,
        key_drivers=questions[:5],
        disconfirming_evidence=[
            q for q in questions[5:] if q
        ],
        update_triggers=_extract_triggers(council),
        evidence=evidence,
        sources=[e.source for e in evidence],
        domain=domain,
        doctrine_agents_used=[a.doctrine_id for a in doctrine_agents],
        base_rate=base_rate,
        status=ForecastStatus.OPEN,
    )


def _extract_triggers(council: CouncilResult) -> list[str]:
    triggers: list[str] = []
    for analysis in council.analyses:
        if len(analysis.response) > 50:
            triggers.append(
                f"[{analysis.agent_id}] watch for: {analysis.response[:80]}..."
            )
    return triggers[:5]
