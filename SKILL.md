---
name: oci-fsdr-skills
description: Router skill for OCI Full Stack Disaster Recovery. Use when users want help onboarding a tenancy for FSDR, validating tenancy prerequisites, configuring FSDR resources, checking readiness, or managing disaster recovery drills.
---

# OCI FSDR Skills

Use this skill as the entry point for OCI FSDR requests. Route the user into one of two phases.

## Intro requests

Use [skills/tenancy/fsdr-introduction.md](skills/tenancy/fsdr-introduction.md) when the user asks:

- what OCI FSDR is
- what FSDR does
- what this FSDR assistant can help with
- what FSDR is not or what is out of scope

Keep the response brief, plain-language, and non-operational unless the user asks to continue into onboarding or operations.

## Phase 1: Tenancy onboarding

Use [skills/tenancy/fsdr-tenancy-onboard.md](skills/tenancy/fsdr-tenancy-onboard.md) when the user needs to:

- register or select a tenancy context
- validate identity or access
- validate regions, compartments, or policies
- confirm prerequisites before any FSDR work starts

Use [skills/tenancy/fsdr-prerequisites-and-policies.md](skills/tenancy/fsdr-prerequisites-and-policies.md) when the user specifically needs:

- OCI FSDR prerequisites
- required IAM policies
- tenancy-level readiness before any protection group work starts

Use [skills/tenancy/fsdr-policy-tailoring.md](skills/tenancy/fsdr-policy-tailoring.md) when the user needs:

- starter IAM policies adapted for a tenancy or compartment scope
- policy guidance tailored to an operator group or persona
- help scoping FSDR policies for a specific environment or workload

Use [skills/tenancy/fsdr-policy-create.md](skills/tenancy/fsdr-policy-create.md) when the user needs:

- a final policy artifact set derived from a tailoring draft
- copy-paste-ready OCI IAM policy statements
- dynamic group definitions and dependency-service policies
- a review-ready output for IAM or security approval

This phase is read-heavy and validation-heavy. Do not jump into FSDR configuration or plan execution before onboarding is complete.

## Phase 2: Tenancy operations

Use [skills/operations/fsdr-tenancy-operations.md](skills/operations/fsdr-tenancy-operations.md) when the user needs to:

- configure FSDR in a validated tenancy
- inspect protection groups, plans, or associations
- create protection groups
- prepare protection group members
- check disaster recovery readiness
- start or stop drills
- troubleshoot execution or validation failures

This phase must always run inside an explicit tenancy context.

For readiness-focused requests, prefer [skills/operations/fsdr-dr-readiness.md](skills/operations/fsdr-dr-readiness.md) before using the broader tenancy operations workflow.
For read-only OCI inventory requests, prefer [skills/operations/fsdr-read-infrastructure.md](skills/operations/fsdr-read-infrastructure.md) before any configuration or drill workflow.
For DR setup requests, prefer [skills/operations/fsdr-create-protection-group.md](skills/operations/fsdr-create-protection-group.md) and [skills/operations/fsdr-member-preparation.md](skills/operations/fsdr-member-preparation.md) before readiness or drill execution.
For member-specific preparation requests, route directly to the exact member skill file:
- [skills/prerequisites/members/fsdr-prepare-oke.md](skills/prerequisites/members/fsdr-prepare-oke.md)
- [skills/prerequisites/members/fsdr-prepare-database.md](skills/prerequisites/members/fsdr-prepare-database.md)
- [skills/prerequisites/members/fsdr-prepare-autonomous-database.md](skills/prerequisites/members/fsdr-prepare-autonomous-database.md)
- [skills/prerequisites/members/fsdr-prepare-compute.md](skills/prerequisites/members/fsdr-prepare-compute.md)
- [skills/prerequisites/members/fsdr-prepare-integration-instance.md](skills/prerequisites/members/fsdr-prepare-integration-instance.md)
- [skills/prerequisites/members/fsdr-prepare-application.md](skills/prerequisites/members/fsdr-prepare-application.md)
For drill lifecycle requests, use the dedicated start and stop drill skills.

## Routing rules

- If the user asks for a brief introduction to OCI FSDR or what it is not, route to the introduction skill first.
- If the user has not identified a tenancy, start with tenancy onboarding.
- If the user mentions a tenancy but access or prerequisites are unclear, start with tenancy onboarding.
- If the user asks about prerequisites or IAM policies for FSDR, route to the prerequisites and policies skill.
- If the user asks to tailor, customize, or scope FSDR IAM policies for a tenancy, route to the policy tailoring skill.
- If the user asks to generate final OCI IAM policy artifacts or dynamic group definitions from that draft, route to the policy creation skill.
- If the user asks how to create a protection group, route to the protection group creation skill.
- If the user asks which members can be added or how to prepare them, route to the member preparation skill.
- If the user asks how to prepare OKE, route to `skills/prerequisites/members/fsdr-prepare-oke.md`.
- If the user asks how to prepare Database, route to `skills/prerequisites/members/fsdr-prepare-database.md`.
- If the user asks how to prepare Autonomous Database, route to `skills/prerequisites/members/fsdr-prepare-autonomous-database.md`.
- If the user asks how to prepare Compute, route to `skills/prerequisites/members/fsdr-prepare-compute.md`.
- If the user asks how to prepare Integration Instance or OIC, route to `skills/prerequisites/members/fsdr-prepare-integration-instance.md`.
- If the user asks how to prepare application-level readiness, route to `skills/prerequisites/members/fsdr-prepare-application.md`.
- Keep read-only inventory requests tenancy-bound; keep instruction-only member guidance tenancy-optional.
- If the user asks to list compute instances, boot volumes, block volumes, or infrastructure inventory, route to the read-only infrastructure skill.
- If the user asks whether an app, environment, or tenancy is ready for DR, use the dedicated readiness skill.
- If the user asks to configure, validate readiness, or execute DR actions in a tenancy that is already known and validated, use tenancy operations.
- If the user asks to start a drill, route to the start drill skill.
- If the user asks to stop a drill, route to the stop drill skill.

## Response style

- Use plain language first and OCI terms second.
- Ask only for the missing inputs needed for the current phase.
- Summarize findings as `ready`, `blocked`, or `needs approval`.
- Keep tenancy onboarding and tenancy operations separate in both explanation and execution.
