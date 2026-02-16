from __future__ import annotations

import logging

from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters

from core.domain.constants import DEFAULT_RAG_RESPONSE_MODE, DEFAULT_SIMILARITY_TOP_K
from integrations.llamaindex.index_builder import load_or_build_index

logger = logging.getLogger(__name__)

_METADATA_KEY_SLUG = "doctrine_slug"


def build_doctrine_tools(
    *,
    index: VectorStoreIndex | None = None,
    top_k: int = DEFAULT_SIMILARITY_TOP_K,
) -> list[QueryEngineTool]:
    index = index or load_or_build_index()
    slugs = _extract_unique_slugs(index)

    tools: list[QueryEngineTool] = []
    for slug in sorted(slugs):
        tool = _create_tool_for_doctrine(index, slug, top_k=top_k)
        if tool:
            tools.append(tool)

    logger.info("Built %d doctrine query tools", len(tools))
    return tools


def _extract_unique_slugs(index: VectorStoreIndex) -> set[str]:
    try:
        docstore = index.docstore
        slugs: set[str] = set()
        for doc_id in docstore.docs:
            doc = docstore.docs[doc_id]
            slug = doc.metadata.get(_METADATA_KEY_SLUG, "")
            if slug:
                slugs.add(slug)
        return slugs
    except Exception:
        logger.warning("Could not extract slugs from docstore, returning empty set")
        return set()


def _create_tool_for_doctrine(
    index: VectorStoreIndex,
    slug: str,
    *,
    top_k: int,
) -> QueryEngineTool | None:
    try:
        filters = MetadataFilters(
            filters=[
                MetadataFilter(key=_METADATA_KEY_SLUG, value=slug),
            ]
        )
        engine = index.as_query_engine(
            similarity_top_k=top_k,
            filters=filters,
            response_mode=DEFAULT_RAG_RESPONSE_MODE,
        )
        pretty_name = slug.replace("_", " ").title()
        return QueryEngineTool(
            query_engine=engine,
            metadata=ToolMetadata(
                name=slug,
                description=f"Query the '{pretty_name}' doctrine for strategic analysis, principles, historical context, and insights.",
            ),
        )
    except Exception as e:
        logger.error("Failed to create tool for doctrine '%s': %s", slug, e)
        return None
