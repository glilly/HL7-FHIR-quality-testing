#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
WORKSPACE_ROOT="$(cd "${REPO_ROOT}/.." && pwd)"

KIT_REPO="${KIT_REPO:-https://github.com/inferno-framework/us-quality-core-test-kit.git}"
KIT_DIR="${KIT_DIR:-${WORKSPACE_ROOT}/us-quality-core-test-kit}"

if [[ -d "${KIT_DIR}/.git" ]]; then
  echo "Updating ${KIT_DIR}"
  git -C "${KIT_DIR}" pull --ff-only
else
  echo "Cloning ${KIT_REPO} into ${KIT_DIR}"
  git clone "${KIT_REPO}" "${KIT_DIR}"
fi

echo "US Quality Core test kit is available at ${KIT_DIR}"
