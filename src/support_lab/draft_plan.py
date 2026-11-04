"""Create inspectable response plans without generating customer-facing prose."""

from __future__ import annotations


def build_draft_plan(intent: str, required_source: str, route: str) -> tuple[str, ...]:
    if route not in {"auto_draft", "human_review"}:
        return ()

    steps = ["Acknowledge the customer's request directly."]
    if required_source != "none":
        steps.append(f"Ground every factual statement in the approved {required_source} source.")
    if intent == "product_recommendation":
        steps.append("State assumptions and avoid presenting suitability as guaranteed.")
    steps.append("Give the next action and preserve a clear path to a human.")
    return tuple(steps)
