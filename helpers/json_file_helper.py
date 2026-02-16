import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class JsonFileHelper:
    @staticmethod
    def read_data(file_path: str | Path) -> dict | list | None:
        path = Path(file_path)
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("File not found: %s", path)
            return None
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in %s: %s", path, e)
            return None

    @staticmethod
    def write_data(file_path: str | Path, data: dict | list) -> bool:
        path = Path(file_path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            logger.error("Failed to write %s: %s", path, e)
            return False
