# FSDR Policy Tailoring

Use this skill when the user wants OCI FSDR IAM policy guidance tailored to a specific tenancy, region scope, compartment scope, persona, or workload context.

## Goal

Turn generic OCI FSDR starter IAM guidance into a fuller tenancy-scoped IAM policy pack the user can review, adapt, and later feed into a policy-creation workflow.

## When to use

Use this skill for requests such as:

- tailor IAM policies for my tenancy
- customize FSDR policies for these compartments
- what policies should this operator group have
- adapt the starter FSDR policies for billing-prod
- how should I scope FSDR policies for this environment

## Preconditions

Before using this skill, collect or confirm:

- tenancy name or OCID
- regions in scope
- compartments in scope
- persona or operator group intent
- workload or application scope when relevant

If tenancy context is incomplete, return the minimum missing fields before giving tailored policy guidance.

## Workflow

1. Restate the tenancy, region, compartment, and persona context.
2. Confirm whether the user wants broad administration, configuration-only access, monitor/precheck access, or another scoped access pattern.
3. Start from the Oracle-aligned FSDR starter policy statements.
4. Tailor group names, compartment names, and access scope to the stated tenancy context.
5. Call out any non-FSDR dependencies, such as Vault, Oracle Cloud Agent, Run Command, or workload-specific service policies.
6. Summarize the result as:
   - `ready to review`
   - `needs clarification`
   - `blocked`

## Supporting files

- Read [../../references/fsdr-setup-reference.md](../../references/fsdr-setup-reference.md) for prerequisite and IAM policy guidance.
- Read [../../references/governance.md](../../references/governance.md) for approval and execution guardrails.
- Read [../../references/personas.md](../../references/personas.md) when the request depends on persona-specific scope.

## Output format

Return:

- tenancy context
- intended access pattern
- suggested IAM principals
- core FSDR policy statements
- dynamic group candidates and policy templates
- additional service dependency policies
- blockers, placeholders, or missing context
- recommended next action

## Guardrails

- Do not present starter examples as production-ready final policy without tenancy-specific review.
- Do not assume tenancy-wide admin access is appropriate when compartment-scoped access may be sufficient.
- Do not omit non-FSDR dependencies when the protected stack clearly needs them.
- Keep the answer specific to the stated tenancy, compartments, and operator intent.
