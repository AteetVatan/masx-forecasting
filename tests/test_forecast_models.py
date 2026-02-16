import pytest
from datetime import date, datetime

from core.domain.constants import (
    DoctrineDomain,
    EventCategory,
    ForecastStatus,
    ScenarioStatus,
)
from core.domain.forecast_models import (
    BrierDecomposition,
    DoctrinePack,
    Evidence,
    Forecast,
    Outcome,
    Scenario,
    Signpost,
)
from core.domain.event_taxonomy import (
    classify_gdelt_event,
    event_label,
    is_conflictual,
    is_cooperative,
)


class TestForecastModel:
    def test_forecast_valid(self):
        fc = Forecast(
            id="fc_test_001",
            event="Will country X impose sanctions by Q2 2026?",
            horizon=date(2026, 6, 30),
            probability=0.35,
            domain=DoctrineDomain.GEOPOLITICS,
        )
        assert fc.probability == 0.35
        assert fc.status == ForecastStatus.OPEN
        assert fc.confidence_interval == (0.0, 1.0)

    def test_forecast_probability_bounds(self):
        with pytest.raises(Exception):
            Forecast(
                id="fc_bad",
                event="test",
                horizon=date(2026, 1, 1),
                probability=1.5,
                domain=DoctrineDomain.MILITARY,
            )

    def test_forecast_with_evidence(self):
        evidence = [
            Evidence(source="article_1", snippet="Sanctions discussed", relevance_score=0.8),
            Evidence(source="gdelt_ev_2", snippet="Military buildup", relevance_score=0.6),
        ]
        fc = Forecast(
            id="fc_ev_001",
            event="test event",
            horizon=date(2026, 12, 31),
            probability=0.5,
            evidence=evidence,
            domain=DoctrineDomain.DIPLOMATIC,
        )
        assert len(fc.evidence) == 2
        assert fc.evidence[0].relevance_score == 0.8


class TestScenarioModel:
    def test_scenario_create(self):
        sc = Scenario(
            id="sc_test_001",
            title="Escalation Scenario",
            narrative="Tensions escalate leading to regional conflict.",
            probability_weight=0.3,
        )
        assert sc.status == ScenarioStatus.ACTIVE
        assert sc.probability_weight == 0.3


class TestDoctrinePack:
    def test_doctrine_pack_create(self):
        dp = DoctrinePack(
            doctrine_id="artofwar",
            name="The Art of War",
            principles=["Know your enemy", "All warfare is deception"],
            domain_fit=[DoctrineDomain.MILITARY, DoctrineDomain.GEOPOLITICS],
        )
        assert dp.doctrine_id == "artofwar"
        assert len(dp.domain_fit) == 2


class TestEventTaxonomy:
    def test_classify_protest(self):
        result = classify_gdelt_event("14")
        assert result == EventCategory.PROTEST

    def test_classify_invalid(self):
        result = classify_gdelt_event("99")
        assert result is None

    def test_labels(self):
        assert event_label(EventCategory.PROTEST) == "Protest"
        assert event_label(EventCategory.FIGHT) == "Fight"

    def test_conflictual(self):
        assert is_conflictual(EventCategory.PROTEST)
        assert is_conflictual(EventCategory.FIGHT)
        assert not is_conflictual(EventCategory.CONSULT)

    def test_cooperative(self):
        assert is_cooperative(EventCategory.CONSULT)
        assert is_cooperative(EventCategory.PROVIDE_AID)
        assert not is_cooperative(EventCategory.PROTEST)
