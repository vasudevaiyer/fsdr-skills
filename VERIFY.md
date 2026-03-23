# Verify The Skills

Run these checks from the repo root.

## File inventory

```bash
find . -maxdepth 3 -type f | sort
```

Confirm the output includes:

- `SKILL.md`
- `SKILLS.md`
- `README.md`
- `VERIFY.md`
- `docs/managed-assistant.md`
- `docs/ai-routing-design.md`
- `skills/tenancy/fsdr-tenancy-onboard.md`
- `skills/tenancy/fsdr-prerequisites-and-policies.md`
- `skills/tenancy/fsdr-policy-tailoring.md`
- `skills/operations/fsdr-create-protection-group.md`
- `skills/operations/fsdr-member-preparation.md`
- `skills/operations/fsdr-dr-readiness.md`
- `skills/operations/fsdr-start-drill.md`
- `skills/operations/fsdr-stop-drill.md`
- `skills/prerequisites/members/fsdr-prepare-oke.md`
- `skills/prerequisites/members/fsdr-prepare-database.md`
- `skills/prerequisites/members/fsdr-prepare-autonomous-database.md`
- `skills/prerequisites/members/fsdr-prepare-compute.md`
- `skills/prerequisites/members/fsdr-prepare-integration-instance.md`
- `skills/prerequisites/members/fsdr-prepare-application.md`
- `tests/test_router.py`
- `tests/test_ai_classifier.py`

## Script and backend syntax checks

```bash
bash -n scripts/check_tenancy_profile.sh
bash -n scripts/summarize_operation_request.sh
bash -n scripts/demo_skill_router.sh
/u01/venv/bin/python -m py_compile backend/*.py tests/test_router.py tests/test_ai_classifier.py
```

All commands should exit cleanly with no output.

## Routing regression tests

```bash
/u01/venv/bin/python -m pytest -q tests/test_router.py tests/test_ai_classifier.py
```

Expected result:

- `14 passed`

The regression set validates:

- OKE member preparation routes to the exact member skill
- Autonomous Database member preparation routes to the exact member skill
- member-preparation guidance stays tenancy-optional
- DRPG inspection remains tenancy-bound
- prechecks route through the readiness skill
- valid AI classifier responses are accepted
- invalid AI classifier responses fall back to heuristics
- policy-tailoring requests route to the tenancy policy-tailoring skill
- tailored policy responses include tenancy-scoped starter statements when context exists

## Helper script sample runs

```bash
./scripts/check_tenancy_profile.sh ocid1.tenancy.oc1..exampleuniqueid us-ashburn-1 finance-prod-shared,finance-prod-apps operator start-drill
./scripts/summarize_operation_request.sh "Stop drill for billing in Phoenix"
./scripts/demo_skill_router.sh "Help me create a protection group"
```

Expected shape of results:

- `check_tenancy_profile.sh` returns `ready:` or `needs approval:`
- `summarize_operation_request.sh` returns `action=stop-drill risk=medium`
- `demo_skill_router.sh` returns a `skill=` path and a short routing reason

## Backend smoke test

If dependencies are installed:

```bash
./scripts/run-backend.sh
```

Then in another shell:

```bash
curl http://127.0.0.1:8010/api/me
curl http://127.0.0.1:8010/api/skills/version
curl http://127.0.0.1:8010/ui
```

Expected behavior:

- `/api/me` returns the demo user
- `/api/skills/version` returns the configured repo ref and router file
- `/ui` returns the frontend page

If you are testing from another machine, replace `127.0.0.1` with the VM's reachable IP or DNS name.

## Optional AI classifier smoke test

Start the backend with AI classifier variables configured:

```bash
export AI_CLASSIFIER_ENABLED=true
export AI_CLASSIFIER_URL=http://<host>/v1/chat/completions
export AI_CLASSIFIER_MODEL=<model-name>
export AI_CLASSIFIER_API_KEY=<token>
./scripts/run-backend.sh
```

Then try broader natural-language prompts such as:

- `We are new to FSDR. What should we do first in this tenancy?`
- `I need to understand what needs to be in place before we use Autonomous Database with FSDR.`
- `Show me how to inspect the DR protection group for billing.`

Expected behavior:

- the backend still routes only to supported skills
- invalid or unavailable AI responses fall back to the heuristic classifier

## Prompt simulation

Use these prompts in the managed assistant or local Codex environment:

- `Help me onboard a tenancy for OCI FSDR`
- `What are the prerequisites and IAM policies for FSDR?`
- `Please tailor the FSDR IAM policies for my tenancy`
- `How do I prepare OKE clusters for FSDR?`
- `How do I prepare Autonomous Database for FSDR?`
- `Read DRPG for payroll`
- `Explore plans for billing`
- `Run prechecks for payroll`
- `Is this environment ready for a drill?`
- `Start a drill for billing-prod`
- `Stop the current drill`

Expected behavior:

- missing tenancy context routes to onboarding only for tenancy-bound workflows
- setup questions route to the setup skills
- member-preparation guidance can answer without tenancy selection
- readiness is checked before drill execution
- drill actions require explicit user intent
