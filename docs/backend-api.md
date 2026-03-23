# FSDR Backend API

This document defines the first-cut API surface for the managed FSDR assistant.

## Principles

- keep tenancy registration explicit
- keep chat stateless at the HTTP boundary and stateful in storage
- expose skill version in responses for traceability
- do not expose direct OCI execution endpoints in Phase 1

## Authentication

These endpoints assume enterprise authentication in front of the app.

## Endpoints

### `GET /api/me`

Returns the signed-in user profile.

Response shape:

```json
{
  "id": "user_123",
  "email": "jane.doe@example.com",
  "display_name": "Jane Doe",
  "role": "operator"
}
```

### `GET /api/skills/version`

Returns the currently loaded skill library version.

Response shape:

```json
{
  "repo_ref": "main",
  "router_file": "SKILL.md",
  "loaded_at": "2026-03-14T12:00:00Z"
}
```

### `GET /api/tenancies`

Lists tenancy profiles visible to the current user.

### `POST /api/tenancies`

Creates a tenancy profile.

Request shape:

```json
{
  "tenancy_name": "Finance Production",
  "tenancy_ocid": "ocid1.tenancy.oc1..exampleuniqueid",
  "home_region": "us-ashburn-1",
  "target_regions": ["us-ashburn-1", "us-phoenix-1"],
  "compartments_in_scope": ["finance-prod-shared", "finance-prod-apps"],
  "persona": "operator",
  "intended_use": "start-drill",
  "application_name": "billing-platform",
  "environment_name": "prod"
}
```

Response shape:

```json
{
  "id": "tenancy_123",
  "onboarding_status": "ready"
}
```

### `GET /api/tenancies/{tenancy_id}`

Returns one tenancy profile.

### `PATCH /api/tenancies/{tenancy_id}`

Updates a tenancy profile.

### `POST /api/sessions`

Creates a new assistant session.

Request shape:

```json
{
  "tenancy_profile_id": "tenancy_123"
}
```

Response shape:

```json
{
  "id": "session_123",
  "current_skill": "SKILL.md",
  "skill_version": "main"
}
```

### `GET /api/sessions`

Lists recent sessions for the current user.

### `GET /api/sessions/{session_id}`

Returns one session plus message metadata.

### `POST /api/sessions/{session_id}/messages`

Posts a user message and returns the routed skill and assistant response.

Request shape:

```json
{
  "message": "Help me create a protection group"
}
```

Response shape:

```json
{
  "session_id": "session_123",
  "selected_skill": "skills/operations/fsdr-create-protection-group.md",
  "routing_reason": "protection group setup request",
  "assistant_message": "To create a DR Protection Group, I need the source region, target region, application scope, and bucket details.",
  "skill_version": "main"
}
```

### `GET /api/sessions/{session_id}/messages`

Returns the message history for a session.

### `GET /api/audit`

Lists audit events for admin or support users.

## Error model

Use a simple consistent error body:

```json
{
  "error": {
    "code": "validation_error",
    "message": "tenancy_ocid is required"
  }
}
```

## Phase 2 extensions

These should be added later, not in the first cut:

- `POST /api/tenancies/{tenancy_id}/validate`
- `GET /api/tenancies/{tenancy_id}/inventory`
- `POST /api/drills/start`
- `POST /api/drills/stop`

## Current read-only OCI inventory extension

The prototype now includes one tenancy-scoped read-only OCI endpoint:

### `GET /api/tenancies/{tenancy_id}/inventory/compute`

Query parameters:

- `compartment_id` (optional if the tenancy profile already stores a compartment OCID in `compartments_in_scope`)
- `region` (optional, defaults to the tenancy home region)
- `instance_id` (optional, narrows the response to one compute instance)

Response shape:

```json
{
  "tenancy_id": "tenancy_123",
  "compartment_id": "ocid1.compartment.oc1..example",
  "region": "us-chicago-1",
  "instance_count": 1,
  "instances": [
    {
      "instance_id": "ocid1.instance.oc1..example",
      "display_name": "billing-app-01",
      "lifecycle_state": "RUNNING",
      "shape": "VM.Standard3.Flex",
      "availability_domain": "kIdk:US-CHICAGO-1-AD-1",
      "fault_domain": "FAULT-DOMAIN-1",
      "compartment_id": "ocid1.compartment.oc1..example",
      "region": "us-chicago-1",
      "boot_volume": {
        "volume_id": "ocid1.bootvolume.oc1..example",
        "display_name": "billing-app-01-boot",
        "volume_type": "boot"
      },
      "block_volumes": [],
      "vnics": []
    }
  ]
}
```

## Backend implementation notes

- use [references/tenancy-profile.md](../references/tenancy-profile.md) as the tenancy shape
- use [SKILL.md](../SKILL.md) as the router entry point
- keep the routing logic observable by returning `selected_skill` and `routing_reason`
- store `skill_version` on every session for reproducibility

## Prototype status

The current repo includes a minimal FastAPI implementation under [../backend](../backend):

- `backend/main.py`
- `backend/models.py`
- `backend/store.py`
- `backend/router.py`
- `backend/config.py`

This implementation is intentionally limited to:

- in-memory storage
- one seeded demo user
- repo-local skill routing
- stub assistant messages instead of live model calls
