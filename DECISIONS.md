# Design Decisions

## Deterministic routing before generative drafting

Routing, risk, authentication, source requirements, and human-handoff decisions are encoded as inspectable rules. A language model could later help draft responses, but it should not silently own authority boundaries.

## No API key in the first release

The initial project uses only the Python standard library. A reviewer can clone it, run the tests, and reproduce the results without credentials, external services, or usage charges.

## Synthetic rather than redacted client data

Every organization, policy, product, identifier, and conversation in the repository is fictional. Redaction can miss context and does not make client-derived material appropriate for a public portfolio.

## Abstention is a valid outcome

When no rule matches or an approved source is missing, the workflow abstains. It does not improvise a plausible response to maximize apparent automation.

## Response plans rather than polished answers

The project returns a response plan that exposes the source and control requirements. This keeps the demonstration focused on operational workflow design and avoids presenting templated prose as an intelligent agent.

## Explicit non-goals

- No autonomous message sending.
- No customer-data ingestion.
- No claim of production readiness.
- No inferred ROI or performance claim.
- No dependency on a specific helpdesk interface.
