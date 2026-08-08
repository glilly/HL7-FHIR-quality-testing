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
