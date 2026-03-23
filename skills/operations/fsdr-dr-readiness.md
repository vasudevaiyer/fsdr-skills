# FSDR DR Readiness

Use this skill when the user wants to know whether a tenancy, application, or environment is ready for OCI FSDR operations.

## Goal

Produce a clear readiness result before any drill action is attempted.

## Preconditions

Before using this skill, confirm:

- a tenancy context exists
- onboarding is `ready` or the missing details are small enough to validate immediately
- the target application, environment, or protection scope is identified

If the tenancy context is missing or unreliable, return to tenancy onboarding.

## Supporting files

- Read [references/tenancy-profile.md](../../references/tenancy-profile.md) to confirm tenancy context fields.
- Read [references/governance.md](../../references/governance.md) to understand the risk of the next action.
- Read [../tenancy/fsdr-prerequisites-and-policies.md](../tenancy/fsdr-prerequisites-and-policies.md) if prerequisite or IAM policy status is unclear.
- Read [fsdr-create-protection-group.md](fsdr-create-protection-group.md) if protection group design or creation status is unclear.
- Read [fsdr-member-preparation.md](fsdr-member-preparation.md) if member eligibility or preparation status is unclear.
- Read [../../references/fsdr-setup-reference.md](../../references/fsdr-setup-reference.md) if the user needs a consolidated Oracle-aligned setup summary.
- Run [scripts/summarize_operation_request.sh](../../scripts/summarize_operation_request.sh) if the user mixes readiness and execution requests.

## Workflow

1. Restate the tenancy, application, and environment in scope.
2. Confirm whether the user wants readiness only or readiness plus a later action.
3. Validate:
   - tenancy onboarding status
   - prerequisite and IAM policy status
   - region scope
   - compartments in scope
   - role and persona alignment
   - DR Protection Group creation status
   - member preparation status
   - known FSDR configuration state
4. Summarize the result as one of:
   - `ready`
   - `partially ready`
   - `blocked`
5. For anything other than `ready`, list the minimum remediation items.
6. If `ready`, recommend the next operation: `configure`, `start-drill`, or `stop-drill`.

## Output format

Return:

- tenancy context
- application or environment in scope
- readiness status
- blockers or gaps
- recommended next action

## Guardrails

- Do not execute DR actions from this skill.
- If the user asks for execution in the same request, complete readiness first and then route to tenancy operations.
- Do not call something `ready` if the tenancy context, persona, or target scope is ambiguous.
- Do not call something `ready` if prerequisites, IAM policies, protection groups, or member preparation are still unresolved.
