from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.domain.agents.ports import DoctrineAgentPort
from core.domain.forecast_models import DoctrinePack, Evidence
from core.llm.ports import LLMClientPort

if TYPE_CHECKING:
    from llama_index.core.tools import QueryEngineTool

logger = logging.getLogger(__name__)

_RAG_SECTION_HEADER = "Source doctrine passages"
_NO_EVIDENCE = "No evidence provided."
_NO_PRINCIPLES = "No specific principles."


class DoctrineAgentAdapter:
    def __init__(
        self,
        *,
        llm: LLMClientPort,
        pack: DoctrinePack,
        query_tool: QueryEngineTool | None = None,
    ) -> None:
        self._llm = llm
        self._pack = pack
        self._query_tool = query_tool

    @property
    def doctrine_id(self) -> str:
        return self._pack.doctrine_id

    def analyze(self, question: str, evidence: list[Evidence]) -> str:
        rag_context = self._retrieve_rag_context(question)
        prompt = self._build_prompt(question, evidence, rag_context=rag_context)
        return self._llm.call(prompt)

    def _retrieve_rag_context(self, question: str) -> str:
        if not self._query_tool:
            return ""
        try:
            result = self._query_tool.call(question)
            return str(result).strip()
        except Exception:
            logger.warning(
                "RAG retrieval failed for doctrine '%s'",
                self._pack.doctrine_id,
                exc_info=True,
            )
            return ""

    def _build_prompt(
        self,
        question: str,
        evidence: list[Evidence],
        *,
        rag_context: str,
    ) -> str:
        evidence_text = "\n".join(
            f"- {e.snippet}" for e in evidence[:5]
        ) or _NO_EVIDENCE

        principles = "\n".join(
            f"- {p}" for p in self._pack.principles[:5]
        ) or _NO_PRINCIPLES

        rag_block = ""
        if rag_context:
            rag_block = f"\n{_RAG_SECTION_HEADER}:\n{rag_context}\n"

        return (
            f"You are analyzing through the lens of {self._pack.name}.\n\n"
            f"Core principles:\n{principles}\n\n"
            f"Evidence:\n{evidence_text}\n"
            f"{rag_block}\n"
            f"Question: {question}\n\n"
            "Provide a concise analysis (3-5 sentences) with specific references "
            "to evidence and doctrine sources. Identify key risks and opportunities."
        )
