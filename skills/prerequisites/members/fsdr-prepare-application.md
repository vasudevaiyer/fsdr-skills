# FSDR Prepare Application Member

Use this skill when the user asks how to prepare an application-level member scope for FSDR.

Goal
- Build one readiness view across all member types in application scope.

Preconditions
- tenancy onboarding is ready
- application and environment scope is known
- source and target regions are known

Required context
- application boundary and critical components
- member types involved
- dependency order for recovery readiness
- known blockers by member type

Workflow
1. Restate application scope and region pair.
2. Identify member types in scope.
3. Evaluate readiness status per member type.
4. Aggregate blockers into one application readiness view.
5. Return readiness state and next action.

Preparation checklist
- application boundary is defined
- component-to-member mapping is complete
- inter-member dependencies are documented
- per-member readiness is available
- unresolved blockers are prioritized

Output format
- member type: application
- status: ready or needs preparation or blocked
- blockers by component
- recommended next action

Guardrails
- Do not mark application scope ready unless required member types are ready.
- Do not skip dependency ordering in readiness output.

Supporting files
- ../../../references/member-prerequisite-taxonomy.md
- ../../../references/fsdr-setup-reference.md
