---
name: oci-fsdr-assistant
description: Use when the user needs help with OCI Full Stack Disaster Recovery, including FSDR introduction, tenancy onboarding, prerequisites and IAM policies, policy tailoring, protection group setup, member preparation, readiness checks, drill lifecycle guidance, or multi-member requests such as adding OKE and Database to a DR Protection Group.
---

# OCI FSDR Assistant

Use this skill as the Codex entry point for OCI Full Stack Disaster Recovery requests.

## Goal

Handle OCI FSDR questions by routing to the right reference workflow, keeping tenancy-bound operations separate from instruction-only guidance, and aggregating multi-member preparation requests into one answer.

## Routing

### Introduction

Use [references/skills/tenancy/fsdr-introduction.md](references/skills/tenancy/fsdr-introduction.md) when the user asks:

- what OCI FSDR is
- what FSDR does
- what this assistant can help with
- what is out of scope

Keep the answer brief unless the user asks to continue.

### Tenancy onboarding

Use [references/skills/tenancy/fsdr-tenancy-onboard.md](references/skills/tenancy/fsdr-tenancy-onboard.md) when the user needs:

- tenancy selection or registration
- identity, region, or compartment validation
- onboarding readiness before FSDR work starts

Use [references/skills/tenancy/fsdr-prerequisites-and-policies.md](references/skills/tenancy/fsdr-prerequisites-and-policies.md) when the user asks specifically about prerequisites or IAM policies.

Use [references/skills/tenancy/fsdr-policy-tailoring.md](references/skills/tenancy/fsdr-policy-tailoring.md) when the user needs:

- starter IAM policies adapted for tenancy, compartment, or persona scope
- a fuller IAM policy pack draft with placeholders
- dynamic-group candidates and dependency policy templates
- policy output that can later feed a policy-creation workflow

Use [references/skills/tenancy/fsdr-policy-create.md](references/skills/tenancy/fsdr-policy-create.md) when the user needs:

- final OCI IAM policy artifacts derived from that draft
- copy-paste-ready policies grouped by principal
- dynamic group definitions and dependency-service policies
- review-ready output for IAM or security approval

### Tenancy operations

Use [references/skills/operations/fsdr-tenancy-operations.md](references/skills/operations/fsdr-tenancy-operations.md) when the user needs tenancy-bound FSDR operations such as DRPG inspection, plan exploration, or drill troubleshooting.

Prefer narrower references when the request is specific:

- readiness: [references/skills/operations/fsdr-dr-readiness.md](references/skills/operations/fsdr-dr-readiness.md)
- read-only inventory: [references/skills/operations/fsdr-read-infrastructure.md](references/skills/operations/fsdr-read-infrastructure.md)
- protection group creation: [references/skills/operations/fsdr-create-protection-group.md](references/skills/operations/fsdr-create-protection-group.md)
- generic member preparation: [references/skills/operations/fsdr-member-preparation.md](references/skills/operations/fsdr-member-preparation.md)
- start drill: [references/skills/operations/fsdr-start-drill.md](references/skills/operations/fsdr-start-drill.md)
- stop drill: [references/skills/operations/fsdr-stop-drill.md](references/skills/operations/fsdr-stop-drill.md)

### Member preparation

For a single member type, route directly to the exact member reference:

- OKE: [references/skills/prerequisites/members/fsdr-prepare-oke.md](references/skills/prerequisites/members/fsdr-prepare-oke.md)
- Database: [references/skills/prerequisites/members/fsdr-prepare-database.md](references/skills/prerequisites/members/fsdr-prepare-database.md)
- Autonomous Database: [references/skills/prerequisites/members/fsdr-prepare-autonomous-database.md](references/skills/prerequisites/members/fsdr-prepare-autonomous-database.md)
- Compute: [references/skills/prerequisites/members/fsdr-prepare-compute.md](references/skills/prerequisites/members/fsdr-prepare-compute.md)
- Integration Instance: [references/skills/prerequisites/members/fsdr-prepare-integration-instance.md](references/skills/prerequisites/members/fsdr-prepare-integration-instance.md)
- Application scope: [references/skills/prerequisites/members/fsdr-prepare-application.md](references/skills/prerequisites/members/fsdr-prepare-application.md)

For multi-member requests, such as `add OKE and Database to a DRPG`:

1. Use [references/skills/operations/fsdr-member-preparation.md](references/skills/operations/fsdr-member-preparation.md) as the orchestration frame.
2. Identify every member type in scope.
3. Load the exact member references for each identified member type.
4. Aggregate the answer into one response with:
   - member types in scope
   - common preparation gates
   - per-member required context
   - per-member preparation checklist
   - aggregated blockers or missing inputs
   - a single recommended next action

Do not answer multi-member requests as disconnected, per-skill fragments.

## Shared references

Load these only when needed:

- FSDR setup details: [references/fsdr-setup-reference.md](references/fsdr-setup-reference.md)
- member taxonomy: [references/member-prerequisite-taxonomy.md](references/member-prerequisite-taxonomy.md)
- tenancy profile context: [references/tenancy-profile.md](references/tenancy-profile.md)
- governance guardrails: [references/governance.md](references/governance.md)
- persona guidance: [references/personas.md](references/personas.md)
- tenancy policy tailoring: [references/skills/tenancy/fsdr-policy-tailoring.md](references/skills/tenancy/fsdr-policy-tailoring.md)
- tenancy policy creation: [references/skills/tenancy/fsdr-policy-create.md](references/skills/tenancy/fsdr-policy-create.md)

## Scripts

Use bundled scripts when they help keep behavior consistent:

- `scripts/check_tenancy_profile.sh`
- `scripts/summarize_operation_request.sh`

## Guardrails

- Keep tenancy onboarding and tenancy operations separate.
- Treat read-only guidance as tenancy-optional unless the workflow explicitly requires tenancy context.
- Do not mark readiness or drill safety as proven unless the required evidence is present.
- For multi-member preparation, aggregate the answer instead of picking only one member skill.
- For multi-step requests that mix intents, finish the current intent cleanly and make the next stage explicit.
- Keep policy-tailoring distinct from generic prerequisites: produce a scoped policy pack draft, not just the Oracle starter examples.
- Use policy creation only after the scope is reasonably clear; keep unresolved placeholders explicit instead of inventing final values.
