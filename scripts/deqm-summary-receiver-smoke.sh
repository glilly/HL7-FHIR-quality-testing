#!/usr/bin/env bash
# Phase 2 helper: optional DEQM receiver + validator smoke.
# Default: structural check only. With --docker, tries deqm-test-server POST.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="${1:-$ROOT/docs/deqm-summary/prototypes/CMS165v14-summary-deqm.json}"
BUNDLE="$ROOT/docs/deqm-summary/prototypes/Bundle-CMS165v14-summary-transaction.json"

echo "== structural check =="
python3 "$ROOT/scripts/check-deqm-summary.py" "$REPORT"

if [[ "${2:-}" != "--docker" ]]; then
  cat <<EOF

Next (manual Phase 2):
  # FHIR Validator service
  docker run --rm -d --name fhir-validator -p 4567:4567 infernocommunity/fhir-validator-service

  # DEQM test server (clone once)
  # git clone https://github.com/projecttacoma/deqm-test-server.git ~/work/deqm-test-server
  # then start per its README with VALIDATE=true

  # Re-run this script with --docker after receiver is up on :3000
  $0 "$REPORT" --docker
EOF
  exit 0
fi

echo "== POST transaction Bundle to localhost:3000 =="
if ! curl -fsS -o /dev/null "http://127.0.0.1:3000/4_0_1/metadata"; then
  echo "FAIL: no DEQM test server metadata at http://127.0.0.1:3000" >&2
  exit 1
fi
curl -fsS -X POST "http://127.0.0.1:3000/4_0_1" \
  -H "Content-Type: application/fhir+json" \
  --data-binary @"$BUNDLE" | tee /tmp/deqm-summary-post-response.json
echo
echo "OK: posted $BUNDLE"
