# FSDR UI And Backend Blueprint

This document turns the managed assistant idea into a concrete first implementation shape.

## Objective

Build a shared FSDR web application where users:

1. sign in
2. register or select a tenancy
3. ask for FSDR help in plain language
4. follow guided workflows backed by this Git repo

## Delivery model

- `Git repo`
  - source of truth for skills, references, templates, and helper scripts
- `Web UI`
  - end-user entry point
- `Backend service`
  - skill loader, router, session manager, tenancy registry, audit layer
- `Agent runtime`
  - Codex or API-backed reasoning layer used by the backend
- `Data store`
  - users, tenancies, sessions, skill version, audit records

## Phase 1 scope

Phase 1 is guidance only.

The application should:

- register tenancy context
- route requests to the right skill
- render guided steps
- save session history

The application should not yet:

- perform live OCI validation
- start or stop real drills
- modify OCI resources

## UI pages

### 1. Login

Purpose:

- authenticate the user with enterprise identity

Core elements:

- sign-in button
- session-expired handling

### 2. Dashboard

Purpose:

- landing page after sign-in

Core elements:

- selected tenancy card
- recent sessions
- common tasks
- version of the loaded skill library

Suggested task shortcuts:

- onboard a tenancy
- check prerequisites and IAM policies
- create a protection group
- prepare protection group members
- check drill readiness
- start a drill
- stop a drill

### 3. Tenancy Registry

Purpose:

- create, edit, and select tenancy profiles

Core elements:

- list of registered tenancies
- add-tenancy form
- edit-tenancy form
- status badge: `ready`, `blocked`, `needs approval`

Base the form on [assets/tenancy-profile-template.yaml](../assets/tenancy-profile-template.yaml).

### 4. Assistant Chat

Purpose:

- primary skill-driven interaction surface

Core elements:

- message timeline
- selected tenancy context
- current skill chip or label
- suggested next actions
- confirmation panel for drill requests

### 5. Session History

Purpose:

- review previous conversations and outcomes

Core elements:

- session list
- filters by tenancy and date
- conversation transcript
- skill version used

### 6. Admin Console

Purpose:

- operational control for the managed assistant

Core elements:

- current Git branch or release tag
- deployment status
- usage counts
- recent errors
- audit events

## Frontend routes

Suggested first-cut routes:

- `/login`
- `/dashboard`
- `/tenancies`
- `/tenancies/new`
- `/tenancies/:id`
- `/chat`
- `/sessions`
- `/sessions/:id`
- `/admin`

## Backend modules

### 1. Auth module

Responsibilities:

- enterprise login
- token/session validation
- user-role lookup

### 2. Tenancy registry module

Responsibilities:

- CRUD for tenancy profiles
- status tracking
- tenancy selection per session

Use [references/tenancy-profile.md](../references/tenancy-profile.md) as the canonical shape.

### 3. Skill repository module

Responsibilities:

- load approved Git branch or release tag
- read [SKILL.md](../SKILL.md)
- resolve referenced skill files
- expose the loaded skill version to the UI

### 4. Routing module

Responsibilities:

- map user request to the first matching skill
- attach routing reason
- use [scripts/demo_skill_router.sh](../scripts/demo_skill_router.sh) logic as the first prototype, then move to backend-native routing

### 5. Session module

Responsibilities:

- create sessions
- store messages
- store selected tenancy
- store skill decisions

### 6. Audit module

Responsibilities:

- store user, tenancy, skill, timestamp, and action summary
- record confirmations for drill start and stop requests

### 7. Agent module

Responsibilities:

- build the agent prompt from:
  - root router
  - selected skill
  - tenancy context
  - recent conversation
- return the next guided step

## Data model

### User

- `id`
- `email`
- `display_name`
- `role`
- `created_at`

### TenancyProfile

- `id`
- `owner_user_id`
- `tenancy_name`
- `tenancy_ocid`
- `home_region`
- `target_regions`
- `compartments_in_scope`
- `persona`
- `intended_use`
- `onboarding_status`
- `application_name`
- `environment_name`
- `created_at`
- `updated_at`

### Session

- `id`
- `user_id`
- `tenancy_profile_id`
- `current_skill`
- `skill_version`
- `status`
- `created_at`
- `updated_at`

### Message

- `id`
- `session_id`
- `role`
- `content`
- `routing_reason`
- `created_at`

### AuditEvent

- `id`
- `user_id`
- `tenancy_profile_id`
- `session_id`
- `event_type`
- `summary`
- `created_at`

## Request lifecycle

1. User signs in.
2. User selects a tenancy or creates one.
3. User sends a message in chat.
4. Backend loads the approved skill library version.
5. Backend routes the request starting from [SKILL.md](../SKILL.md).
6. Backend builds the prompt using the selected skill and tenancy context.
7. Agent returns the next guided step.
8. Backend stores the message, routing decision, and session state.

## Repo integration

Use a simple deployment contract:

- `main` is stable
- feature branches are for draft changes
- tagged releases are preferred for assistant deployments

Suggested backend config:

- `SKILL_REPO_PATH`
- `SKILL_REPO_REF`
- `SKILL_ROUTER_FILE=SKILL.md`

## Recommended implementation stack

- frontend: Next.js or React
- backend: FastAPI or Node.js
- database: PostgreSQL
- background jobs later: Redis queue or equivalent for long-running actions

## First build milestone

Build only these features first:

1. login
2. tenancy registry
3. assistant chat
4. Git-backed skill loading
5. message routing
6. saved sessions

That is enough to demonstrate the product before adding live OCI integrations.
