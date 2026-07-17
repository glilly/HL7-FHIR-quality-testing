#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-https://devfhir.vistaplex.org}"
LOAD="${LOAD:-0}"
MANIFEST="${1:-}"
OUT="${OUT:-2026/patients/devfhir-ingest.tsv}"

if [[ -z "$MANIFEST" || ! -f "$MANIFEST" ]]; then
  echo "Usage: $0 MANIFEST.tsv" >&2
  exit 2
fi
mkdir -p "$(dirname "$OUT")"
printf 'bundle_path\thttp_code\tien\tdfn\tresponse_file\n' > "$OUT"

i=0
while IFS=$'\t' read -r bundle patient_id name birthDate gender; do
  if [[ "$bundle" == "bundle_path" ]]; then
    continue
  fi
  i=$((i+1))
  response="$(dirname "$OUT")/ingest-response-${i}.json"
  code=$(curl -sS -o "$response" -w '%{http_code}' -H 'Expect:' -H 'Content-Type: application/json' --data-binary "@$bundle" "$BASE_URL/addpatient?load=$LOAD")
  ien=$(python3 - "$response" <<'PY2'
import json, sys
try:
    d=json.load(open(sys.argv[1]))
except Exception:
    print('')
    raise SystemExit
for key in ('ien','IEN'):
    if key in d:
        print(d[key]); break
else:
    print('')
PY2
)
  dfn=$(python3 - "$response" <<'PY2'
import json, sys
try:
    d=json.load(open(sys.argv[1]))
except Exception:
    print('')
    raise SystemExit
for key in ('dfn','DFN'):
    if key in d:
        print(d[key]); break
else:
    print('')
PY2
)
  printf '%s\t%s\t%s\t%s\t%s\n' "$bundle" "$code" "$ien" "$dfn" "$response" >> "$OUT"
  echo "[$i] HTTP $code ien=$ien dfn=$dfn $bundle"
done < "$MANIFEST"

echo "INGEST_MANIFEST=$OUT"
