"""Deterministic policy-as-code routing for synthetic support conversations."""

from __future__ import annotations

from dataclasses import dataclass

from .draft_plan import build_draft_plan
from .models import Decision, SupportCase
from .normalize import searchable_text, validate


@dataclass(frozen=True)
class Rule:
    intent: str
    terms: tuple[str, ...]
    lifecycle_stage: str
    risk: str
    ai_eligibility: str
    required_source: str
    route: str
    reason: str


RULES = (
    Rule(
        "instruction_attack",
        ("ignore previous instructions", "reveal your system prompt", "bypass policy"),
        "other",
        "high",
        "no",
        "human_judgment",
        "human_handoff",
        "Conversation contains an instruction-manipulation attempt.",
    ),
    Rule(
        "dispute_or_legal",
        ("chargeback", "legal action", "solicitor", "sue", "consumer authority"),
        "after_sales",
        "high",
        "no",
        "human_judgment",
        "human_handoff",
        "Dispute or legal-risk language requires accountable human handling.",
    ),
    Rule(
        "order_change",
        ("change my address", "change the address", "cancel my order", "modify my order"),
        "active_order",
        "high",
        "no",
        "order",
        "human_handoff",
        "Post-purchase account changes must be verified and completed by authorized staff.",
    ),
    Rule(
        "refund_or_compensation",
        ("refund", "compensation", "money back"),
        "after_sales",
        "high",
        "no",
        "human_judgment",
        "human_handoff",
        "Financial remedies require human authorization.",
    ),
    Rule(
        "delivery_problem",
        ("parcel is missing", "package is missing", "never arrived", "damaged delivery"),
        "after_sales",
        "high",
        "no",
        "order",
        "human_handoff",
        "A delivery exception requires authenticated order investigation.",
    ),
    Rule(
        "order_status",
        ("where is my order", "track my order", "order status"),
        "active_order",
        "medium",
        "draft_only",
        "order",
        "human_review",
        "Order-specific information requires authentication and review before disclosure.",
    ),
    Rule(
        "product_recommendation",
        ("which product", "recommend", "suitable for", "best for"),
        "pre_purchase",
        "medium",
        "draft_only",
        "product",
        "human_review",
        "Suitability advice may depend on context not present in the conversation.",
    ),
    Rule(
        "shipping_policy",
        ("shipping cost", "delivery cost", "ship to", "delivery time"),
        "pre_purchase",
        "low",
        "yes",
        "policy",
        "auto_draft",
        "A factual policy question can be drafted from an approved source.",
    ),
    Rule(
        "product_information",
        ("dimensions", "material", "specification", "in stock", "available in"),
        "pre_purchase",
        "low",
        "yes",
        "product",
        "auto_draft",
        "A factual product question can be drafted from an approved source.",
    ),
)


def _match_rule(text: str) -> Rule | None:
    for rule in RULES:
        if any(term in text for term in rule.terms):
            return rule
    return None


def decide(case: SupportCase) -> Decision:
    issues = validate(case)
    if issues:
        return Decision(
            case_id=case.case_id or "unknown",
            valid=False,
            intent="invalid_input",
            lifecycle_stage="unknown",
            risk="unknown",
            ai_eligibility="no",
            required_source="none",
            route="human_review",
            reasons=issues,
        )

    rule = _match_rule(searchable_text(case))
    if rule is None:
        return Decision(
            case_id=case.case_id,
            valid=True,
            intent="unknown",
            lifecycle_stage="other",
            risk="medium",
            ai_eligibility="no",
            required_source="human_judgment",
            route="abstain",
            reasons=("No approved deterministic rule matched this request.",),
        )

    if rule.required_source in {"policy", "product", "order"} and rule.required_source not in case.sources_available:
        return Decision(
            case_id=case.case_id,
            valid=True,
            intent=rule.intent,
            lifecycle_stage=rule.lifecycle_stage,
            risk=rule.risk,
            ai_eligibility="no",
            required_source=rule.required_source,
            route="abstain" if rule.risk == "low" else "human_handoff",
            reasons=(rule.reason, f"Approved {rule.required_source} source is unavailable."),
        )

    if rule.required_source == "order" and not case.customer_authenticated:
        return Decision(
            case_id=case.case_id,
            valid=True,
            intent=rule.intent,
            lifecycle_stage=rule.lifecycle_stage,
            risk=rule.risk,
            ai_eligibility="no",
            required_source="order",
            route="human_handoff",
            reasons=(rule.reason, "Customer identity is not authenticated for order-specific access."),
        )

    plan = build_draft_plan(rule.intent, rule.required_source, rule.route)
    return Decision(
        case_id=case.case_id,
        valid=True,
        intent=rule.intent,
        lifecycle_stage=rule.lifecycle_stage,
        risk=rule.risk,
        ai_eligibility=rule.ai_eligibility,
        required_source=rule.required_source,
        route=rule.route,
        reasons=(rule.reason,),
        draft_plan=plan,
    )
