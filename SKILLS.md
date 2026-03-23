# OCI FSDR Skills Library

This repository is a starter library for OCI Full Stack Disaster Recovery workflows.

## Usage model

The skills are organized around a two-step operating model:

1. Tenancy onboarding
2. Tenancy operations

Users should start with tenancy onboarding before attempting FSDR configuration or DR execution.

The backend router uses an AI-first classifier path to map natural-language requests into the bounded FSDR skill taxonomy, with local fallback only when the model result is invalid or unavailable.
Inventory and mutating operations require tenancy context, while instruction-only skills (including member preparation guidance) are tenancy-optional.

## Skill index

- [SKILL.md](SKILL.md): Root router for OCI FSDR requests
- [skills/tenancy/fsdr-introduction.md](skills/tenancy/fsdr-introduction.md): Brief explanation of what OCI FSDR is, what the assistant can do, and what is out of scope
- [skills/tenancy/fsdr-tenancy-onboard.md](skills/tenancy/fsdr-tenancy-onboard.md): Validate tenancy access and prerequisites
- [skills/tenancy/fsdr-prerequisites-and-policies.md](skills/tenancy/fsdr-prerequisites-and-policies.md): Explain OCI FSDR prerequisites and required IAM policies
- [skills/tenancy/fsdr-policy-tailoring.md](skills/tenancy/fsdr-policy-tailoring.md): Tailor OCI FSDR starter IAM policy guidance to a tenancy, compartment, and persona scope
- [skills/tenancy/fsdr-policy-create.md](skills/tenancy/fsdr-policy-create.md): Turn a tailored FSDR policy pack into review-ready OCI IAM policy artifacts and dynamic group definitions
- [skills/operations/fsdr-tenancy-operations.md](skills/operations/fsdr-tenancy-operations.md): Configure FSDR and execute DR workflows in a validated tenancy
- [skills/operations/fsdr-read-infrastructure.md](skills/operations/fsdr-read-infrastructure.md): Read-only OCI inventory for compute instances, attached volumes, and VNIC context
- [skills/operations/fsdr-create-protection-group.md](skills/operations/fsdr-create-protection-group.md): Guide DR Protection Group creation and setup
- [skills/operations/fsdr-member-preparation.md](skills/operations/fsdr-member-preparation.md): Explain which members can be added and route to member-specific preparation skills
- [skills/prerequisites/members/fsdr-prepare-oke.md](skills/prerequisites/members/fsdr-prepare-oke.md): Prepare OKE members for FSDR
- [skills/prerequisites/members/fsdr-prepare-database.md](skills/prerequisites/members/fsdr-prepare-database.md): Prepare Database members for FSDR
- [skills/prerequisites/members/fsdr-prepare-autonomous-database.md](skills/prerequisites/members/fsdr-prepare-autonomous-database.md): Prepare Autonomous Database members for FSDR
- [skills/prerequisites/members/fsdr-prepare-compute.md](skills/prerequisites/members/fsdr-prepare-compute.md): Prepare Compute members for FSDR
- [skills/prerequisites/members/fsdr-prepare-integration-instance.md](skills/prerequisites/members/fsdr-prepare-integration-instance.md): Prepare Integration Instance members for FSDR
- [skills/prerequisites/members/fsdr-prepare-application.md](skills/prerequisites/members/fsdr-prepare-application.md): Prepare application-level member scope for FSDR
- [skills/operations/fsdr-dr-readiness.md](skills/operations/fsdr-dr-readiness.md): Assess whether a tenancy, application, or environment is ready for DR execution
- [skills/operations/fsdr-start-drill.md](skills/operations/fsdr-start-drill.md): Start a drill in a validated tenancy
- [skills/operations/fsdr-stop-drill.md](skills/operations/fsdr-stop-drill.md): Stop a drill in a validated tenancy

## References

- [references/tenancy-profile.md](references/tenancy-profile.md): Reusable schema for tenancy context and onboarding status
- [references/personas.md](references/personas.md): Persona-to-action mapping for end users and operators
- [references/governance.md](references/governance.md): Approval and execution guardrails for DR actions
- [references/fsdr-setup-reference.md](references/fsdr-setup-reference.md): Oracle-aligned summary of prerequisites, IAM policy guidance, protection group members, and member preparation notes

## Assets

- [assets/tenancy-profile-template.yaml](assets/tenancy-profile-template.yaml): Starter tenancy profile that can be reused across onboarding sessions

## Starter scripts

- [scripts/check_tenancy_profile.sh](scripts/check_tenancy_profile.sh): Validate required tenancy profile fields and emit a status summary
- [scripts/summarize_operation_request.sh](scripts/summarize_operation_request.sh): Normalize an operations request into an action category and risk level

## Suggested repo evolution

- Add read-only validation scripts under `scripts/`
- Add tenancy profile and policy references under `references/`
- Add managed tool integrations once the team is ready for live OCI execution
