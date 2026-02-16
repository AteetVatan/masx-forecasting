from __future__ import annotations

import logging
from pathlib import Path

import chromadb
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from core.config.paths import Paths
from core.config.settings import get_settings

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "masx_doctrines"


def load_or_build_index(
    *,
    documents: list[Document] | None = None,
    persist_dir: Path | None = None,
) -> VectorStoreIndex:
    persist_dir = persist_dir or Paths.VECTOR_DIR
    persist_dir.mkdir(parents=True, exist_ok=True)

    chroma_client = _create_chroma_client(persist_dir)
    vector_store = _create_vector_store(chroma_client)
    embed_model = _create_embed_model()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    if documents:
        node_parser = _create_node_parser()
        logger.info(
            "Building index from %d documents (chunk_size=%d, overlap=%d)",
            len(documents), node_parser.chunk_size, node_parser.chunk_overlap,
        )
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            embed_model=embed_model,
            transformations=[node_parser],
            show_progress=True,
        )
        logger.info("Index built and persisted to %s", persist_dir)
        return index

    logger.info("Loading existing index from %s", persist_dir)
    return VectorStoreIndex.from_vector_store(
        vector_store,
        embed_model=embed_model,
    )


def _create_chroma_client(persist_dir: Path) -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=str(persist_dir))


def _create_vector_store(client: chromadb.ClientAPI) -> ChromaVectorStore:
    collection = client.get_or_create_collection(name=_COLLECTION_NAME)
    return ChromaVectorStore(chroma_collection=collection)


def _create_embed_model() -> OpenAIEmbedding:
    settings = get_settings()
    return OpenAIEmbedding(
        model=settings.llamaindex_embed_model,
        api_key=settings.openai_api_key,
    )


def _create_node_parser() -> SentenceSplitter:
    settings = get_settings()
    return SentenceSplitter(
        chunk_size=settings.llamaindex_chunk_size,
        chunk_overlap=settings.llamaindex_chunk_overlap,
    )
