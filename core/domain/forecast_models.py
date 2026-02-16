from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from core.domain.constants import (
    DoctrineDomain,
    EventCategory,
    ForecastStatus,
    ScenarioStatus,
)


class Evidence(BaseModel):
    source: str
    snippet: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class Forecast(BaseModel):
    id: str
    event: str
    horizon: date
    probability: float = Field(ge=0.0, le=1.0)
    confidence_interval: tuple[float, float] = (0.0, 1.0)
    key_drivers: list[str] = Field(default_factory=list)
    disconfirming_evidence: list[str] = Field(default_factory=list)
    update_triggers: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    domain: DoctrineDomain
    event_category: EventCategory | None = None
    doctrine_agents_used: list[str] = Field(default_factory=list)
    base_rate: float | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None
    status: ForecastStatus = ForecastStatus.OPEN


class Outcome(BaseModel):
    forecast_id: str
    resolved: bool
    resolution_date: date
    notes: str = ""


class Signpost(BaseModel):
    id: str
    description: str
    scenario_id: str
    indicator: str
    current_status: Literal["not_seen", "emerging", "confirmed"] = "not_seen"
    last_checked: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Scenario(BaseModel):
    id: str
    title: str
    narrative: str
    probability_weight: float = Field(ge=0.0, le=1.0)
    signposts: list[Signpost] = Field(default_factory=list)
    key_assumptions: list[str] = Field(default_factory=list)
    early_warnings: list[str] = Field(default_factory=list)
    domain: DoctrineDomain | None = None
    status: ScenarioStatus = ScenarioStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DoctrinePack(BaseModel):
    doctrine_id: str
    name: str
    principles: list[str] = Field(default_factory=list)
    heuristics: list[str] = Field(default_factory=list)
    failure_modes: list[str] = Field(default_factory=list)
    recommended_tools: list[str] = Field(default_factory=list)
    domain_fit: list[DoctrineDomain] = Field(default_factory=list)


class BrierDecomposition(BaseModel):
    reliability: float
    resolution: float
    uncertainty: float
    overall: float
