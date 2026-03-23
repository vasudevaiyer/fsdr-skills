# FSDR Member Preparation

Use this skill when the user wants to know which resources can be added to a DR Protection Group and what must be prepared before they are added.

## Goal

Clarify member eligibility and preparation steps before the user attempts to build or validate a DR Protection Group.

## Preconditions

Before using this skill, confirm:

- tenancy onboarding is `ready`
- the relevant protection group or application scope is identified
- the user knows which workload or resource types are in scope

If the target scope is unclear, return to protection group creation or tenancy onboarding.

## Workflow

1. Restate the tenancy, application, and protection group scope.
2. Confirm whether the user wants a member eligibility summary, preparation guidance, or both.
3. Identify the resource types the user plans to add.
4. Explain:
   - which member types are supported in the current scope
   - what preparation each member type needs before addition
   - what gaps would block readiness or drill execution
5. Summarize the result as:
   - `ready for add`
   - `needs preparation`
   - `blocked`
6. Route to DR readiness after the member set is prepared.

## Supporting files

- Read [../../references/fsdr-setup-reference.md](../../references/fsdr-setup-reference.md) for supported member types and preparation notes.

## Output format

Return:

- tenancy context
- protection group scope
- member types in scope
- preparation status
- blockers or missing preparation
- recommended next action

## Guardrails

- Do not assume all workload components can be added without preparation.
- Keep guidance tied to the specific member types the user is working with.
- If the user asks for drill execution before members are prepared, route to readiness first.
