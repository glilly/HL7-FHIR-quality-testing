#!/usr/bin/env bash
# Focused recovery: CMS165 (restored VSAC) + CMS122 attempt → CQL → enrich → load → Inferno.
# Skips preclassifier (already on disk). Does not wipe expansions on empty VSAC.
set -uo pipefail
export PYTHONUNBUFFERED=1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="logs/recover-cms165-122-${STAMP}.log"
mkdir -p logs 2026/scorecards/inferno

exec > >(tee -a "$LOG") 2>&1
echo "=== RECOVER CMS165/122 START $(date -Is) ==="

section() { echo; echo "==== $* ===="; date -Is; }
ok() { echo "OK: $*"; }
fail() { echo "FAIL: $*"; }

if [[ "${SKIP_VSAC:-}" == "1" ]]; then
  unset VSAC_API_KEY UMLS_API_KEY
  ok "SKIP_VSAC=1 — using local expansions only"
elif [[ -x "$HOME/ops/scripts/load-vsac-api-key.sh" ]]; then
  # shellcheck disable=SC1090
  eval "$("$HOME/ops/scripts/load-vsac-api-key.sh")" || true
  if [[ -n "${VSAC_API_KEY:-}" ]]; then ok "VSAC_API_KEY loaded"; else fail "VSAC_API_KEY missing"; fi
fi

# Confirm CMS165 expansions present
if ! python3 - <<'PY'
import json, pathlib, sys
p = pathlib.Path('2026/measures/CMS165v14/cqm/value_sets.json')
vs = json.loads(p.read_text())
arr = vs if isinstance(vs, list) else vs.get('value_sets') or vs.get('valueSets') or []
exp = sum(1 for v in arr if isinstance(v, dict) and (v.get('concepts') or []))
print(f'CMS165 expansions: {exp}/{len(arr)}')
sys.exit(0 if exp > 0 else 1)
PY
then
  fail "CMS165 value_sets empty — restore value_sets.vsac-local.json first"
  exit 1
fi

section "1) Build CQM packages CMS165 + CMS122 (keep existing if VSAC empty)"
node scripts/build-cqm-package.js CMS165v14 CMS122v14 && ok cqm-build || fail cqm-build

section "2) Evaluate CQL"
for m in CMS165v14 CMS122v14; do
  echo "-- evaluate $m --"
  node scripts/evaluate-cqm.js "$m" --limit 18 && ok "eval $m" || fail "eval $m"
done

section "3) Enrich showcase/selected for Inferno"
python3 scripts/enrich-showcase-for-inferno.py && ok enrich || fail enrich

section "4) load=0 enriched bundles"
if [[ -f 2026/patients/enriched/overnight-enrich-manifest.tsv ]]; then
  python3 scripts/devfhir-bulk-ingest.py \
    2026/patients/enriched/overnight-enrich-manifest.tsv \
    --load 0 \
    --workers 4 \
    --out 2026/patients/devfhir-ingest-enriched-load0.tsv \
    --response-dir 2026/patients/ingest-responses-enriched-load0 \
    && ok enrich-load0 || fail enrich-load0
else
  fail "no enrich manifest"
fi

section "5) load=1 small manifest"
python3 - <<'PY'
import pathlib
root = pathlib.Path('.')
rows = ['bundle_path\n']
ing = root/'2026/patients/devfhir-ingest-enriched-load0.tsv'
if ing.exists():
    lines = ing.read_text().splitlines()
    hdr = lines[0].split('\t')
    for line in lines[1:]:
        parts = line.split('\t')
        row = {hdr[i]: (parts[i] if i < len(parts) else '') for i in range(len(hdr))}
        if row.get('http_code','').startswith('2') and row.get('bundle_path'):
            rows.append(row['bundle_path']+'\n')
out = root/'2026/patients/overnight-load1-manifest.tsv'
seen=set(); uniq=['bundle_path\n']
for r in rows[1:]:
    if r not in seen:
        seen.add(r); uniq.append(r)
    if len(uniq) > 25: break
