# FSDR Create Protection Group

Use this skill when the user wants to create or plan an OCI FSDR DR Protection Group in a validated tenancy.

## Goal

Guide the user through DR Protection Group creation and the choices that affect later drill workflows.

## Preconditions

Before using this skill, confirm:

- tenancy onboarding is `ready`
- prerequisite and IAM policy status are not blocked
- the source application or environment is identified
- the source and target regions are identified

If any of these are unclear, route back to tenancy onboarding or prerequisites and policies.

## Workflow

1. Restate the tenancy, application, and regions in scope.
2. Confirm whether the user wants conceptual guidance or a concrete creation workflow.
3. Identify the protection group context:
   - source role and target role
   - source region and target region
   - object storage or log bucket requirements
   - peer relationship expectations
4. Explain what information must be prepared before the protection group is created.
5. Summarize the creation sequence in plain language.
6. Route to member preparation after the protection group design is clear.

## Supporting files

- Read [references/fsdr-setup-reference.md](../../fsdr-setup-reference.md) for protection group creation requirements and member-type context.

## Output format

Return:

- tenancy context
- application or environment in scope
- protection group plan or status
- missing setup details
- recommended next action

## Guardrails

- Do not treat protection group creation as complete if peer, region, or bucket details are still unresolved.
- Do not proceed to drill workflows until protection group creation and member preparation are complete.
