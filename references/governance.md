# Governance

Use this reference during tenancy operations to decide when to stop, confirm, or escalate.

## Risk categories

- `inspect`
  - Read-only inventory or status retrieval
- `readiness`
  - Read-only validation and precheck workflows
- `configure`
  - Changes tenancy or FSDR configuration
- `start-drill`
  - Starts a controlled DR exercise
- `stop-drill`
  - Stops a drill workflow in the current tenancy context

## Approval model

- `inspect` and `readiness`
  - No additional approval required beyond tenancy access
- `configure`
  - Allowed for `admin`
- `start-drill`
  - Allowed for `operator` or `admin`
- `stop-drill`
  - Allowed for `operator` or `admin`, but should require explicit confirmation

## Stop conditions

Stop the workflow and return `blocked` when:

- tenancy onboarding is not `ready`
- the action category cannot be confirmed
- the target tenancy or compartments are ambiguous
- required approvals are missing
- the environment state cannot be verified

## Response expectations

Before a non-read-only action, state:

- tenancy in scope
- action category
- expected impact
- confirmation requirement
- next step after execution
