# FSDR Start Drill

Use this skill when the user wants to start an OCI FSDR drill in a tenancy that has already passed onboarding.

## Goal

Start a drill only after the tenancy context, target scope, and operator intent are explicit.

## Preconditions

Before using this skill, confirm:

- tenancy onboarding status is `ready`
- the target application, environment, or protection group is identified
- the user persona allows drill execution
- readiness blockers have been reviewed or cleared

If any of these are unclear, return to tenancy onboarding or DR readiness.

## Supporting files

- Read [references/governance.md](../../governance.md) before execution.
- Read [references/personas.md](../../personas.md) if the user's role is unclear.
- Run [scripts/summarize_operation_request.sh](../../../scripts/summarize_operation_request.sh) if the request mixes drill start with other actions.

## Workflow

1. Restate the tenancy, application, environment, and target regions.
2. Confirm that the requested action is `start-drill`.
3. Summarize the current validation state and any remaining warnings.
4. State the expected impact of starting the drill.
5. Require explicit confirmation.
6. Execute or guide the drill start workflow.
7. Report the drill status, identifiers, and next follow-up action.

## Output format

Return:

- tenancy context
- target scope
- action: `start-drill`
- validation summary
- execution status
- next step

## Guardrails

- Do not start a drill if tenancy context or target scope is ambiguous.
- Do not combine drill start with drill stop in the same action.
- If readiness is not clear, route to DR readiness first.
