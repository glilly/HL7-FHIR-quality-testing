#!/usr/bin/env bash
# Publish 2026/research/out/ (ResearchStudy/ResearchSubject/matches.json)
# to devfhir /filesystem/research/ — same lane as measurereports.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/2026/research/out"
FHIRDEV_SSH="${FHIRDEV_SSH:-root@devfhir.vistaplex.org}"
FHIRDEV_CONTAINER="${FHIRDEV_CONTAINER:-fhirdev22}"
REMOTE_WWW="${FHIRDEV_WWW:-/home/vehu/www/filesystem}"
HTTP_BASE="${FHIRDEV_HTTP_BASE:-https://devfhir.vistaplex.org}"
DEST_REL="research"

[[ -f "$SRC/matches.json" ]] || { echo "missing $SRC/matches.json — run scripts/trial-matching.py first" >&2; exit 1; }

TGZ="$(mktemp /tmp/research.XXXXXX.tgz)"
cleanup() { rm -f "$TGZ"; }
trap cleanup EXIT
tar -C "$SRC" -czf "$TGZ" .

echo "==> Publish to ${FHIRDEV_CONTAINER}:${REMOTE_WWW}/${DEST_REL}"
scp -o BatchMode=yes "$TGZ" "${FHIRDEV_SSH}:/tmp/research.tgz"
ssh -o BatchMode=yes "$FHIRDEV_SSH" bash -s <<EOF
set -euo pipefail
docker cp /tmp/research.tgz '${FHIRDEV_CONTAINER}:/home/vehu/research.tgz'
rm -f /tmp/research.tgz
docker exec '${FHIRDEV_CONTAINER}' bash -lc '
set -euo pipefail
DEST="${REMOTE_WWW}/${DEST_REL}"
mkdir -p "\$DEST"
find "\$DEST" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
tar -C "\$DEST" -xzf /home/vehu/research.tgz
rm -f /home/vehu/research.tgz
chown -R vehu:vehu "\$DEST" 2>/dev/null || true
'
EOF

echo "==> Smoke: ${HTTP_BASE}/filesystem/${DEST_REL}/matches.json"
curl -sS --max-time 30 "${HTTP_BASE}/filesystem/${DEST_REL}/matches.json" | head -c 200
echo
echo "Published."
