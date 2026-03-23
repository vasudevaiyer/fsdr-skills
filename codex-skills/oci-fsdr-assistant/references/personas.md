# Personas

Use this reference when mapping a user to allowed FSDR actions.

## Personas

- `viewer`
  - Can review readiness, inventory, and status
  - Cannot configure or execute DR actions
- `operator`
  - Can run onboarding checks, readiness checks, and drill workflows
  - Cannot change governance settings
- `admin`
  - Can configure tenancy and FSDR resources
  - Can prepare plans and supporting configuration

## Mapping guidance

- If the user describes themselves as an application owner, default to `viewer` unless they explicitly manage DR operations.
- If the user manages day-to-day DR exercises, default to `operator`.
- If the user owns tenancy setup, policy, or environment configuration, default to `admin`.
- If the user owns drill lifecycle management, default to `operator` unless the team uses a stricter custom policy.

## Conflict handling

- If the requested action exceeds the user's persona, return `needs approval`.
- If the user's role is unknown, keep the request in onboarding until a persona is established.
