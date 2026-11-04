"""Input normalization and quality checks."""

from __future__ import annotations

import re

from .models import SupportCase


def normalize_text(value: str) -> str:
    """Collapse whitespace while preserving the original wording."""
    return re.sub(r"\s+", " ", value).strip()


def validate(case: SupportCase) -> tuple[str, ...]:
    issues: list[str] = []
    if not case.case_id:
        issues.append("missing_case_id")
    if not normalize_text(case.text):
        issues.append("missing_conversation_text")
    return tuple(issues)


def searchable_text(case: SupportCase) -> str:
    return normalize_text(f"{case.subject} {case.text}").lower()
