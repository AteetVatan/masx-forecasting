"""CLI entry point for doctrine ingestion pipeline.

Usage:
    python -m integrations.llamaindex.ingest_cli
"""
from __future__ import annotations

import logging
import sys
import time

from core.config.log import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()
    logger.info("Starting doctrine ingestion pipeline")
    start = time.monotonic()

    from integrations.llamaindex.doctrine_reader import read_doctrine_documents
    from integrations.llamaindex.index_builder import load_or_build_index

    documents = read_doctrine_documents()
    if not documents:
        logger.error("No documents found — aborting")
        sys.exit(1)

    logger.info("Ingested %d documents, building vector index...", len(documents))
    index = load_or_build_index(documents=documents)

    elapsed = time.monotonic() - start
    logger.info(
        "Ingestion complete in %.1fs — index ready with %d documents",
        elapsed, len(documents),
    )


if __name__ == "__main__":
    main()
