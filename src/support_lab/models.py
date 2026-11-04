"""Typed domain models for synthetic support cases and routing decisions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


VALID_SOURCES = {"policy", "product", "order", "human_judgment"}


@dataclass(frozen=True)
class SupportCase:
    case_id: str
    subject: str
    text: str
    customer_authenticated: bool = False
    sources_available: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "SupportCase":
        return cls(
            case_id=str(value.get("case_id", "")).strip(),
            subject=str(value.get("subject", "")).strip(),
            text=str(value.get("text", "")).strip(),
            customer_authenticated=bool(value.get("customer_authenticated", False)),
            sources_available=tuple(
                str(source).strip().lower()
                for source in value.get("sources_available", [])
                if str(source).strip().lower() in VALID_SOURCES
            ),
        )


@dataclass(frozen=True)
class Decision:
    case_id: str
    valid: bool
    intent: str
    lifecycle_stage: str
    risk: str
    ai_eligibility: str
    required_source: str
    route: str
    reasons: tuple[str, ...]
    draft_plan: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["reasons"] = list(self.reasons)
        value["draft_plan"] = list(self.draft_plan)
        return value
