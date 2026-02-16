from __future__ import annotations

import logging
from dataclasses import dataclass, field

from core.domain.agents.ports import DoctrineAgentPort
from core.domain.forecast_models import Evidence

logger = logging.getLogger(__name__)


@dataclass
class CouncilAnalysis:
    agent_id: str
    response: str


@dataclass
class CouncilResult:
    analyses: list[CouncilAnalysis] = field(default_factory=list)
    synthesis: str = ""


def run_doctrine_council(
    questions: list[str],
    evidence: list[Evidence],
    agents: list[DoctrineAgentPort],
) -> CouncilResult:
    analyses = _collect_analyses(questions, evidence, agents)
    synthesis = _synthesize(analyses)
    return CouncilResult(analyses=analyses, synthesis=synthesis)


def _collect_analyses(
    questions: list[str],
    evidence: list[Evidence],
    agents: list[DoctrineAgentPort],
) -> list[CouncilAnalysis]:
    combined_question = "\n".join(f"- {q}" for q in questions)
    results: list[CouncilAnalysis] = []
    for agent in agents:
        try:
            response = agent.analyze(combined_question, evidence)
            results.append(CouncilAnalysis(
                agent_id=agent.doctrine_id,
                response=response,
            ))
        except Exception:
            logger.warning(
                "Doctrine agent '%s' failed during council",
                agent.doctrine_id,
                exc_info=True,
            )
    return results


def _synthesize(analyses: list[CouncilAnalysis]) -> str:
    if not analyses:
        return "No doctrine agent responses available."
    lines = [
        f"[{a.agent_id}]: {a.response[:200]}"
        for a in analyses
    ]
    return "\n\n".join(lines)
