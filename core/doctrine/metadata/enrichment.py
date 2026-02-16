import json
import logging
from collections import defaultdict
from pathlib import Path

from core.domain.constants import DoctrineStatus

logger = logging.getLogger(__name__)


def enrich_metadata_from_chunks(
    meta_path: Path,
    all_chunks: list[dict],
) -> None:
    doctrine_meta = _load_meta(meta_path)
    aggregated = _aggregate_chunk_metadata(all_chunks)

    doctrine_meta.update(aggregated)
    doctrine_meta["status"] = DoctrineStatus.TAGGED.value

    _save_meta(meta_path, doctrine_meta)


def _load_meta(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _save_meta(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _aggregate_chunk_metadata(chunks: list[dict]) -> dict:
    strategic: defaultdict[str, set] = defaultdict(set)
    economic: defaultdict[str, set] = defaultdict(set)
    civilizational: defaultdict[str, set] = defaultdict(set)
    influenced_works: set[str] = set()
    modern_apps: set[str] = set()
    usage_tags: set[str] = set()
    regions: set[str] = set()

    for chunk in chunks:
        meta = chunk.get("meta", {})
        regions.add(meta.get("region", ""))
        usage_tags.add(meta.get("use_case", ""))
        strategic["strategic_category"].update(meta.get("strategic_category", {}))
        economic["economic_category"].update(meta.get("economic_category", {}))
        civilizational["civilizational_category"].update(
            meta.get("civilizational_category", {})
        )
        _collect_influence(meta, influenced_works, modern_apps)

    return {
        "strategic_category": list(set().union(*strategic.values())),
        "economic_category": list(set().union(*economic.values())),
        "civilizational_category": list(set().union(*civilizational.values())),
        "usage_tags": list(usage_tags),
        "origin_civilization": list(regions),
        "influence_map": {
            "influenced_works": list(influenced_works),
            "modern_applications": list(modern_apps),
        },
    }


def _collect_influence(
    meta: dict, works: set[str], apps: set[str]
) -> None:
    influence = meta.get("influence_map")
    if isinstance(influence, dict):
        works.update(influence.get("influenced_works", []))
        apps.update(influence.get("modern_applications", []))
