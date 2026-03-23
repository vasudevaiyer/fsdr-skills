# FSDR Assistant Team Onboarding

## What this is

The FSDR Assistant is a shared AI assistant for OCI Full Stack Disaster Recovery guidance.

It helps with:

- OCI FSDR introduction and scope
- tenancy onboarding questions
- prerequisites and IAM policy guidance
- policy tailoring and policy artifact drafting
- DR Protection Group setup guidance
- member preparation guidance
- readiness checks
- drill start and stop guidance
- multi-member preparation requests such as adding OKE and Database to a DRPG

This assistant is centrally managed. End users do not need to install local Codex skills.

## Who should use it

Use the assistant if you are:

- planning OCI FSDR onboarding
- validating prerequisites before setup
- preparing workload members for a DRPG
- checking readiness before a drill
- looking for guided FSDR workflow support

## How to access it

Use the shared FSDR assistant URL provided by the team.

Current local prototype endpoint:

- `http://127.0.0.1:8010/ui`

In production or team rollout, use the shared team URL instead of localhost.

## What to ask

You can ask questions in natural language.

Examples:

- `What is OCI FSDR?`
- `What IAM policies do I need for FSDR?`
- `Tailor the FSDR IAM policies for my tenancy and compartments`
- `Turn this FSDR policy draft into final OCI IAM policies and dynamic groups`
- `How do I prepare OKE for FSDR?`
- `What can I do to add database to a DRPG?`
- `I want to add OKE and Database to a DRPG. What should I do?`
- `Is billing-prod ready for a drill?`
- `Start a drill for billing-prod`

## How the assistant behaves

The assistant uses AI-based routing to decide what guidance is needed.

It can:

- route to one relevant capability for a focused question
- aggregate multiple capabilities for requests involving more than one member type
- keep tenancy-bound workflows separate from instruction-only guidance

Example:

- If you ask how to add both OKE and Database to a DRPG, the assistant will build one answer that combines the preparation requirements for both member types.

## What this assistant does not do

This assistant does not:

- replace official OCI documentation
- guarantee readiness without the required context and validation inputs
- bypass governance or approval requirements
- automatically perform production-impacting actions by default in this prototype

## Good usage pattern

Start with planning and preparation questions first.

Recommended flow:

1. Ask onboarding or prerequisite questions
2. Ask member preparation questions
3. Ask readiness questions
4. Ask drill execution questions only after readiness is clear

## If the answer is incomplete

If the assistant asks for more context, provide details such as:

- tenancy or environment
- source and target regions
- application scope
- member types involved
- readiness or protection group status

## Support model

End users:

- use the shared assistant UI
- do not install local skills

Maintainers:

- manage the skill definitions
- update routing and orchestration logic
- test and publish new versions

## Maintainers

Contact the FSDR assistant maintainers if:

- the routing looks incorrect
- a supported workflow is missing
- you need a new use case added
- the assistant output needs refinement


## If your team uses Codex directly

The packaged Codex skill is available under [codex-skills/oci-fsdr-assistant](/u01/scripts/oci_samples/fsdr/codex-skills/oci-fsdr-assistant).

Recommended prompt pattern for Codex users:

- `Use the OCI FSDR assistant skill and tailor IAM policies for payroll-prod`
- `Use the OCI FSDR assistant skill and create final FSDR IAM policy artifacts from this draft`

Suggested flow for policy work:

1. use policy tailoring first
2. review placeholders, compartments, persona, and dependency services
3. use policy creation second to generate review-ready artifacts

For Codex users, this packaged skill is the reusable workflow layer. The shared UI assistant remains the easier path for general end users.
