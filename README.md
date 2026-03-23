# OCI FSDR Skills

This repository is a Git-backed skill library for OCI Full Stack Disaster Recovery.

It is designed for a managed assistant model:

- this Git repo is the source of truth
- the managed assistant is the runtime used by end users

## What is in this repo

- [SKILL.md](SKILL.md): root router skill
- [SKILLS.md](SKILLS.md): skill library index
- [skills/tenancy](skills/tenancy): tenancy onboarding and prerequisite skills
- [skills/operations](skills/operations): protection group, member preparation, readiness, and drill skills
- [references](references): shared FSDR guidance
- [assets](assets): reusable templates
- [scripts](scripts): small helper scripts for validation and intent normalization

## End-user model

End users should access these skills through a managed assistant, not by reading the repo directly.

Typical user requests:

- "Help me onboard a tenancy for OCI FSDR"
- "What prerequisites and IAM policies do I need?"
- "Help me create a protection group"
- "What members can I add to a protection group?"
- "Is this environment ready for a drill?"
- "Start a drill for this application"
- "Stop the current drill"

## Suggested user flow

1. Tenancy onboarding
2. Prerequisites and policies
3. Create protection group
4. Member preparation
5. DR readiness
6. Start drill or stop drill

## Repo workflow

Recommended branch model:

- `main`: stable assistant content
- `dev`: integration and review
- feature branches: individual changes

Recommended change flow:

1. Update or add skill files
2. Run the checks in [VERIFY.md](VERIFY.md)
3. Open a pull request
4. Merge to `main` after review
5. Publish the approved version to the managed assistant runtime

## Optional AI classifier

The backend can now use an optional AI classification layer before falling back to the built-in heuristic classifier.

Behavior:

- if `AI_CLASSIFIER_ENABLED=true` and the endpoint settings are present, the backend sends bounded classification prompts to the configured model
- the model may only return the supported FSDR taxonomy values
- invalid or failed AI responses automatically fall back to the local heuristic classifier
- routing still remains constrained by the local skill catalog

Environment variables:

- `AI_CLASSIFIER_ENABLED=true`
- `AI_CLASSIFIER_URL=<openai-compatible-chat-completions-endpoint>`
- `AI_CLASSIFIER_MODEL=<model-name>`
- `AI_CLASSIFIER_API_KEY=<optional-bearer-token>`
- `AI_CLASSIFIER_TIMEOUT_SECONDS=10`

Example:

```bash
export AI_CLASSIFIER_ENABLED=true
export AI_CLASSIFIER_URL=http://<host>/v1/chat/completions
export AI_CLASSIFIER_MODEL=<model-name>
export AI_CLASSIFIER_API_KEY=<token>
./scripts/run-backend.sh
```

## Local demo

Use the demo router to see which skill this first cut would select for a prompt:

```bash
./scripts/demo_skill_router.sh "Help me onboard a tenancy for OCI FSDR"
./scripts/demo_skill_router.sh "What IAM policies do I need for FSDR?"
./scripts/demo_skill_router.sh "Help me create a protection group"
./scripts/demo_skill_router.sh "What members can I add to a protection group?"
./scripts/demo_skill_router.sh "Is billing-prod ready for a drill?"
./scripts/demo_skill_router.sh "Start a drill for billing-prod"
./scripts/demo_skill_router.sh "Stop the current drill"
```

This is a dry-run router only. It shows the expected skill file and why it matched.

## Backend prototype

A minimal FastAPI backend scaffold now lives under [backend](backend).

Install and run it like this:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
./scripts/run-backend.sh install-service
./scripts/run-backend.sh start
```

The preferred path is now `systemd`-managed. `install-service` installs and enables `fsdr-backend.service`, and `start`/`stop`/`restart`/`status` automatically manage that service once it exists. The service binds to `0.0.0.0` on port `8010`, uses the configured Python interpreter, and stays up after logout and across reboots.

If `systemd` is not available, the same script still falls back to the older `nohup` background launcher.

For local access, open:

- `http://127.0.0.1:8010/docs`
- `http://127.0.0.1:8010/api/me`
- `http://127.0.0.1:8010/api/skills/version`
- `http://127.0.0.1:8010/ui`

For remote access, use your VM's public IP or DNS name with the same port.

To use a different port:

```bash
./scripts/run-backend.sh start 8020
```

The backend host is fixed to `0.0.0.0`.

To restart it on a different port:

```bash
./scripts/run-backend.sh restart 8010
```

To manage the background process:

```bash
./scripts/run-backend.sh status
./scripts/run-backend.sh stop
./scripts/run-backend.sh restart
```

The backend is intentionally Phase 1 only:

- in-memory storage
- repo-backed skill routing
- no live OCI calls
- no persistent database yet

The frontend prototype at `/ui` currently supports:

- API status and skill version display
- tenancy registration
- tenancy selection
- session creation
- prompt-driven chat against the current routing logic

## Read-only OCI inventory

The prototype now includes one live read-only OCI inventory endpoint for compute infrastructure:

```bash
curl "http://127.0.0.1:8010/api/tenancies/<tenancy_id>/inventory/compute?compartment_id=<compartment_ocid>"
```

Optional query parameters:

- `region`
- `instance_id`

This endpoint returns compute instances plus attached boot volumes, block volumes, and VNIC context.

Important: for live OCI lookups, the compartment must be an OCI compartment OCID. If your tenancy profile stores only friendly names in `compartments_in_scope`, pass `compartment_id` explicitly in the request.

If you expose it beyond localhost, treat it as a prototype and put it behind network controls such as a firewall, security list, IP allowlist, VPN, or reverse proxy with authentication.

## Managed assistant model

Use this repo behind a shared assistant:

1. Users open the assistant
2. Users authenticate with enterprise identity
3. The assistant loads the approved repo version
4. The assistant routes requests through [SKILL.md](SKILL.md)
5. The assistant uses the specific skill files as needed

See [docs/managed-assistant.md](docs/managed-assistant.md) for the deployment model.
See [docs/ui-backend-blueprint.md](docs/ui-backend-blueprint.md) for the application layout.
See [docs/backend-api.md](docs/backend-api.md) for the first-cut API contract.
