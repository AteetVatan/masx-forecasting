from __future__ import annotations

import json
import logging
from pathlib import Path

from core.domain.constants import DoctrineDomain
from core.domain.exceptions import ConfigurationError
from core.domain.forecast_models import DoctrinePack

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "masx_ai" / "data_templates" / "doctrines"


def load_doctrine_pack(doctrine_path: Path) -> DoctrinePack:
    try:
        raw = json.loads(doctrine_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        msg = f"Failed to load doctrine pack from {doctrine_path}"
        raise ConfigurationError(msg) from e

    doctrine_id = doctrine_path.stem
    name = raw.get("name", doctrine_id.replace("_", " ").title())

    return DoctrinePack(
        doctrine_id=doctrine_id,
        name=name,
        principles=raw.get("principles", []),
        heuristics=raw.get("heuristics", []),
        failure_modes=raw.get("failure_modes", []),
        recommended_tools=raw.get("recommended_tools", []),
        domain_fit=_parse_domains(raw.get("domain_fit", [])),
    )


def load_all_doctrine_packs(
    templates_dir: Path = _TEMPLATES_DIR,
) -> list[DoctrinePack]:
    if not templates_dir.exists():
        logger.warning("Doctrine templates directory not found: %s", templates_dir)
        return []
    packs: list[DoctrinePack] = []
    for path in sorted(templates_dir.glob("*.json")):
        try:
            packs.append(load_doctrine_pack(path))
        except ConfigurationError:
            logger.warning("Skipping invalid doctrine pack: %s", path.name)
    logger.info("Loaded %d doctrine packs", len(packs))
    return packs


def _parse_domains(raw_domains: list[str]) -> list[DoctrineDomain]:
    result: list[DoctrineDomain] = []
    for d in raw_domains:
        try:
            result.append(DoctrineDomain(d.lower()))
        except ValueError:
            continue
    return result
