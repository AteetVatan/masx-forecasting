import pytest
from datetime import date

from core.domain.constants import DoctrineDomain, ForecastStatus
from core.domain.exceptions import ScoringError
from core.domain.forecast_models import BrierDecomposition, Forecast, Outcome
from core.domain.scoring import brier_score, brier_decomposition


class TestBrierScore:
    def test_perfect_prediction_true(self):
        assert brier_score(1.0, outcome=True) == 0.0

    def test_perfect_prediction_false(self):
        assert brier_score(0.0, outcome=False) == 0.0

    def test_worst_prediction_true(self):
        assert brier_score(0.0, outcome=True) == 1.0

    def test_worst_prediction_false(self):
        assert brier_score(1.0, outcome=False) == 1.0

    def test_fifty_fifty(self):
        assert brier_score(0.5, outcome=True) == 0.25
        assert brier_score(0.5, outcome=False) == 0.25

    def test_invalid_probability_raises(self):
        with pytest.raises(ScoringError):
            brier_score(1.5, outcome=True)
        with pytest.raises(ScoringError):
            brier_score(-0.1, outcome=False)


class TestBrierDecomposition:
    def _make_forecast(self, id: str, prob: float) -> Forecast:
        return Forecast(
            id=id,
            event="test event",
            horizon=date(2026, 12, 31),
            probability=prob,
            domain=DoctrineDomain.GEOPOLITICS,
        )

    def test_perfect_calibration(self):
        forecasts = [
            self._make_forecast("f1", 1.0),
            self._make_forecast("f2", 0.0),
        ]
        outcomes = [
            Outcome(forecast_id="f1", resolved=True, resolution_date=date(2026, 12, 31)),
            Outcome(forecast_id="f2", resolved=False, resolution_date=date(2026, 12, 31)),
        ]
        result = brier_decomposition(forecasts, outcomes)
        assert isinstance(result, BrierDecomposition)
        assert result.overall == 0.0

    def test_mismatched_lengths_raises(self):
        forecasts = [self._make_forecast("f1", 0.5)]
        outcomes = [
            Outcome(forecast_id="f1", resolved=True, resolution_date=date(2026, 12, 31)),
            Outcome(forecast_id="f2", resolved=False, resolution_date=date(2026, 12, 31)),
        ]
        with pytest.raises(ScoringError):
            brier_decomposition(forecasts, outcomes)

    def test_decomposition_components(self):
        forecasts = [
            self._make_forecast(f"f{i}", 0.7) for i in range(10)
        ]
        outcomes = [
            Outcome(
                forecast_id=f"f{i}",
                resolved=(i < 7),
                resolution_date=date(2026, 12, 31),
            )
            for i in range(10)
        ]
        result = brier_decomposition(forecasts, outcomes)
        assert result.reliability >= 0.0
        assert result.resolution >= 0.0
        assert result.uncertainty >= 0.0
