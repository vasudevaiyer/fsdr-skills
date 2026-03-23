# Managed Assistant Deployment Model

This document describes how to use this repository behind a managed assistant.

## Objective

Use a Git repo for version control and a shared assistant for end-user access.

Users should not need local installation of the skill library.

## Architecture

- `Git repo`
  - source of truth for skills, references, assets, and helper scripts
- `CI or validation step`
  - runs basic verification from [VERIFY.md](../VERIFY.md)
- `Managed assistant runtime`
  - loads an approved repo branch or release tag
- `Enterprise identity`
  - controls who can use the assistant and what actions they can perform

## Runtime flow

1. A skill author updates the Git repo.
2. The change is reviewed and merged.
3. The approved version is published to the managed assistant runtime.
4. End users access the assistant through a shared chat or portal.
5. The assistant uses [SKILL.md](../SKILL.md) as the router.
6. The assistant loads the matching skill files for the user's request.

For the concrete application shape, see:

- [ui-backend-blueprint.md](ui-backend-blueprint.md)
- [backend-api.md](backend-api.md)

## User roles

Suggested starting roles:

- `viewer`
  - onboarding and readiness guidance
- `operator`
  - drill lifecycle workflows
- `admin`
  - configuration and setup guidance

## Recommended deployment phases

### Phase 1

- Git-backed skill library
- managed assistant
- guidance only

### Phase 2

- read-only backend validation
- tenancy and policy checks
- inventory lookup for protection groups and members

### Phase 3

- controlled drill start and stop actions
- audit logging
- stronger role-based guardrails

## Operational recommendations

- publish only reviewed content to the shared assistant
- keep `main` stable
- use feature branches for skill changes
- tag assistant-ready releases
- make the assistant load a known branch or tag, not arbitrary local state

## End-user access model

The end user should experience this as:

1. open the FSDR assistant
2. sign in
3. ask a question in plain language
4. follow the guided workflow

The end user should not need:

- Git access
- repo knowledge
- local setup
- skill file awareness

## Prototype exposure note

If you run the current backend prototype on `0.0.0.0`, it becomes reachable from outside the VM if the network allows it.

Do not treat the current prototype as internet-ready. It still lacks:

- real authentication in the app
- persistent storage
- rate limiting
- hardened deployment controls

For any non-local testing, place it behind at least one network control such as a VPN, IP allowlist, reverse proxy authentication, or restrictive security rules.
