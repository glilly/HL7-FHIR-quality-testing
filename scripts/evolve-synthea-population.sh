#!/usr/bin/env bash
# Evolve a Synthea Java population snapshot forward and re-export FHIR.
# Requires a snap from generate-synthea-1000.sh (-u population.snap), not FHIR JSON.
# Docs: https://github.com/synthetichealth/synthea/wiki/Evolving-a-Population
set -euo pipefail

SNAP_IN="${1:-}"
if [[ -z "$SNAP_IN" || ! -f "$SNAP_IN" ]]; then
  echo "usage: $0 <initial-population.snap> [days]" >&2
  echo "  days: optional -t N; omit to evolve to current system time" >&2
  exit 1
fi
DAYS="${2:-}"

SYN_SYNTHEA_ROOT="${SYN_SYNTHEA_ROOT:-/home/glilly/work/vista-stack/synthea}"
OUT_ROOT="${OUT_ROOT:-/home/glilly/work/vista-stack/HL7-FHIR-quality-testing/2026/patients/raw}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_ID="${RUN_ID:-synthea-evolve-${STAMP}}"
OUT_DIR="${OUT_DIR:-$OUT_ROOT/$RUN_ID}"
DOCKER_IMAGE="${SYNTHEA_JDK_IMAGE:-eclipse-temurin:17-jdk}"
GRADLE_CACHE="${GRADLE_CACHE:-/home/glilly/work/vista-stack/synthea-gradle-cache-user}"
PROJECT_CACHE="${PROJECT_CACHE:-/home/glilly/work/vista-stack/synthea-gradle-project-cache-user}"
BUILD_DIR="${BUILD_DIR:-/home/glilly/work/vista-stack/synthea-build-user}"
SNAP_OUT="${SNAP_OUT:-$OUT_DIR/population.snap}"
MANIFEST="$OUT_DIR/manifest.tsv"

if [[ ! -f "$SYN_SYNTHEA_ROOT/run_synthea" ]]; then
  echo "error: missing $SYN_SYNTHEA_ROOT/run_synthea" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
mkdir -p "$GRADLE_CACHE" "$PROJECT_CACHE" "$BUILD_DIR"
SNAP_IN_ABS="$(cd "$(dirname "$SNAP_IN")" && pwd)/$(basename "$SNAP_IN")"

PARAMS="[\"-i\",\"/snap-in\",\"-u\",\"/out/population.snap\",\"--exporter.fhir.export=true\",\"--exporter.fhir.transaction_bundle=true\",\"--exporter.baseDirectory=/out\""
if [[ -n "$DAYS" ]]; then
  PARAMS="${PARAMS},\"-t\",\"${DAYS}\""
fi
PARAMS="${PARAMS}]"

echo "Synthea evolve: in=$SNAP_IN_ABS days=${DAYS:-now} out=$OUT_DIR snap=$SNAP_OUT"

docker run --rm \
  -u "$(id -u):$(id -g)" \
  -e GRADLE_USER_HOME=/gradle-cache \
  -v "$SYN_SYNTHEA_ROOT:/work" \
  -v "$OUT_DIR:/out" \
  -v "$SNAP_IN_ABS:/snap-in:ro" \
  -v "$GRADLE_CACHE:/gradle-cache" \
  -v "$PROJECT_CACHE:/project-cache" \
  -v "$BUILD_DIR:/work/build" \
  -w /work \
  "$DOCKER_IMAGE" \
  sh -lc "./gradlew --project-cache-dir /project-cache run -Params='${PARAMS}'"

python3 - "$OUT_DIR" "$MANIFEST" <<'PY2'
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
manifest = Path(sys.argv[2])
fhir = out / 'fhir'
rows = [('bundle_path','patient_id','patient_name','birthDate','gender')]
for path in sorted(fhir.glob('*.json')):
    if path.name.startswith(('hospitalInformation', 'practitionerInformation')):
        continue
    data = json.loads(path.read_text())
    patient = None
    for entry in data.get('entry', []):
        res = entry.get('resource', {})
        if res.get('resourceType') == 'Patient':
            patient = res
            break
    if not patient:
        continue
    name = patient.get('name', [{}])[0]
    display = ' '.join(name.get('given', []) + ([name.get('family')] if name.get('family') else []))
    rows.append((str(path), patient.get('id',''), display, patient.get('birthDate',''), patient.get('gender','')))
manifest.write_text('\n'.join('\t'.join(str(c) for c in row) for row in rows) + '\n')
print(f"BUNDLES={len(rows)-1}")
print(f"MANIFEST={manifest}")
snap = out / 'population.snap'
print(f"SNAP={snap if snap.is_file() else 'MISSING'}")
PY2
