from __future__ import annotations

import json
import logging
from pathlib import Path

from core.domain.exceptions import FileProcessingError
from core.domain.forecast_models import Forecast, Outcome

logger = logging.getLogger(__name__)

_DEFAULT_DIR = Path("data/forecasts")


class ForecastStore:
    def __init__(self, *, storage_dir: Path = _DEFAULT_DIR) -> None:
        self._dir = storage_dir
        self._forecasts_file = self._dir / "forecasts.json"
        self._outcomes_file = self._dir / "outcomes.json"

    def save_forecast(self, forecast: Forecast) -> None:
        forecasts = self._load_forecasts()
        forecasts.append(forecast.model_dump(mode="json"))
        self._write(self._forecasts_file, forecasts)
        logger.info("Saved forecast %s", forecast.id)

    def save_outcome(self, outcome: Outcome) -> None:
        outcomes = self._load_outcomes()
        outcomes.append(outcome.model_dump(mode="json"))
        self._write(self._outcomes_file, outcomes)
        logger.info("Saved outcome for forecast %s", outcome.forecast_id)

    def load_forecasts(self) -> list[Forecast]:
        raw = self._load_forecasts()
        return [Forecast.model_validate(item) for item in raw]

    def load_outcomes(self) -> list[Outcome]:
        raw = self._load_outcomes()
        return [Outcome.model_validate(item) for item in raw]

    def _load_forecasts(self) -> list[dict]:
        return self._read(self._forecasts_file)

    def _load_outcomes(self) -> list[dict]:
        return self._read(self._outcomes_file)

    def _read(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            msg = f"Failed to read {path}"
            raise FileProcessingError(msg) from e

    def _write(self, path: Path, data: list[dict]) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data, indent=2, default=str),
            encoding="utf-8",
        )
