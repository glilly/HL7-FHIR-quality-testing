#!/usr/bin/env bash
# Phase 2 helper: structural check + optional validator + deqm-test-server POST.
# Default: structural check only.
#   --validate  POST to Inferno fhir-validator-service (:4567) with DEQM profile
#   --docker    POST transaction Bundle to deqm-test-server (:3000)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="${1:-$ROOT/docs/deqm-summary/prototypes/CMS165v14-summary-deqm.json}"
BUNDLE="$ROOT/docs/deqm-summary/prototypes/Bundle-CMS165v14-summary-transaction.json"
PROFILE='http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/summary-measurereport-deqm'
DO_VALIDATE=0
DO_DOCKER=0
shift || true
for arg in "$@"; do
  case "$arg" in
    --validate) DO_VALIDATE=1 ;;
    --docker) DO_DOCKER=1 ;;
    *)
      echo "Unknown arg: $arg" >&2
      exit 2
      ;;
  esac
done

echo "== structural check =="
python3 "$ROOT/scripts/check-deqm-summary.py" "$REPORT"

if [[ "$DO_VALIDATE" -eq 0 && "$DO_DOCKER" -eq 0 ]]; then
  cat <<EOF

Next (manual Phase 2):
  # FHIR Validator service (DISABLE_TX avoids tx.fhir.org hangs)
  docker run --rm -d --name fhir-validator -p 4567:4567 \\
    -e DISABLE_TX=true infernocommunity/fhir-validator-service
  curl -X PUT 'http://127.0.0.1:4567/igs/hl7.fhir.us.davinci-deqm?version=5.0.0'

  # DEQM test server (clone once; needs MongoDB + Redis)
  # git clone https://github.com/projecttacoma/deqm-test-server.git ~/work/deqm-test-server
  # npm install && npm run db:setup && npm start

  $0 "$REPORT" --validate --docker
EOF
  exit 0
fi

if [[ "$DO_VALIDATE" -eq 1 ]]; then
  echo "== FHIR Validator (DEQM Summary profile) =="
  if ! curl -fsS -o /dev/null "http://127.0.0.1:4567/version"; then
    echo "FAIL: no validator at http://127.0.0.1:4567" >&2
    exit 1
  fi
  # Ensure DEQM package is loaded (idempotent; may take several minutes first time)
  if ! curl -fsS "http://127.0.0.1:4567/profiles" | grep -q 'summary-measurereport-deqm'; then
    echo "Loading hl7.fhir.us.davinci-deqm#5.0.0 ..."
    curl -fsS -X PUT 'http://127.0.0.1:4567/igs/hl7.fhir.us.davinci-deqm?version=5.0.0' >/tmp/deqm-ig-load.json
  fi
  Q=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$PROFILE'))")
  curl -fsS -X POST "http://127.0.0.1:4567/validate?profile=$Q" \
    -H 'Content-Type: application/fhir+json' \
    --data-binary @"$REPORT" | tee /tmp/deqm-validate-oo.json >/dev/null
  python3 - <<'PY'
import json, sys
from collections import Counter
oo = json.load(open("/tmp/deqm-validate-oo.json"))
issues = oo.get("issue") or []
counts = Counter(i.get("severity") for i in issues)
print("severity:", dict(counts))
# Known IG/validator noise also present on DEQM STU5 golden summ-measurereport02:
KNOWN = (
    "Unable to resolve profile CanonicalType[http://hl7.org/fhir/5.0/StructureDefinition/extension-MeasureReport.supplementalData]",
)
errors = [i for i in issues if i.get("severity") in ("error", "fatal")]
actionable = []
for i in errors:
    text = i.get("diagnostics") or (i.get("details") or {}).get("text") or ""
    if any(k in text for k in KNOWN):
        print(f"KNOWN(IG/validator): {text}")
        continue
    actionable.append(i)
    loc = ",".join(i.get("location") or i.get("expression") or [])
    print(f"ERROR: {text} @ {loc}")
if actionable:
    sys.exit(1)
print("OK: no actionable profile errors (known IG supplementalData slice noise allowed)")
PY
fi

if [[ "$DO_DOCKER" -eq 1 ]]; then
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
fi
