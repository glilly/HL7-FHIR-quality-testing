#!/usr/bin/env bash
# Nightly US Core 6.1.0 against Show only.
#
# Show (DFNs 101258–101291) is the host whose full us_core_v610 suite is
# green. iris2's charts are 190–223 and do not carry these examples, so
# this loop does not rotate. A fail, an error, a skip, or a short result
# list fails the night: a red result means a regression on this host.
#
# Evidence:
#   2026/scorecards/inferno/nightly-us-core/YYYY-MM-DD-showfhir.json
#   2026/scorecards/inferno/nightly-us-core/YYYY-MM-DD-showfhir.md
#
#   ./scripts/nightly-us-core-show.sh
#   US_CORE_NIGHTLY_DRY=1 ./scripts/nightly-us-core-show.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DAY="${US_CORE_NIGHTLY_DAY:-$(date -u +%F)}"
OUT_DIR="${US_CORE_EVIDENCE_DIR:-$ROOT/2026/scorecards/inferno/nightly-us-core}"
URL="https://showfhir.vistaplex.org/fhir"
PIDS=""
for ((i=101258; i<=101291; i++)); do PIDS+="${PIDS:+,}$i"; done

if [[ "${US_CORE_NIGHTLY_DRY:-0}" == "1" ]]; then
  echo "us-core-show dry url=$URL patients=$(echo "$PIDS" | awk -F, '{print NF}') day=$DAY"
  exit 0
fi

mkdir -p "$OUT_DIR"
OUT="$OUT_DIR/${DAY}-showfhir.json"
python3 "$ROOT/scripts/inferno-run.py" \
  --url "$URL" \
  --patient-ids "$PIDS" \
  --title "nightly showfhir US Core 6.1.0 ${DAY}" \
  --suite us_core_v610-us_core_v610_fhir_api \
  --test-suite-id us_core_v610 \
  --poll-seconds 20 \
  --timeout-seconds 5400 \
  --out "$OUT"
python3 "$ROOT/scripts/summarize-inferno.py" "$OUT"
python3 - "$OUT" "$ROOT" "$OUT_DIR" <<'PY'
import json, sys
from collections import Counter
from pathlib import Path
out, root, out_dir = sys.argv[1:4]
data = json.load(open(out))
results = data.get("results") or []
counts = Counter(r.get("result") or "unknown" for r in results)

def test_ids(path):
    body = json.load(open(path))
    return {r.get("test_id") for r in (body.get("results") or []) if r.get("test_id")}

current = test_ids(out)
priors = sorted(p for p in Path(out_dir).glob("*.json") if p.resolve() != Path(out).resolve())
prior = priors[-1] if priors else None
if prior is None:
    baseline = Path(root) / "2026/scorecards/inferno/2026-11-10-showfhir-us-core-v610-step7.json"
    if baseline.is_file():
        prior = baseline
added, removed = set(), set()
compared = "no prior scorecard"
if prior is not None:
    previous = test_ids(prior)
    added = current - previous
    removed = previous - current
    compared = prior.name
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
    "us-core-show "
    f"pass={counts['pass']} fail={counts['fail']} "
    f"error={counts['error']} skip={counts['skip']} n={len(results)} "
    f"session={data.get('session_url','')}"
)
# 505 rows was the green Show suite on 2026-11-10. Fewer means the run
# stopped early. A new hosted test still passes when its result is pass.
if counts["fail"] or counts["error"] or counts["skip"] or len(results) < 500:
    sys.exit(1)
PY
