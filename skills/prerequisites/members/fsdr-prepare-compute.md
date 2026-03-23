# FSDR Prepare Compute Member

Use this skill when the user asks how to prepare compute members for FSDR.

Goal
- Validate compute and volume dependencies before add-member decisions.

Preconditions
- tenancy onboarding is ready
- source and target regions are known
- instance scope is known

Required context
- instance scope and recovery style
- boot and block volume dependencies
- volume group preparation status
- automation script and run-command dependencies

Workflow
1. Restate compute scope and region pair.
2. Confirm moving or non-moving recovery expectation.
3. Validate volume and replication assumptions.
4. Identify unresolved blockers.
5. Return readiness state and next action.

Preparation checklist
- volume group strategy is defined
- boot and block mappings are documented
- standby volume availability approach is clear
- automation dependencies are captured

Output format
- member type: compute
- status: ready or needs preparation or blocked
- blockers
- recommended next action

Guardrails
- Do not mark ready when volume dependencies are unresolved.
- Do not assume moving recovery readiness without explicit volume preparation.

Supporting files
- ../../../references/member-prerequisite-taxonomy.md
- ../../../references/fsdr-setup-reference.md
