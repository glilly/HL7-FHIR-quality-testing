#!/usr/bin/env bash
# Nightly US Quality Core run, one public host per UTC day.
#
# Hosted Inferno cannot reach localhost. The rotation is the public hosts
# that currently serve the ZZ cohort, so a new fail or skip is a change in
# the hosted suite or in that cohort, not a missing chart:
#   showfhir  DFNs 101258–101291
#   iris2     DFNs 190–223
# fhirdev, wvehr, and rpmsfhir are public and are not in this list: they
# do not have these charts. Add a host here only after it does.
#
# A fail, an error, or a skip fails the night. A change in the suite's
# test ids is recorded and does not, by itself, fail the night.
#
# Evidence:
#   2026/scorecards/inferno/nightly/YYYY-MM-DD-<host>.json
#   2026/scorecards/inferno/nightly/YYYY-MM-DD-<host>.md
#
#   ./scripts/nightly-inferno-rotate.sh
#   INFERNO_ROTATE_HOST=iris2 ./scripts/nightly-inferno-rotate.sh
#   INFERNO_ROTATE_DRY=1 ./scripts/nightly-inferno-rotate.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DAY="${INFERNO_ROTATE_DAY:-$(date -u +%F)}"
OUT_DIR="${INFERNO_EVIDENCE_DIR:-$ROOT/2026/scorecards/inferno/nightly}"
ORDER=(showfhir iris2)

host_url() {
  case "$1" in
    showfhir) echo "https://showfhir.vistaplex.org/fhir" ;;
    iris2) echo "https://iris2.vistaplex.org/fhir" ;;
    *) return 1 ;;
  esac
}

host_pids() {
  local i out=""
  case "$1" in
    showfhir)
      for ((i=101258; i<=101291; i++)); do out+="${out:+,}$i"; done ;;
    iris2)
      for ((i=190; i<=223; i++)); do out+="${out:+,}$i"; done ;;
    *) return 1 ;;
  esac
  echo "$out"
}

pick_host() {
  local forced="${INFERNO_ROTATE_HOST:-}"
  if [[ -n "$forced" ]]; then
    echo "$forced"
    return 0
  fi
  local doy idx
  doy=$(date -u +%j)
  doy=$((10#$doy))
  idx=$((doy % ${#ORDER[@]}))
  echo "${ORDER[$idx]}"
}

HOST="$(pick_host)"
URL="$(host_url "$HOST")" || { echo "inferno-rotate: unknown host $HOST" >&2; exit 2; }
PIDS="$(host_pids "$HOST")"
if [[ "${INFERNO_ROTATE_DRY:-0}" == "1" ]]; then
  echo "inferno-rotate dry host=$HOST url=$URL patients=$(echo "$PIDS" | awk -F, '{print NF}')"
  exit 0
fi

mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/${DAY}-${HOST}.json"
python3 "$ROOT/scripts/inferno-run.py" \
  --url "$URL" \
  --patient-ids "$PIDS" \
  --title "nightly ${HOST} ZZ cohort ${DAY}" \
  --poll-seconds 20 \
  --timeout-seconds 5400 \
  --out "$OUT"
python3 "$ROOT/scripts/summarize-inferno.py" "$OUT"
python3 - "$OUT" "$ROOT" "$OUT_DIR" "$HOST" <<'PY'
import json, sys
from collections import Counter
from pathlib import Path
out, root, out_dir, host = sys.argv[1:5]
data = json.load(open(out))
results = data.get("results") or []
counts = Counter(r.get("result") or "unknown" for r in results)

def test_ids(path):
    body = json.load(open(path))
    return {r.get("test_id") for r in (body.get("results") or []) if r.get("test_id")}

current = test_ids(out)
prior = None
priors = sorted(p for p in Path(out_dir).glob("*.json") if p.resolve() != Path(out).resolve())
if priors:
    prior = priors[-1]
else:
    baseline = Path(root) / "2026/scorecards/inferno/2026-11-09-showfhir.json"
    if baseline.is_file():
        prior = baseline
added, removed = set(), set()
compared = "no prior scorecard"
if prior is not None:
    previous = test_ids(prior)
    added = current - previous
    removed = previous - current
    compared = prior.name
if not added and not removed and prior is not None:
    suite = "same"
else:
    suite = f"+{len(added)}/-{len(removed)}"
md = Path(out).with_suffix(".md")
lines = ["", "## Suite delta", "", f"Compared with `{compared}`.", ""]
if prior is None:
    lines.append("- No earlier scorecard to compare.")
elif not added and not removed:
    lines.append(f"- No change in test ids ({len(current)}).")
else:
    lines.append(f"- Added {len(added)}, removed {len(removed)}.")
    for label, ids in (("added", sorted(added)), ("removed", sorted(removed))):
        for tid in ids:
            lines.append(f"- {label}: `{tid}`")
lines.append("")
md.write_text(md.read_text() + "\n".join(lines))
print(
    "inferno-rotate "
    f"host={host} pass={counts['pass']} fail={counts['fail']} "
    f"error={counts['error']} skip={counts['skip']} n={len(results)} "
    f"suite={suite} session={data.get('session_url','')}"
)
if counts["fail"] or counts["error"] or counts["skip"] or len(results) < 498:
    sys.exit(1)
PY
