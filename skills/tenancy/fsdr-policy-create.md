# FSDR Policy Create

Use this skill when the user wants to turn an FSDR policy-tailoring draft into a concrete IAM policy artifact set that can be reviewed and later applied in OCI.

## Goal

Convert a scoped FSDR policy pack into copy-paste-ready IAM policy statements, dynamic group definitions, and a short implementation checklist without executing any tenancy changes.

## When to use

Use this skill for requests such as:

- create the final IAM policies for FSDR
- turn this policy draft into OCI policy statements
- generate dynamic group rules and policies for FSDR
- prepare policy artifacts for review and approval
- give me the final policy set for this tenancy and workload

## Preconditions

Before using this skill, collect or confirm:

- tenancy or environment scope
- compartments in scope
- persona or operator group intent
- workload or application scope
- any dependency services that require additional policies

If the policy-tailoring draft already exists, use that as the source of truth and keep unresolved placeholders explicit.

## Workflow

1. Restate the confirmed tenancy, compartment, persona, and workload context.
2. Separate the output into:
   - human group policies
   - dynamic group definitions
   - dependency-service policies
   - implementation notes
3. Produce copy-paste-ready OCI policy statements with placeholders only where context is still missing.
4. Keep the Oracle-aligned starter FSDR policies visible as the baseline.
5. Call out anything that still needs security, IAM, or workload-owner review.
6. Summarize the result as:
   - `ready for review`
   - `needs placeholders replaced`
   - `blocked`

## Supporting files

- Read [../../references/fsdr-setup-reference.md](../../references/fsdr-setup-reference.md) for prerequisite and IAM policy guidance.
- Read [../../references/governance.md](../../references/governance.md) for approval and execution guardrails.
- Read [../../references/personas.md](../../references/personas.md) when persona scope affects the final policy set.
- Read [fsdr-policy-tailoring.md](fsdr-policy-tailoring.md) if the user first needs a scoped policy-pack draft.

## Output format

Return:

- policy creation status
- confirmed scope
- human group policies
- dynamic group definitions
- dependency-service policy statements
- placeholders or unresolved gaps
- implementation checklist
- recommended next action

## Guardrails

- Do not execute OCI IAM changes from this skill.
- Do not hide unresolved placeholders just to make the output look complete.
- Keep final policy artifacts grouped by principal and service dependency.
- Preserve a clear distinction between Oracle starter examples and tenancy-specific final policy artifacts.
