import json
import logging
import re

logger = logging.getLogger(__name__)

_JSON_ARRAY_PATTERN = re.compile(r"(\[\s*{.*?}\s*\])", re.DOTALL)
_CODE_BLOCK_PATTERN = re.compile(r"```json(.*?)```", re.DOTALL)


def extract_json_array(text: str) -> list[dict] | None:
    result = _try_strict_json(text)
    if result is not None:
        return result

    result = _try_code_block(text)
    if result is not None:
        return result

    return _try_json5_fallback(text)


def _try_strict_json(text: str) -> list[dict] | None:
    try:
        match = _JSON_ARRAY_PATTERN.search(text)
        if match:
            return json.loads(match.group(1))
    except json.JSONDecodeError:
        pass
    return None


def _try_code_block(text: str) -> list[dict] | None:
    try:
        match = _CODE_BLOCK_PATTERN.search(text)
        if match:
            return json.loads(match.group(1).strip())
    except json.JSONDecodeError:
        pass
    return None


def _try_json5_fallback(text: str) -> list[dict] | None:
    try:
        import json5
        return json5.loads(text)
    except Exception:
        logger.debug("json5 fallback failed for text: %.100s...", text)
        return None
