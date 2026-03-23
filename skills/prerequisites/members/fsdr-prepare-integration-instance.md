# FSDR Prepare Integration Instance Member

Use this skill when the user asks how to prepare Integration Instance members for FSDR.

Goal
- Validate Integration Instance prerequisites before add-member decisions.

Preconditions
- tenancy onboarding is ready
- source and target regions are known
- integration instance scope is known

Required context
- source and standby integration scope
- region and peer mapping assumptions
- networking, policy, and secret dependencies

Workflow
1. Restate integration scope and region pair.
2. Confirm standby service assumptions.
3. Validate dependency readiness before add-member.
4. Identify unresolved blockers.
5. Return readiness state and next action.

Preparation checklist
- source and standby scope is defined
- region and peer mapping is explicit
- networking and policy dependencies are clear
- secret and connectivity dependencies are documented

Output format
- member type: integration_instance
- status: ready or needs preparation or blocked
- blockers
- recommended next action

Guardrails
- Do not mark ready when standby assumptions are implicit.
- Do not proceed with unresolved service dependencies.

Supporting files
- ../../../references/member-prerequisite-taxonomy.md
- ../../../references/fsdr-setup-reference.md
