# FSDR Prerequisites And Policies

Use this skill when the user wants to understand or validate what must exist before OCI FSDR can be configured in a tenancy.

## Goal

Make tenancy-level prerequisites and IAM policy expectations explicit before the user starts protection group or drill work.

## When to use

Use this skill for requests such as:

- what are the prerequisites for OCI FSDR
- what IAM policies are required
- what must be configured before creating protection groups
- why FSDR setup is blocked at the tenancy level

## Preconditions

Before using this skill, collect or confirm:

- tenancy name or OCID
- regions in scope
- compartments in scope
- user persona or role

If tenancy context is missing, return to tenancy onboarding first.

## Workflow

1. Restate the tenancy context and the target regions.
2. Confirm whether the user wants explanation, validation, or remediation guidance.
3. Evaluate prerequisite areas:
   - tenancy access and identity
   - compartments in scope
   - region availability
   - IAM policy requirements
   - any FSDR-specific setup dependencies that block protection group work
4. Summarize the result as:
   - `ready`
   - `partially ready`
   - `blocked`
5. List the minimum missing items in plain language.
6. Route the user to protection group creation once prerequisites are in place.

## Supporting files

- Read [../../references/fsdr-setup-reference.md](../../references/fsdr-setup-reference.md) for Oracle-aligned prerequisite and IAM policy guidance.

## Starter IAM policy statements

Use these as Oracle-documented starter examples and replace group names and compartment names for your tenancy.

### Full DR administration in the tenancy

```text
Allow group DRUberAdmins to manage disaster-recovery-family in tenancy
```

### Create DR configurations and execute prechecks in one compartment

```text
Allow group DRMonitors to manage disaster-recovery-protection-groups in compartment ApplicationERP
Allow group DRMonitors to manage disaster-recovery-plans in compartment ApplicationERP
Allow group DRMonitors to manage disaster-recovery-prechecks in compartment ApplicationERP
```

### Create DR configurations in one compartment

```text
Allow group DRConfig to manage disaster-recovery-protection-groups in compartment ApplicationERP
Allow group DRConfig to manage disaster-recovery-plans in compartment ApplicationERP
```

## Policy notes

- `disaster-recovery-family` is the family-level resource type for Full Stack DR.
- Full Stack DR also has individual resource types such as protection groups, plans, plan prechecks, plan executions, and work requests.
- In addition to Full Stack DR policies, expect other service policies for the stack you are protecting. Common examples are Vault access for database workflows and Oracle Cloud Agent or Run Command access for compute workflows.

## Output format

Return:

- tenancy context
- prerequisite status
- IAM policy status
- blockers or gaps
- recommended next action

## Guardrails

- Do not assume prerequisites are satisfied just because the user has tenancy access.
- Do not move into protection group creation until policy and access blockers are clear.
- Keep explanations concrete and tenancy-scoped.
