from __future__ import annotations

from typing import Protocol

from core.domain.forecast_models import Evidence


class DoctrineAgentPort(Protocol):
    def analyze(self, question: str, evidence: list[Evidence]) -> str: ...

    @property
    def doctrine_id(self) -> str: ...


class EvidenceRetrievalPort(Protocol):
    def retrieve(self, query: str, *, top_k: int = 10) -> list[Evidence]: ...
