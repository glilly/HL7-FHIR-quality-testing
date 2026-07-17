#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKSPACE_ROOT="$(cd "${REPO_ROOT}/.." && pwd)"

KIT_DIR="${KIT_DIR:-${WORKSPACE_ROOT}/us-quality-core-test-kit}"
TITLE="${TITLE:-Vista/RPMS FHIR Server}"
FHIR_URL="${1:-${FHIR_URL:-}}"
PATIENT_IDS="${2:-${PATIENT_IDS:-}}"
ACCESS_TOKEN="${ACCESS_TOKEN:-}"
PRESET_FILE="${PRESET_FILE:-${KIT_DIR}/config/presets/vista_on_fhir_preset.json}"

if [[ -z "${FHIR_URL}" || -z "${PATIENT_IDS}" ]]; then
  echo "Usage: $0 <fhir-base-url> <comma-separated-patient-ids>" >&2
  echo "Example: $0 http://localhost:5177/fhir 14" >&2
  exit 2
fi

if [[ ! -d "${KIT_DIR}" ]]; then
  echo "Test kit not found at ${KIT_DIR}; run scripts/usqc-setup.sh first." >&2
  exit 1
fi

FHIR_URL="${FHIR_URL%/}"
mkdir -p "$(dirname "${PRESET_FILE}")"

python3 - "$PRESET_FILE" "$TITLE" "$FHIR_URL" "$PATIENT_IDS" "$ACCESS_TOKEN" <<'PY'
import json
import sys

path, title, url, patient_ids, access_token = sys.argv[1:]
inputs = [
    {
        "name": "url",
        "type": "text",
        "title": "FHIR Endpoint",
        "description": "URL of the FHIR endpoint",
        "value": url,
    },
    {
        "name": "patient_ids",
        "type": "text",
        "title": "Patient IDs",
        "description": "Comma separated list of Patient resource IDs",
        "value": patient_ids,
    },
]

if access_token:
    inputs.insert(
        1,
        {
            "name": "smart_auth_info",
            "optional": "true",
            "type": "auth_info",
            "value": {
                "auth_type": "public",
                "use_discovery": "false",
                "access_token": access_token,
            },
        },
    )

with open(path, "w", encoding="utf-8") as preset:
    json.dump(
        {
            "title": title,
            "id": None,
            "test_suite_id": "us_quality_core_v050",
            "inputs": inputs,
        },
        preset,
        indent=2,
    )
    preset.write("\n")
PY

echo "Wrote ${PRESET_FILE}"
echo "Open Inferno and select preset: ${TITLE}"
