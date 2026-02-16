from tiktoken import get_encoding

from core.domain.constants import DEFAULT_CHUNK_SIZE

_ENCODING = None


def _get_encoding():
    global _ENCODING
    if _ENCODING is None:
        _ENCODING = get_encoding("cl100k_base")
    return _ENCODING


def split_text(text: str, *, max_tokens: int = DEFAULT_CHUNK_SIZE) -> list[str]:
    enc = _get_encoding()
    tokens = enc.encode(text)
    token_chunks = [tokens[i : i + max_tokens] for i in range(0, len(tokens), max_tokens)]
    return [enc.decode(chunk) for chunk in token_chunks]
