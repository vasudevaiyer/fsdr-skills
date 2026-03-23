# AI Routing Design

## Goal

Provide a stable routing layer for the OCI FSDR assistant that can answer instruction-only questions without tenancy context, while keeping inventory lookups and operational workflows tenancy-bound.

## Design Pattern

The router uses an AI-first pattern:

- AI-first classification for both explicit and broad natural-language requests, constrained to the bounded FSDR intent set.
- Local fallback only when the model result is invalid, unavailable, or outside the supported taxonomy.
- Catalog-backed enforcement so the final selected skill must be one of the approved skill files.

This keeps routing flexible for natural language while still preventing the classifier from inventing new actions.

## Intent Model

The current classifier maps requests into a small, stable taxonomy:

- introduction
- tenancy_onboarding
- prerequisites
- member_preparation
- readiness
- create_protection_group
- read_inventory
- read_protection_group
- explore_plans
- run_prechecks
- start_drill
- stop_drill
- troubleshooting

For member preparation, the router also classifies member type and dispatches directly to the exact member skill file when available.

## Tenancy Gating

The catalog marks each skill as one of these operational classes:

- instruction
- read_only
- validate
- mutating

Instruction-only skills do not require a selected tenancy. This includes:

- FSDR introduction
- tenancy prerequisites and IAM policy guidance
- generic member-preparation guidance
- member-specific preparation skills such as OKE, Database, Autonomous Database, Compute, Integration Instance, and Application

Read-only inventory, readiness validation, DRPG inspection, plan exploration, and drill workflows require tenancy context.

## Member Preparation Pattern

Member preparation is intentionally split from tenancy operations:

- generic entry point for supported-member guidance
- exact member skill files for OKE, Database, Autonomous Database, Compute, Integration Instance, and Application
- shared taxonomy reference for response contract and readiness states

This lets users ask preparation questions before tenancy registration, which is important for architecture and planning conversations.

## Response Contract

The router should return enough metadata for the UI and future orchestrators to stay deterministic:

- selected skill
- classified intent
- member type when relevant
- confidence
- whether tenancy context is required
- missing context
- routing reason

## Future AI Layer

The classifier should be AI-first while preserving the same bounded taxonomy and skill catalog. Recommended pattern:

1. Normalize user request and available session context.
2. Ask the classifier to return only supported intent and member type values.
3. Validate classifier output against the local catalog.
4. Fall back to the bounded local classifier only when the model result is invalid, unavailable, or out of taxonomy.

## Live OCI Tooling Integration

When live OCI tools are added, they should sit behind the routed skills rather than bypass the router. Recommended sequence:

1. Router classifies and selects a skill.
2. Skill checks required context and guardrails.
3. Read-only or mutating OCI tool call runs only if that skill permits it.
4. Result is summarized back into the same response contract.

This keeps UI behavior, CLI behavior, and future multi-agent orchestration aligned behind one routing layer.
