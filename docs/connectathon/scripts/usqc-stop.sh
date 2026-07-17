#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKSPACE_ROOT="$(cd "${REPO_ROOT}/.." && pwd)"

KIT_DIR="${KIT_DIR:-${WORKSPACE_ROOT}/us-quality-core-test-kit}"
OVERRIDE_FILE="${KIT_DIR}/data/vista-on-fhir/docker-compose.override.yml"

if [[ ! -d "${KIT_DIR}" ]]; then
  echo "Test kit not found at ${KIT_DIR}" >&2
  exit 1
fi

cd "${KIT_DIR}"
if [[ -f "${OVERRIDE_FILE}" ]]; then
  docker compose -f docker-compose.yml -f "${OVERRIDE_FILE}" down
else
  docker compose down
fi
