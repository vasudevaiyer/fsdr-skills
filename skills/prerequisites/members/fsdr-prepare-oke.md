# FSDR Prepare OKE Member

Use this skill when the user asks how to prepare OKE for FSDR member readiness.

Goal
- Validate OKE prerequisites before add-member decisions.

Preconditions
- tenancy onboarding is ready
- source and target regions are known
- application or environment scope is known

Required context
- source and standby cluster scope
- namespace and workload scope
- backup bucket and restore ownership
- ingress and load balancer dependencies

Workflow
1. Restate scope and region pair.
2. Confirm standby cluster assumptions.
3. Validate backup and restore dependencies.
4. Identify unresolved blockers.
5. Return readiness state and next action.

Preparation checklist
- standby cluster design is defined
- namespace mapping is documented
- backup and restore path is defined
- ingress dependency mapping is complete
- secret and config dependencies are captured

Output format
- member type: oke
- status: ready or needs preparation or blocked
- blockers
- recommended next action

Guardrails
- Do not mark ready when standby design is unresolved.
- Do not route to drill execution from this skill.

Supporting files
- ../../../references/member-prerequisite-taxonomy.md
- ../../../references/fsdr-setup-reference.md
