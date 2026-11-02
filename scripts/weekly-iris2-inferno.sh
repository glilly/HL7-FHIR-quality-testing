#!/usr/bin/env bash
# Weekly US Quality Core run against the iris2 golden cohort.
#
# Hosted Inferno only (it cannot score localhost). The PIDS default is the
# ZZ + gap charts loaded last by the 2026-11-02 rebuild (Vista-on-FHIR
# docs/iris2/IRIS2_REBUILD_PLAN_2026-11-02.md). A skip does not fail this
# job; a fail or error row does.
#
# Evidence:
#   2026/scorecards/inferno/weekly/YYYY-MM-DD-iris2.json
#   2026/scorecards/inferno/weekly/YYYY-MM-DD-iris2.md
#
# The Sunday night lane runs this. Daytime:
#   ./scripts/weekly-iris2-inferno.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DAY="${IRIS2_INFERNO_DAY:-$(date -u +%F)}"
OUT_DIR="$ROOT/2026/scorecards/inferno/weekly"
OUT="$OUT_DIR/${DAY}-iris2.json"
URL="${IRIS2_FHIR_BASE:-https://iris2.vistaplex.org/fhir}"
if [[ -n "${IRIS2_INFERNO_PATIENTS:-}" ]]; then
  PIDS="$IRIS2_INFERNO_PATIENTS"
else
  PIDS="190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223"
fi

mkdir -p "$OUT_DIR"
python3 "$ROOT/scripts/inferno-run.py" \
  --url "$URL" \
  --patient-ids "$PIDS" \
  --title "weekly iris2 ZZ cohort ${DAY}" \
  --poll-seconds 20 \
  --timeout-seconds 5400 \
  --out "$OUT"
python3 "$ROOT/scripts/summarize-inferno.py" "$OUT"
python3 - "$OUT" <<'PY'
import json, sys
from collections import Counter
data = json.load(open(sys.argv[1]))
results = data.get("results") or []
counts = Counter(r.get("result") or "unknown" for r in results)
print(
    "iris2-inferno "
    f"pass={counts['pass']} fail={counts['fail']} "
    f"error={counts['error']} skip={counts['skip']} n={len(results)} "
    f"session={data.get('session_url','')}"
)
if counts["fail"] or counts["error"] or len(results) < 498:
    sys.exit(1)
PY
