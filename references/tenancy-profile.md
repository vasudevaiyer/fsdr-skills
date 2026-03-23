# Tenancy Profile

Use this reference to normalize tenancy onboarding data into a reusable context.

## Required fields

- `tenancy_name`: Friendly display name for the tenancy
- `tenancy_ocid`: OCI tenancy identifier
- `home_region`: The tenancy home region
- `target_regions`: Regions relevant to the requested FSDR workflow
- `compartments_in_scope`: Compartments the user wants to inspect or operate in
- `persona`: One of `viewer`, `operator`, or `admin`
- `intended_use`: One of `onboarding`, `readiness`, `configure`, `start-drill`, `stop-drill`
- `onboarding_status`: One of `ready`, `blocked`, or `needs approval`

## Optional fields

- `tenancy_alias`: Short label shown in chat or UI
- `business_unit`: Owning team or business group
- `application_name`: Application or service in scope
- `environment_name`: Such as `dev`, `test`, `stage`, or `prod`
- `contacts`: Owners or escalation contacts
- `notes`: Free-form context that may help future operations

## Example

```yaml
tenancy_name: Finance Production
tenancy_ocid: ocid1.tenancy.oc1..exampleuniqueid
home_region: us-ashburn-1
target_regions:
  - us-ashburn-1
  - us-phoenix-1
compartments_in_scope:
  - finance-prod-shared
  - finance-prod-apps
persona: operator
intended_use: start-drill
onboarding_status: ready
application_name: billing-platform
environment_name: prod
```

## Normalization rules

- Store region names as OCI region identifiers.
- Store compartment values as names or OCIDs, but use one format consistently inside a session.
- If the user asks for multiple actions, keep `intended_use` aligned to the highest-risk requested action.
- Update `onboarding_status` only after prerequisite checks are complete.
