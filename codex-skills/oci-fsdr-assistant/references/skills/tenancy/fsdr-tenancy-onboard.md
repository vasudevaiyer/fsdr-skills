# FSDR Tenancy Onboarding

Use this skill when the user needs to prepare a tenancy for OCI FSDR usage.

## Goal

Establish a safe, reusable tenancy context for later FSDR operations.

## Supporting files

- Read [references/tenancy-profile.md](../../tenancy-profile.md) when building or validating the tenancy context.
- Use [assets/tenancy-profile-template.yaml](../../../assets/tenancy-profile-template.yaml) as the default shape for new tenancy profiles.
- Read [references/personas.md](../../personas.md) when the user's role is unclear.
- Run [scripts/check_tenancy_profile.sh](../../../scripts/check_tenancy_profile.sh) after the required fields are collected.

## Required outputs

At the end of this workflow, produce:

- the selected tenancy identifier or alias
- onboarding status: `ready`, `blocked`, or `needs approval`
- the list of missing prerequisites, if any
- the recommended next step

## Inputs to collect

Collect only what is missing:

- tenancy name or OCID
- target regions
- compartments in scope
- user role or persona
- intended use: onboarding only, readiness check, configure, start drill, stop drill

## Workflow

1. Confirm the tenancy context.
2. Validate that the user is authorized to work on that tenancy.
3. Validate region scope and required compartments.
4. Validate prerequisites for FSDR work:
   - identity and access
   - policies
   - service availability
   - networking or environment dependencies as required by the target workload
5. Summarize findings in plain language.
6. If blocked, list the minimum fixes needed.
7. If ready, hand off to tenancy operations.

## Validation guidance

- Use the tenancy profile schema consistently so the context can be reused by later skills and tools.
- Treat missing `tenancy_ocid`, `home_region`, `compartments_in_scope`, or `persona` as onboarding gaps.
- If validation is only partial, return `blocked` with the exact missing fields.
- If the user is allowed to view but not act, return `needs approval`.

## Guardrails

- Do not perform FSDR configuration in this workflow.
- Do not attempt drill execution in this workflow.
- If the user wants to act immediately but prerequisites are incomplete, keep the workflow in `blocked` state and explain why.

## Completion criteria

This workflow is complete only when one of these is true:

- `ready`: the tenancy can move into tenancy operations
- `blocked`: required conditions are missing
- `needs approval`: the user has access but a governance step is required before continuing