out.write_text(''.join(uniq))
print(f'LOAD1_MANIFEST={out} count={len(uniq)-1}')
PY

if [[ -f 2026/patients/overnight-load1-manifest.tsv ]]; then
  python3 scripts/devfhir-bulk-ingest.py \
    2026/patients/overnight-load1-manifest.tsv \
    --load 1 \
    --workers 2 \
    --out 2026/patients/devfhir-ingest-overnight-load1.tsv \
    --response-dir 2026/patients/ingest-responses-overnight-load1 \
    && ok load1 || fail load1
fi

section "6) Hosted Inferno (showcase + CMS165 selected-18)"
run_inferno() {
  local url="$1" ids="$2" title="$3" out="$4"
  echo "Inferno $title ids=$ids"
  python3 scripts/inferno-run.py \
    --url "$url" \
    --patient-ids "$ids" \
    --title "$title" \
    --out "$out" \
    --timeout-seconds 2400 \
    && python3 scripts/summarize-inferno.py "$out" \
    && ok "$title" || fail "$title"
}

run_inferno https://devfhir.vistaplex.org/altfhir 482 \
  "recover-altfhir-ien482" \
  2026/scorecards/inferno/recover-altfhir-ien482.json

run_inferno https://devfhir.vistaplex.org/fhir 101090 \
  "recover-fhir-dfn101090" \
  2026/scorecards/inferno/recover-fhir-dfn101090.json

run_inferno https://devfhir.vistaplex.org/altfhir \
  "492,505,524,529,530,558,567,566,574,576,577,582,607,608,624,644,680,686" \
  "recover-altfhir-cms165-selected18" \
  2026/scorecards/inferno/recover-altfhir-cms165-selected18.json

section "7) Recovery report"
STAMP="$STAMP" LOG="$LOG" python3 - <<'PY'
import json, os, pathlib, datetime as dt
stamp = os.environ["STAMP"]
log = os.environ["LOG"]
root = pathlib.Path('.')
lines = [
    f"# Recovery CMS165/122 Report ({stamp})",
    "",
    f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}",
    "",
    "## CQM package build",
]
cqm = root/'2026/measures/OVERNIGHT_CQM_BUILD_SUMMARY.json'
if cqm.exists():
    lines += ['```json', cqm.read_text().strip(), '```']
else:
    lines.append('_missing_')
lines += ["", "## Inferno scorecards"]
for p in sorted((root/'2026/scorecards/inferno').glob('recover-*.json')):
    try:
        data = json.loads(p.read_text())
    except Exception as e:
        lines.append(f"- `{p.name}`: parse error {e}")
        continue
    results = data.get('results') or []
    items = results if isinstance(results, list) else results.get('results') or []
    if isinstance(items, dict):
        items = items.get('results') or []
    counts = {'pass': 0, 'fail': 0, 'skip': 0}
    for r in items if isinstance(items, list) else []:
        st = str(r.get('result') or r.get('status') or '').lower()
        if st in counts:
            counts[st] += 1
        elif 'pass' in st:
            counts['pass'] += 1
        elif 'fail' in st:
            counts['fail'] += 1
        elif 'skip' in st:
            counts['skip'] += 1
    url = data.get('session_url', '')
    lines.append(
        f"- `{p.name}`: pass={counts['pass']} fail={counts['fail']} skip={counts['skip']} [session]({url})"
    )
lines += ["", "## Log", f"`{log}`"]
out = root/f'docs/RECOVER_CMS165_122_REPORT_{stamp}.md'
out.write_text('\n'.join(lines) + '\n')
(root/'docs/RECOVER_CMS165_122_REPORT_LATEST.md').write_text(out.read_text())
print(f'REPORT={out}')
PY

echo "=== RECOVER CMS165/122 END $(date -Is) ==="
echo "LOG=$LOG"
echo "REPORT=docs/RECOVER_CMS165_122_REPORT_LATEST.md"
