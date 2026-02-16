from __future__ import annotations

import logging
import re
from collections import defaultdict
from pathlib import Path

from llama_index.core.schema import Document
from llama_index.readers.file import PyMuPDFReader

from core.config.paths import Paths

logger = logging.getLogger(__name__)

_PART_SUFFIX_PATTERN = re.compile(r"[-_](\d+)$")

_METADATA_KEY_SLUG = "doctrine_slug"
_METADATA_KEY_FILENAME = "source_filename"
_METADATA_KEY_PART = "part_index"


def read_doctrine_documents(
    *,
    raw_dir: Path | None = None,
) -> list[Document]:
    raw_dir = raw_dir or Paths.RAW_DIR
    pdf_files = sorted(raw_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in %s", raw_dir)
        return []

    grouped = _group_by_doctrine(pdf_files)
    reader = PyMuPDFReader()
    documents: list[Document] = []

    for slug, paths in grouped.items():
        docs = _read_doctrine_group(reader, slug, paths)
        documents.extend(docs)
        logger.info(
            "Read doctrine '%s': %d files → %d documents",
            slug, len(paths), len(docs),
        )

    logger.info("Total: %d documents from %d doctrines", len(documents), len(grouped))
    return documents


def _group_by_doctrine(pdf_files: list[Path]) -> dict[str, list[Path]]:
    grouped: dict[str, list[Path]] = defaultdict(list)
    for pdf in pdf_files:
        slug = _extract_slug(pdf.stem)
        grouped[slug].append(pdf)
    return dict(sorted(grouped.items()))


def _extract_slug(stem: str) -> str:
    return _PART_SUFFIX_PATTERN.sub("", stem.lower())


def _read_doctrine_group(
    reader: PyMuPDFReader,
    slug: str,
    paths: list[Path],
) -> list[Document]:
    docs: list[Document] = []
    for part_idx, pdf_path in enumerate(sorted(paths), start=1):
        try:
            part_docs = reader.load_data(file_path=pdf_path)
            for doc in part_docs:
                doc.metadata[_METADATA_KEY_SLUG] = slug
                doc.metadata[_METADATA_KEY_FILENAME] = pdf_path.name
                doc.metadata[_METADATA_KEY_PART] = part_idx
            docs.extend(part_docs)
        except Exception as e:
            logger.error(
                "Failed to read PDF '%s': %s", pdf_path.name, e,
            )
    return docs
