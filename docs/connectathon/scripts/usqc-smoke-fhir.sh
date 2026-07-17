#!/usr/bin/env bash
set -euo pipefail

FHIR_URL="${1:-${FHIR_URL:-}}"
PATIENT_IDS="${2:-${PATIENT_IDS:-}}"
ACCESS_TOKEN="${ACCESS_TOKEN:-}"

if [[ -z "${FHIR_URL}" || -z "${PATIENT_IDS}" ]]; then
  echo "Usage: $0 <fhir-base-url> <comma-separated-patient-ids>" >&2
  echo "Example: $0 http://localhost:5177/fhir 14" >&2
  exit 2
fi

FHIR_URL="${FHIR_URL%/}"
AUTH_ARGS=()
if [[ -n "${ACCESS_TOKEN}" ]]; then
  AUTH_ARGS=(-H "Authorization: Bearer ${ACCESS_TOKEN}")
fi

echo "Checking CapabilityStatement: ${FHIR_URL}/metadata"
curl -fsS "${AUTH_ARGS[@]}" "${FHIR_URL}/metadata" >/dev/null

IFS=',' read -r -a IDS <<< "${PATIENT_IDS}"
for id in "${IDS[@]}"; do
  id="$(echo "${id}" | xargs)"
  [[ -z "${id}" ]] && continue
  echo "Checking Patient/${id}"
  curl -fsS "${AUTH_ARGS[@]}" "${FHIR_URL}/Patient/${id}" >/dev/null
done

echo "FHIR smoke checks passed for ${FHIR_URL}"
