from __future__ import annotations

import logging

import httpx

from core.domain.agents.ports import EvidenceRetrievalPort
from core.domain.forecast_models import Evidence

logger = logging.getLogger(__name__)

_GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"
_REQUEST_TIMEOUT = 30.0


class GdeltEvidenceAdapter:
    def __init__(self, *, timeout: float = _REQUEST_TIMEOUT) -> None:
        self._timeout = timeout

    def retrieve(self, query: str, *, top_k: int = 10) -> list[Evidence]:
        articles = self._fetch_articles(query, max_records=top_k)
        return [_article_to_evidence(a) for a in articles]

    def _fetch_articles(
        self,
        query: str,
        *,
        max_records: int = 10,
    ) -> list[dict]:
        params = {
            "query": query,
            "mode": "artlist",
            "maxrecords": str(max_records),
            "format": "json",
        }
        try:
            response = httpx.get(
                _GDELT_DOC_API, params=params, timeout=self._timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("articles", [])
        except (httpx.HTTPError, ValueError) as e:
            logger.warning("GDELT API query failed: %s", e)
            return []


def _article_to_evidence(article: dict) -> Evidence:
    return Evidence(
        source=article.get("url", "unknown"),
        snippet=article.get("title", "No title"),
        relevance_score=min(1.0, article.get("socialimage", 0.5)),
    )
