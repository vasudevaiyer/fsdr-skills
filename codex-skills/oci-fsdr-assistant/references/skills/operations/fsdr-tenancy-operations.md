# FSDR Tenancy Operations

Use this skill when the user wants to work inside a tenancy that has already passed onboarding.

## Goal

Operate OCI FSDR safely within a validated tenancy context.

## Supporting files

- Read [references/governance.md](../../governance.md) before any execution workflow.
- Read [references/personas.md](../../personas.md) if the user's allowed actions are unclear.
- Run [scripts/summarize_operation_request.sh](../../../scripts/summarize_operation_request.sh) to normalize the requested action before execution.

## Preconditions

Before using this skill, confirm:

- a tenancy has been selected
- onboarding status is `ready` or an approved equivalent
- the requested action matches the user's role

If any of these are unclear, return to tenancy onboarding.

## Supported intents

Use this skill for:

- configure FSDR resources
- inspect FSDR inventory
- create protection groups
- prepare members for protection groups
- check readiness for DR operations
- start drills
- stop drills
- troubleshoot failed validation or execution

## Workflow

1. Restate the tenancy and action in scope.
2. Confirm the user intent category:
   - `configure`
   - `inspect`
   - `readiness`
   - `start-drill`
   - `stop-drill`
   - `troubleshoot`
3. Run read-only checks first whenever possible.
4. Summarize expected impact before any write or execution step.
5. Require explicit confirmation before starting or stopping a drill.
6. Execute or guide the requested workflow.
7. Report the outcome, current state, and next recommended action.

## Decision guidance

- Default to `inspect` or `readiness` if the user intent is ambiguous.
- Do not treat a general request such as "run DR" as sufficient for drill execution.
- If governance approval is required for the action category, stop before execution and return `needs approval`.
- If the tenancy onboarding record is stale or incomplete, return to tenancy onboarding before continuing.

## Safety rules

- `configure` is lower risk than `start-drill`.
- `start-drill` and `stop-drill` both require explicit operator intent.
- Always make the action category explicit before execution.
- Require explicit confirmation for `start-drill` and `stop-drill`.
- If the tool or environment cannot verify the tenancy state, stop and return a `blocked` result.

## Output format

Return:

- tenancy context
- action requested
- validation summary
- execution status: `not started`, `ready`, `blocked`, `running`, `completed`, or `failed`
- next step
