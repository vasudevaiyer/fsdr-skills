#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  cat <<'EOF'
Usage:
  demo_skill_router.sh "<request text>"

Examples:
  demo_skill_router.sh "Help me onboard a tenancy for OCI FSDR"
  demo_skill_router.sh "What IAM policies do I need for FSDR?"
  demo_skill_router.sh "Help me create a protection group"
  demo_skill_router.sh "What members can I add to a protection group?"
  demo_skill_router.sh "Is billing-prod ready for a drill?"
  demo_skill_router.sh "Start a drill for billing-prod"
  demo_skill_router.sh "Stop the current drill"
EOF
  exit 1
fi

request_text="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"
skill="SKILL.md"
reason="default router"

if [[ "$request_text" == *"what is fsdr"* || "$request_text" == *"what is oci fsdr"* || "$request_text" == *"intro to fsdr"* || "$request_text" == *"introduction to fsdr"* || "$request_text" == *"what fsdr is not"* || "$request_text" == *"what can fsdr do"* ]]; then
  skill="skills/tenancy/fsdr-introduction.md"
  reason="fsdr overview request"
elif [[ "$request_text" == *"compute instance"* || "$request_text" == *"compute instances"* || "$request_text" == *"boot volume"* || "$request_text" == *"block volume"* || "$request_text" == *"attached volumes"* || "$request_text" == *"infrastructure inventory"* || "$request_text" == *"instance inventory"* || "$request_text" == *"list instances"* ]]; then
  skill="skills/operations/fsdr-read-infrastructure.md"
  reason="read-only infrastructure inventory request"
elif [[ "$request_text" == *"stop drill"* || "$request_text" == *"stop a drill"* || "$request_text" == *"end drill"* || "$request_text" == *"terminate drill"* ]]; then
  skill="skills/operations/fsdr-stop-drill.md"
  reason="explicit stop-drill request"
elif [[ "$request_text" == *"start drill"* || "$request_text" == *"start a drill"* || "$request_text" == *"run drill"* || "$request_text" == *"exercise"* ]]; then
  skill="skills/operations/fsdr-start-drill.md"
  reason="explicit start-drill request"
elif [[ "$request_text" == *"ready for a drill"* || "$request_text" == *"readiness"* || "$request_text" == *"precheck"* || "$request_text" == *"validate"* ]]; then
  skill="skills/operations/fsdr-dr-readiness.md"
  reason="readiness or precheck request"
elif [[ "$request_text" == *"member"* || "$request_text" == *"members"* || "$request_text" == *"prepare each member"* || "$request_text" == *"prepare the members"* ]]; then
  skill="skills/operations/fsdr-member-preparation.md"
  reason="member eligibility or preparation request"
elif [[ "$request_text" == *"create protection group"* || "$request_text" == *"protection group"* || "$request_text" == *"dr protection group"* ]]; then
  skill="skills/operations/fsdr-create-protection-group.md"
  reason="protection group setup request"
elif [[ "$request_text" == *"iam polic"* || "$request_text" == *"prereq"* || "$request_text" == *"policy"* || "$request_text" == *"permissions"* ]]; then
  skill="skills/tenancy/fsdr-prerequisites-and-policies.md"
  reason="prerequisites or IAM policy request"
elif [[ "$request_text" == *"onboard"* || "$request_text" == *"new to oci fsdr"* || "$request_text" == *"get started"* || "$request_text" == *"tenancy"* ]]; then
  skill="skills/tenancy/fsdr-tenancy-onboard.md"
  reason="tenancy onboarding request"
fi

printf 'request=%s\nskill=%s\nreason=%s\n' "$1" "$skill" "$reason"
