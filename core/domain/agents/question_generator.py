from __future__ import annotations

import logging

from core.domain.agents.ports import DoctrineAgentPort, EvidenceRetrievalPort
from core.domain.forecast_models import Evidence

logger = logging.getLogger(__name__)


def generate_strategic_questions(
    event: str,
    evidence: list[Evidence],
    *,
    llm_call: callable,
    max_questions: int = 10,
) -> list[str]:
    evidence_text = _format_evidence(evidence)
    prompt = _build_question_prompt(event, evidence_text, max_questions)
    raw = llm_call(prompt)
    return _parse_questions(raw)


def _format_evidence(evidence: list[Evidence]) -> str:
    lines = [f"- {e.snippet} (source: {e.source})" for e in evidence[:10]]
    return "\n".join(lines) if lines else "No evidence available."


def _build_question_prompt(
    event: str,
    evidence_text: str,
    max_questions: int,
) -> str:
    return (
        f"You are analyzing whether: {event}\n\n"
        f"Evidence:\n{evidence_text}\n\n"
        f"Generate {max_questions} decisive strategic questions that must be answered "
        "to forecast this event. Focus on: base rates, key actors' incentives, "
        "capability vs intent, historical analogues, and disconfirming evidence.\n"
        "Return one question per line, numbered."
    )


def _parse_questions(raw: str) -> list[str]:
    lines = raw.strip().split("\n")
    questions: list[str] = []
    for line in lines:
        cleaned = line.strip().lstrip("0123456789.)- ").strip()
        if cleaned and len(cleaned) > 10:
            questions.append(cleaned)
    return questions
