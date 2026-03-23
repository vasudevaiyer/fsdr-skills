#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  cat <<'EOF'
Usage:
  summarize_operation_request.sh "<request text>"

Example:
  summarize_operation_request.sh "Stop drill for billing in Phoenix"
EOF
  exit 1
fi

request_text="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"
action="inspect"
risk="low"

if [[ "$request_text" == *"stop drill"* || "$request_text" == *"end drill"* || "$request_text" == *"terminate drill"* ]]; then
  action="stop-drill"
  risk="medium"
elif [[ "$request_text" == *"start drill"* || "$request_text" == *"run drill"* || "$request_text" == *"drill"* || "$request_text" == *"exercise"* ]]; then
  action="start-drill"
  risk="medium"
elif [[ "$request_text" == *"readiness"* || "$request_text" == *"precheck"* || "$request_text" == *"validate"* ]]; then
  action="readiness"
  risk="low"
elif [[ "$request_text" == *"configure"* || "$request_text" == *"setup"* || "$request_text" == *"create"* ]]; then
  action="configure"
  risk="medium"
fi

printf 'action=%s risk=%s\n' "$action" "$risk"
