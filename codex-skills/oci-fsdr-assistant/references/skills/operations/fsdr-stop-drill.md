# FSDR Stop Drill

Use this skill when the user wants to stop an OCI FSDR drill in a tenancy that has already passed onboarding.

## Goal

Stop a known drill safely without affecting unrelated FSDR resources.

## Preconditions

Before using this skill, confirm:

- tenancy onboarding status is `ready`
- the drill, application, environment, or protection scope is identified
- the user persona allows drill operations

If the drill target is unclear, stop and ask for the exact drill context before continuing.

## Supporting files

- Read [references/governance.md](../../governance.md) before stopping a drill.
- Read [references/personas.md](../../personas.md) if the user's role is unclear.
- Run [scripts/summarize_operation_request.sh](../../../scripts/summarize_operation_request.sh) if the request mixes drill stop with other actions.

## Workflow

1. Restate the tenancy and drill context in scope.
2. Confirm that the requested action is `stop-drill`.
3. Summarize what drill activity will be stopped.
4. Require explicit confirmation.
5. Execute or guide the drill stop workflow.
6. Report the final status and any remaining follow-up actions.

## Output format

Return:

- tenancy context
- drill context
- action: `stop-drill`
- validation summary
- execution status
- next step

## Guardrails

- Do not stop a drill if the target drill context is ambiguous.
- Do not infer drill scope from a generic request like "stop DR."
- If the tenancy context is stale or incomplete, return to tenancy onboarding first.
