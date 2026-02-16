from __future__ import annotations

import logging

from llama_index.core import VectorStoreIndex

from core.domain.constants import DEFAULT_RAG_RESPONSE_MODE, DEFAULT_SIMILARITY_TOP_K
from core.domain.forecast_models import Evidence
from integrations.llamaindex.index_builder import load_or_build_index

logger = logging.getLogger(__name__)


class LlamaIndexEvidenceRetriever:
    def __init__(self, *, index: VectorStoreIndex | None = None) -> None:
        self._index = index

    def retrieve(self, query: str, *, top_k: int = DEFAULT_SIMILARITY_TOP_K) -> list[Evidence]:
        index = self._get_index()
        retriever = index.as_retriever(similarity_top_k=top_k)
        nodes = retriever.retrieve(query)
        return _nodes_to_evidence(nodes)

    def _get_index(self) -> VectorStoreIndex:
        if self._index is None:
            self._index = load_or_build_index()
        return self._index


def _nodes_to_evidence(nodes: list) -> list[Evidence]:
    results: list[Evidence] = []
    for node_with_score in nodes:
        node = node_with_score.node
        metadata = node.metadata or {}
        source = metadata.get("source_filename", metadata.get("file_path", "unknown"))
        slug = metadata.get("doctrine_slug", "")
        if slug:
            source = f"{slug} ({source})"

        results.append(Evidence(
            source=source,
            snippet=node.get_content()[:500],
            relevance_score=_normalize_score(node_with_score.score),
        ))
    return results


def _normalize_score(score: float | None) -> float:
    if score is None:
        return 0.5
    return max(0.0, min(1.0, score))
