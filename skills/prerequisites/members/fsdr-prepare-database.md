# FSDR Prepare Database Member

Use this skill when the user asks how to prepare Oracle Database members for FSDR.

Goal
- Validate database prerequisites before add-member decisions.

Preconditions
- tenancy onboarding is ready
- source and target regions are known
- application or environment scope is known

Required context
- database type and deployment model
- primary and peer role mapping
- replication and peer relationship status
- vault and secret dependencies

Workflow
1. Restate database scope and region pair.
2. Confirm peer role assumptions.
3. Validate replication and secret dependencies.
4. Identify unresolved blockers.
5. Return readiness state and next action.

Preparation checklist
- primary and peer databases are identified
- role mapping is documented
- replication setup is confirmed
- secret dependencies are available
- policy dependencies are clear

Output format
- member type: database
- status: ready or needs preparation or blocked
- blockers
- recommended next action

Guardrails
- Do not mark ready when role mapping is unclear.
- Do not proceed with implicit replication assumptions.

Supporting files
- ../../../references/member-prerequisite-taxonomy.md
- ../../../references/fsdr-setup-reference.md
