#!/usr/bin/env bash
# Recovery without VSAC network: keep CMS165 local expansions, skip empty overwrite,
# then CQL → enrich → load → Inferno.
set -uo pipefail
export PYTHONUNBUFFERED=1
unset VSAC_API_KEY UMLS_API_KEY
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="logs/recover-cms165-122-${STAMP}.log"
mkdir -p logs 2026/scorecards/inferno docs

exec > >(tee -a "$LOG") 2>&1
echo "=== RECOVER (no-VSAC) START $(date -Is) LOG=$LOG ==="

node scripts/build-cqm-package.js CMS165v14 CMS122v14

python3 - <<'PY'
import json, pathlib, sys
p = pathlib.Path("2026/measures/CMS165v14/cqm/value_sets.json")
vs = json.loads(p.read_text())
arr = vs if isinstance(vs, list) else vs.get("value_sets") or vs.get("valueSets") or []
exp = sum(1 for v in arr if isinstance(v, dict) and (v.get("concepts") or []))
print(f"CMS165 kept {exp}/{len(arr)}")
sys.exit(0 if exp > 0 else 1)
PY

echo "-- evaluate CMS165 --"
node scripts/evaluate-cqm.js CMS165v14 --limit 18
echo "-- evaluate CMS122 --"
node scripts/evaluate-cqm.js CMS122v14 --limit 18 || echo "CMS122 eval failed (expected without VSAC)"

python3 scripts/enrich-showcase-for-inferno.py || echo "enrich failed"

if [[ -f 2026/patients/enriched/overnight-enrich-manifest.tsv ]]; then
  python3 scripts/devfhir-bulk-ingest.py \
    2026/patients/enriched/overnight-enrich-manifest.tsv \
    --load 0 --workers 4 \
    --out 2026/patients/devfhir-ingest-enriched-load0.tsv \
    --response-dir 2026/patients/ingest-responses-enriched-load0 \
    || echo "load0 failed"

  python3 - <<'PY'
import pathlib
root = pathlib.Path(".")
ing = root / "2026/patients/devfhir-ingest-enriched-load0.tsv"
rows = ["bundle_path\n"]
if ing.exists():
    lines = ing.read_text().splitlines()
    hdr = lines[0].split("\t")
    for line in lines[1:]:
        parts = line.split("\t")
        row = {hdr[i]: (parts[i] if i < len(parts) else "") for i in range(len(hdr))}
        if row.get("http_code", "").startswith("2") and row.get("bundle_path"):
            rows.append(row["bundle_path"] + "\n")
seen = set()
uniq = ["bundle_path\n"]
for r in rows[1:]:
    if r not in seen:
        seen.add(r)
        uniq.append(r)
    if len(uniq) > 25:
        break
(root / "2026/patients/overnight-load1-manifest.tsv").write_text("".join(uniq))
print("LOAD1", len(uniq) - 1)
PY

  python3 scripts/devfhir-bulk-ingest.py \
    2026/patients/overnight-load1-manifest.tsv \
    --load 1 --workers 2 \
    --out 2026/patients/devfhir-ingest-overnight-load1.tsv \
    --response-dir 2026/patients/ingest-responses-overnight-load1 \
    || echo "load1 failed"
fi

run_inf() {
  echo "Inferno $3"
  python3 scripts/inferno-run.py \
    --url "$1" --patient-ids "$2" --title "$3" --out "$4" --timeout-seconds 2400 \
    && python3 scripts/summarize-inferno.py "$4" \
    || echo "FAIL $3"
}

run_inf https://devfhir.vistaplex.org/altfhir 482 \
  recover-altfhir-ien482 \
  2026/scorecards/inferno/recover-altfhir-ien482.json

run_inf https://devfhir.vistaplex.org/fhir 101090 \
  recover-fhir-dfn101090 \
  2026/scorecards/inferno/recover-fhir-dfn101090.json

run_inf https://devfhir.vistaplex.org/altfhir \
  "492,505,524,529,530,558,567,566,574,576,577,582,607,608,624,644,680,686" \
  recover-altfhir-cms165-selected18 \
  2026/scorecards/inferno/recover-altfhir-cms165-selected18.json

STAMP="$STAMP" LOG="$LOG" python3 - <<'PY'
import json, os, pathlib, datetime as dt

stamp = os.environ["STAMP"]
log = os.environ["LOG"]
root = pathlib.Path(".")
lines = [
    f"# Recovery CMS165/122 Report ({stamp})",
    "",
    f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}",
    "",
    "## Note",
    "VSAC DNS unavailable; CMS165 kept local expansions. CMS122 still 0 expansions.",
    "",
    "## CQM",
]
cqm = root / "2026/measures/OVERNIGHT_CQM_BUILD_SUMMARY.json"
lines += ["```json", cqm.read_text().strip() if cqm.exists() else "{}", "```", "", "## Inferno"]
for p in sorted((root / "2026/scorecards/inferno").glob("recover-*.json")):
    try:
        data = json.loads(p.read_text())
    except Exception as e:
        lines.append(f"- `{p.name}`: {e}")
        continue
    results = data.get("results") or []
    items = results if isinstance(results, list) else results.get("results") or []
    if isinstance(items, dict):
        items = items.get("results") or []
    c = {"pass": 0, "fail": 0, "skip": 0}
    for r in items if isinstance(items, list) else []:
        st = str(r.get("result") or r.get("status") or "").lower()
        if st in c:
            c[st] += 1
        elif "pass" in st:
            c["pass"] += 1
        elif "fail" in st:
            c["fail"] += 1
        elif "skip" in st:
            c["skip"] += 1
    lines.append(
        f"- `{p.name}`: pass={c['pass']} fail={c['fail']} skip={c['skip']} [session]({data.get('session_url', '')})"
    )
lines += ["", "## Log", f"`{log}`"]
out = root / f"docs/RECOVER_CMS165_122_REPORT_{stamp}.md"
out.write_text("\n".join(lines) + "\n")
(root / "docs/RECOVER_CMS165_122_REPORT_LATEST.md").write_text(out.read_text())
print("REPORT", out)
PY

echo "=== RECOVER END $(date -Is) ==="
echo "LOG=$LOG"
echo "REPORT=docs/RECOVER_CMS165_122_REPORT_LATEST.md"
