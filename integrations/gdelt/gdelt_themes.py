import logging
from pathlib import Path

import httpx

from helpers.json_file_helper import JsonFileHelper

logger = logging.getLogger(__name__)

_GDELT_THEMES_URL = "http://data.gdeltproject.org/api/v2/guides/LOOKUP-GKGTHEMES.TXT"
_DOWNLOAD_TIMEOUT = 60.0


class GdeltV2Themes:
    def __init__(self) -> None:
        self.themes: list[tuple[str, str]] = []

    @staticmethod
    def download_themes(*, url: str = _GDELT_THEMES_URL, dest: Path) -> None:
        response = httpx.get(url, timeout=_DOWNLOAD_TIMEOUT)
        response.raise_for_status()
        dest.write_text(response.text, encoding="utf-8")
        logger.info("Downloaded GDELT themes to %s", dest)

    @staticmethod
    def load_and_filter(
        themes_file: Path,
        keywords: dict[str, list[str]],
    ) -> list[tuple[str, str]]:
        relevant: list[tuple[str, str]] = []
        with open(themes_file, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                parts = line.strip().split("\t")
                if len(parts) != 2:
                    continue
                theme_code = parts[0].lower()
                match = _match_keyword(theme_code, keywords)
                if match:
                    relevant.append((theme_code, match))
        return relevant

    @staticmethod
    def map_to_categories(themes: list[tuple[str, str]]) -> dict[str, list[dict[str, str]]]:
        categories: dict[str, list[dict[str, str]]] = {}
        for theme_code, category in themes:
            categories.setdefault(category, []).append({"code": theme_code})
        return categories


def _match_keyword(theme_code: str, keywords: dict[str, list[str]]) -> str | None:
    for category, words in keywords.items():
        if any(word.lower() in theme_code for word in words):
            return category
    return None
