#!/usr/bin/env bash
# Publish 2026/cohorts/measurereports/ to fhirdev /filesystem/quality/measurereports/
# Optional: rebuild from SETPOP first (--build).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/2026/cohorts/measurereports"
FHIRDEV_SSH="${FHIRDEV_SSH:-root@devfhir.vistaplex.org}"
FHIRDEV_CONTAINER="${FHIRDEV_CONTAINER:-fhirdev22}"
REMOTE_WWW="${FHIRDEV_WWW:-/home/vehu/www/filesystem}"
HTTP_BASE="${FHIRDEV_HTTP_BASE:-https://devfhir.vistaplex.org}"
DEST_REL="quality/measurereports"

if [[ "${1:-}" == "--build" ]]; then
  # Official-cql DEQM freezes (copied into summary-deqm.json when present)
  python3 "${ROOT}/scripts/build-deqm-summary-batch.py" --check || true
  python3 "${ROOT}/scripts/build-measurereports-from-setpop.py"
fi

[[ -f "$SRC/index.json" ]] || { echo "missing $SRC/index.json — run with --build first" >&2; exit 1; }

# Include the RPMS-lane DEQM Summary MeasureReports (distinct reporter Org).
RPMS_SRC="${ROOT}/docs/deqm-summary/prototypes/rpms"
if [[ -d "$RPMS_SRC" ]]; then
  rm -rf "$SRC/rpms"
  mkdir -p "$SRC/rpms"
  cp "$RPMS_SRC"/*.json "$SRC/rpms/"
  python3 - "$SRC/rpms" <<'PY'
import json, pathlib, sys
from datetime import datetime, timezone
d = pathlib.Path(sys.argv[1])
reports = sorted(p.name for p in d.glob("*-rpms-summary-deqm.json"))
index = {
    "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "lane": "rpms",
    "note": "DEQM Summary MeasureReports from rpmsfhir round-trip official CQL (synthetic data); reporter Organization/vistaplex-rpms-demo",
    "reports": reports,
}
(d / "index.json").write_text(json.dumps(index, indent=2) + "\n")
print(f"rpms lane: {len(reports)} reports indexed")
PY
fi

# Include the fhirprod-lane DEQM Summary MeasureReports (fhir.vistaplex.org reporter Org).
FHIRPROD_SRC="${ROOT}/docs/deqm-summary/prototypes/fhirprod"
if [[ -d "$FHIRPROD_SRC" ]]; then
  rm -rf "$SRC/fhirprod"
  mkdir -p "$SRC/fhirprod"
  cp "$FHIRPROD_SRC"/*.json "$SRC/fhirprod/"
  python3 - "$SRC/fhirprod" <<'PY'
import json, pathlib, sys
from datetime import datetime, timezone
d = pathlib.Path(sys.argv[1])
reports = sorted(p.name for p in d.glob("*-fhirprod-summary-deqm.json"))
index = {
    "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "lane": "fhirprod",
    "note": "DEQM Summary MeasureReports from fhir.vistaplex.org round-trip official CQL (synthetic data); reporter Organization/vistaplex-prod-demo",
    "reports": reports,
}
(d / "index.json").write_text(json.dumps(index, indent=2) + "\n")
print(f"fhirprod lane: {len(reports)} reports indexed")
PY
fi

TGZ="$(mktemp /tmp/measurereports.XXXXXX.tgz)"
cleanup() { rm -f "$TGZ"; }
trap cleanup EXIT
tar -C "$SRC" -czf "$TGZ" .

echo "==> Publish to ${FHIRDEV_CONTAINER}:${REMOTE_WWW}/${DEST_REL}"
scp -o BatchMode=yes "$TGZ" "${FHIRDEV_SSH}:/tmp/measurereports.tgz"
ssh -o BatchMode=yes "$FHIRDEV_SSH" bash -s <<EOF
set -euo pipefail
docker cp /tmp/measurereports.tgz '${FHIRDEV_CONTAINER}:/home/vehu/measurereports.tgz'
rm -f /tmp/measurereports.tgz
docker exec '${FHIRDEV_CONTAINER}' bash -lc '
set -euo pipefail
DEST="${REMOTE_WWW}/${DEST_REL}"
mkdir -p "\$DEST"
find "\$DEST" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
tar -C "\$DEST" -xzf /home/vehu/measurereports.tgz
rm -f /home/vehu/measurereports.tgz
chown -R vehu:vehu "\$DEST"
echo "files=\$(find "\$DEST" -type f | wc -l)"
'
EOF

echo "==> Smoke"
for path in \
  "/filesystem/${DEST_REL}/index.json" \
  "/filesystem/${DEST_REL}/CMS165v14/summary.json" \
  "/filesystem/${DEST_REL}/CMS165v14/summary-deqm.json" \
  "/filesystem/${DEST_REL}/CMS165v14/Patient-101094.json"
do
  code=$(curl -sS -o /tmp/mr-smoke.json -w '%{http_code}' "${HTTP_BASE}${path}" || true)
  echo "HTTP ${code} ${path}"
done
python3 -c "import json; d=json.load(open('/tmp/mr-smoke.json')); print('last', d.get('resourceType'), d.get('id'), (d.get('meta') or {}).get('profile'))"
echo "Done. ${HTTP_BASE}/filesystem/${DEST_REL}/index.json"
