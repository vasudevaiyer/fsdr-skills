# FSDR Prepare Autonomous Database Member

Use this skill when the user asks how to prepare Autonomous Database members for FSDR.

Goal
- Validate Autonomous Database prerequisites before add-member decisions.

Preconditions
- tenancy onboarding is ready
- source and target regions are known
- application or environment scope is known

Required context
- autonomous database scope
- remote peer and standby mapping
- region mapping for primary and standby

Workflow
1. Restate autonomous database scope and region pair.
2. Confirm remote peer mapping assumptions.
3. Validate mapping dependencies for DR protection groups.
4. Identify unresolved blockers.
5. Return readiness state and next action.

Preparation checklist
- primary and remote peer resources are identified
- peer relationship is defined
- standby mapping is explicit
- DR protection group mapping assumptions are documented

Output format
- member type: autonomous_database
- status: ready or needs preparation or blocked
- blockers
- recommended next action

Guardrails
- Do not mark ready when remote peer mapping is missing.
- Do not route to drill execution from this skill.

Supporting files
- ../../../references/member-prerequisite-taxonomy.md
- ../../../references/fsdr-setup-reference.md
