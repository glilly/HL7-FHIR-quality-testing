#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKSPACE_ROOT="$(cd "${REPO_ROOT}/.." && pwd)"

KIT_DIR="${KIT_DIR:-${WORKSPACE_ROOT}/us-quality-core-test-kit}"
INFERNO_HTTP_PORT="${INFERNO_HTTP_PORT:-8088}"
FHIRPATH_PORT="${FHIRPATH_PORT:-6789}"
REFERENCE_SERVER_PORT="${REFERENCE_SERVER_PORT:-8089}"
REDIS_PORT="${REDIS_PORT:-6389}"

if [[ ! -d "${KIT_DIR}" ]]; then
  echo "Test kit not found at ${KIT_DIR}; run scripts/usqc-setup.sh first." >&2
  exit 1
fi

cd "${KIT_DIR}"
mkdir -p data/vista-on-fhir data/redis
chmod -R a+rwX data/redis 2>/dev/null || true
touch .dockerignore
grep -qxF "data/redis" .dockerignore || printf '\n# Vista-on-FHIR local runtime data\ndata/redis\n' >> .dockerignore
OVERRIDE_FILE="${KIT_DIR}/data/vista-on-fhir/docker-compose.override.yml"

if [[ ! -f "${OVERRIDE_FILE}" ]]; then
  cat > "${OVERRIDE_FILE}" <<YAML
services:
  nginx:
    ports: !override
      - "${INFERNO_HTTP_PORT}:80"
  fhirpath:
    ports: !override
      - "${FHIRPATH_PORT}:6789"
  inferno_reference_server:
    ports: !override
      - "${REFERENCE_SERVER_PORT}:8080"
  redis:
    ports: !override
      - "${REDIS_PORT}:6379"
YAML
fi

echo "Starting US Quality Core Inferno at http://localhost:${INFERNO_HTTP_PORT}"
echo "Reference server, if needed: http://localhost:${REFERENCE_SERVER_PORT}/reference-server/r4"
docker compose -f docker-compose.yml -f "${OVERRIDE_FILE}" up
