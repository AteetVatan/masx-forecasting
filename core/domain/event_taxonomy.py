from __future__ import annotations

from core.domain.constants import EventCategory

_CAMEO_LABELS: dict[EventCategory, str] = {
    EventCategory.VERBAL_COOPERATION: "Verbal Cooperation",
    EventCategory.APPEAL: "Appeal",
    EventCategory.INTEND_COOPERATION: "Intend to Cooperate",
    EventCategory.CONSULT: "Consult",
    EventCategory.DIPLOMATIC_COOPERATION: "Diplomatic Cooperation",
    EventCategory.MATERIAL_COOPERATION: "Material Cooperation",
    EventCategory.PROVIDE_AID: "Provide Aid",
    EventCategory.YIELD: "Yield",
    EventCategory.INVESTIGATE: "Investigate",
    EventCategory.DEMAND: "Demand",
    EventCategory.DISAPPROVE: "Disapprove",
    EventCategory.REJECT: "Reject",
    EventCategory.THREATEN: "Threaten",
    EventCategory.PROTEST: "Protest",
    EventCategory.EXHIBIT_FORCE: "Exhibit Military Force",
    EventCategory.REDUCE_RELATIONS: "Reduce/Sever Relations",
    EventCategory.COERCE: "Coerce",
    EventCategory.ASSAULT: "Assault",
    EventCategory.FIGHT: "Fight",
    EventCategory.MASS_VIOLENCE: "Mass Violence",
}


def classify_gdelt_event(cameo_root_code: str) -> EventCategory | None:
    cleaned = cameo_root_code.strip().zfill(2)[:2]
    try:
        return EventCategory(cleaned)
    except ValueError:
        return None


def event_label(category: EventCategory) -> str:
    return _CAMEO_LABELS.get(category, category.value)


def is_conflictual(category: EventCategory) -> bool:
    _CONFLICT_THRESHOLD = 10
    return int(category.value) >= _CONFLICT_THRESHOLD


def is_cooperative(category: EventCategory) -> bool:
    _COOPERATION_THRESHOLD = 9
    return int(category.value) <= _COOPERATION_THRESHOLD
