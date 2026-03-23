#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 4 ]]; then
  cat <<'EOF'
Usage:
  check_tenancy_profile.sh <tenancy_ocid> <home_region> <compartments_csv> <persona> [intended_use]

Example:
  check_tenancy_profile.sh ocid1.tenancy.oc1..example us-ashburn-1 finance-prod-shared,finance-prod-apps operator drill
EOF
  exit 1
fi

tenancy_ocid="$1"
home_region="$2"
compartments_csv="$3"
persona="$4"
intended_use="${5:-onboarding}"

status="ready"

if [[ -z "$tenancy_ocid" || "$tenancy_ocid" != ocid1.tenancy.* ]]; then
  echo "blocked: tenancy_ocid must look like an OCI tenancy OCID"
  exit 0
fi

if [[ -z "$home_region" ]]; then
  echo "blocked: home_region is required"
  exit 0
fi

if [[ -z "$compartments_csv" ]]; then
  echo "blocked: at least one compartment is required"
  exit 0
fi

case "$persona" in
  viewer|operator|admin)
    ;;
  *)
    echo "blocked: persona must be one of viewer, operator, admin"
    exit 0
    ;;
esac

case "$intended_use" in
  onboarding|readiness|configure|start-drill|stop-drill)
    ;;
  *)
    echo "blocked: intended_use must be one of onboarding, readiness, configure, start-drill, stop-drill"
    exit 0
    ;;
esac

if [[ "$persona" == "viewer" && "$intended_use" =~ ^(configure|start-drill|stop-drill)$ ]]; then
  status="needs approval"
fi

if [[ "$persona" == "operator" && "$intended_use" == "configure" ]]; then
  status="needs approval"
fi

printf '%s: tenancy=%s region=%s persona=%s intended_use=%s compartments=%s\n' \
  "$status" "$tenancy_ocid" "$home_region" "$persona" "$intended_use" "$compartments_csv"
