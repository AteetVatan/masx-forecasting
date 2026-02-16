import json
import logging
import time

from core.config.paths import Paths
from core.domain.constants import ResponseType
from core.domain.exceptions import DoctrineProcessingError
from core.doctrine.parser import convert_text_to_chunks
from core.doctrine.text_splitter import split_text
from core.llm.ports import LLMClientPort
from core.prompts.prompts import Prompts

logger = logging.getLogger(__name__)

_BATCH_SIZE = 3
_BATCH_DELAY_SECONDS = 5


class ChunkAndEnrich:
    @staticmethod
    def process(
        slug: str,
        clients: list[LLMClientPort],
        *,
        embedded_prompt: str = Prompts.CHUNK_AND_ENRICH_PROMPT,
        system_prompt: str = Prompts.SYSTEM_ROLE_PROMPT,
    ) -> None:
        chunk_path = Paths.CHUNK_DIR / f"{slug}_chunks.json"
        if chunk_path.exists():
            logger.info("Skipping %s — already chunked", slug)
            return

        cleaned_path = Paths.CLEANED_DIR / f"{slug}.md"
        full_text = cleaned_path.read_text(encoding="utf-8")

        segments = split_text(full_text, max_tokens=1000)
        batches = [segments[i : i + _BATCH_SIZE] for i in range(0, len(segments), _BATCH_SIZE)]

        all_chunks = _process_batches(slug, batches, clients, embedded_prompt, system_prompt)
        _assign_ids(slug, all_chunks)
        _save_chunks(chunk_path, all_chunks)


def _process_batches(
    slug: str,
    batches: list[list[str]],
    clients: list[LLMClientPort],
    embedded_prompt: str,
    system_prompt: str,
) -> list[dict]:
    all_chunks: list[dict] = []

    for batch_idx, batch in enumerate(batches):
        chunks = _try_clients(slug, batch_idx, len(batches), batch, clients, embedded_prompt, system_prompt)
        all_chunks.extend(chunks)
        time.sleep(_BATCH_DELAY_SECONDS)

    return all_chunks


def _try_clients(
    slug: str,
    batch_idx: int,
    total_batches: int,
    batch: list[str],
    clients: list[LLMClientPort],
    embedded_prompt: str,
    system_prompt: str,
) -> list[dict]:
    for client_idx, client in enumerate(clients):
        try:
            logger.info("[%s] batch %d/%d via client %d", slug, batch_idx + 1, total_batches, client_idx)

            response = client.call_batch(batch, embedded_prompt, system_prompt)

            if response.response_type == ResponseType.JSON:
                chunks = response.content if isinstance(response.content, list) else []
            else:
                chunks = convert_text_to_chunks(str(response.content))

            if not chunks:
                raise DoctrineProcessingError("Empty chunk response")
            return chunks

        except Exception as e:
            logger.warning("[%s] batch %d client %d failed: %s", slug, batch_idx + 1, client_idx, e)
            if client_idx == len(clients) - 1:
                logger.error("[%s] batch %d: all clients exhausted", slug, batch_idx + 1)

    return []


def _assign_ids(slug: str, chunks: list[dict]) -> None:
    for idx, chunk in enumerate(chunks):
        chunk["id"] = f"{slug}_{str(idx + 1).zfill(3)}"
        chunk.setdefault("meta", {})["chunk_index"] = idx + 1


def _save_chunks(path, chunks: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    logger.info("Saved %d chunks to %s", len(chunks), path)
