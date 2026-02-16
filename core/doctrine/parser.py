import json
import logging
import re

from core.domain.models import DoctrineChunk, ChunkMeta

logger = logging.getLogger(__name__)

_SECTION_PATTERN = re.compile(
    r'{\s*"section"\s*:[\s\S]+?}', re.DOTALL
)
_MARKDOWN_PATTERN = re.compile(
    r"\*\*Section:\*\* (.*?)\n\*\*Text:\*\*\n(.*?)(?=\n###|$)",
    re.DOTALL,
)


def convert_text_to_chunks(raw_text: str) -> list[dict]:
    chunks = _try_json_parse(raw_text)
    if chunks:
        return chunks
    return _parse_markdown_fallback(raw_text)


def _try_json_parse(raw_text: str) -> list[dict]:
    match = _SECTION_PATTERN.search(raw_text)
    if not match:
        return []

    parsed = safe_parse_llm_chunk(match.group())
    if parsed:
        return [normalize_chunk(parsed, idx=1)]
    return []


def _parse_markdown_fallback(raw_text: str) -> list[dict]:
    matches = _MARKDOWN_PATTERN.findall(raw_text)
    chunks = []
    for idx, (section, text) in enumerate(matches, 1):
        chunk = DoctrineChunk(
            id=f"chunk_{idx:03}",
            section=section.strip(),
            text=text.strip(),
            meta=ChunkMeta(chunk_index=idx),
        )
        chunks.append(chunk.model_dump())
    return chunks


def normalize_chunk(parsed: dict, *, idx: int) -> dict:
    meta_raw = parsed.get("meta", {})
    chunk = DoctrineChunk(
        id=f"chunk_{idx:03}",
        section=str(parsed.get("section", "")).strip(),
        text=str(parsed.get("text", "")).strip(),
        meta=ChunkMeta(
            theme=meta_raw.get("theme", "unspecified"),
            region=meta_raw.get("region", "unspecified"),
            use_case=meta_raw.get("use_case", "doctrine_selector"),
            strategic_category=meta_raw.get("strategic_category", {}),
            economic_category=meta_raw.get("economic_category", {}),
            civilizational_category=meta_raw.get("civilizational_category", {}),
            usage_tags=meta_raw.get("usage_tags", []),
            influence_map=meta_raw.get(
                "influence_map",
                {"influenced_works": [], "modern_applications": []},
            ),
            chunk_index=idx,
        ),
    )
    return chunk.model_dump()


def safe_parse_llm_chunk(raw_json_str: str) -> dict | None:
    if not raw_json_str:
        return None

    raw = _clean_json_string(raw_json_str)
    raw = _fix_common_json_issues(raw)
    raw = _balance_braces(raw)

    return _parse_with_fallbacks(raw)


def _clean_json_string(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"```json\s*|\s*```", "", raw)
    raw = re.sub(r"^[^{]*", "", raw)
    raw = re.sub(r"[^}]*$", "", raw)
    return raw


def _fix_common_json_issues(raw: str) -> str:
    raw = re.sub(r",\s*([}\]])", r"\1", raw)
    raw = re.sub(r"([{,]\s*)(\w+)(\s*:)", r'\1"\2"\3', raw)
    raw = re.sub(r"'", '"', raw)
    return raw


def _balance_braces(raw: str) -> str:
    opens = raw.count("{")
    closes = raw.count("}")
    if closes < opens:
        raw += "}" * (opens - closes)
    elif closes > opens:
        raw = "{" * (closes - opens) + raw
    return raw


def _parse_with_fallbacks(raw: str) -> dict | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    try:
        wrapped = raw if raw.startswith("[") else f"[{raw}]"
        return json.loads(wrapped)[0]
    except json.JSONDecodeError:
        pass

    text_match = re.search(r'"text"\s*:\s*"([^"]*)"', raw)
    if text_match:
        return {
            "section": "Extracted Content",
            "text": text_match.group(1),
            "meta": {"theme": "unspecified", "region": "unspecified", "use_case": "doctrine_selector"},
        }

    logger.debug("Failed to parse LLM chunk: %.100s...", raw)
    return None
