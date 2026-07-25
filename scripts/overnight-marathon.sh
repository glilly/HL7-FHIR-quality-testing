#!/usr/bin/env bash
# Non-interactive September measure×Inferno overnight marathon.
# Logs to logs/overnight-marathon-<stamp>.log
set -uo pipefail
export PYTHONUNBUFFERED=1
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="logs/overnight-marathon-${STAMP}.log"
REPORT="docs/OVERNIGHT_MARATHON_REPORT_${STAMP}.md"
mkdir -p logs 2026/scorecards/inferno

exec > >(tee -a "$LOG") 2>&1
echo "=== OVERNIGHT MARATHON START $(date -Is) ==="
echo "ROOT=$ROOT LOG=$LOG"

section() { echo; echo "==== $* ===="; date -Is; }

ok() { echo "OK: $*"; }
fail() { echo "FAIL: $*"; }

# Load VSAC if available (non-interactive)
if [[ -x "$HOME/ops/scripts/load-vsac-api-key.sh" ]]; then
  # shellcheck disable=SC1090
  eval "$("$HOME/ops/scripts/load-vsac-api-key.sh")" || true
  if [[ -n "${VSAC_API_KEY:-}" ]]; then ok "VSAC_API_KEY loaded"; else fail "VSAC_API_KEY missing"; fi
else
  fail "VSAC loader not found"
fi

section "1) Multi-measure FHIR preclassifier"
python3 scripts/multi-measure-fhir-preclassifier.py \
  --manifest 2026/patients/devfhir-ingest-load0-success-1000.tsv \
  && ok preclassifier || fail preclassifier

section "2) Build CQM packages with VSAC (all shortlist)"
node scripts/build-cqm-package.js --all && ok cqm-build || fail cqm-build

section "3) Evaluate CQL for priority measures (selected-18 / available)"
for m in CMS165v14 CMS122v14 CMS138v14 CMS2v15 CMS130v14 CMS125v14 CMS131v14 CMS68v15 CMS22v14; do
  echo "-- evaluate $m --"
  node scripts/evaluate-cqm.js "$m" --limit 18 && ok "eval $m" || fail "eval $m"
done

section "4) Enrich showcase/selected bundles for Inferno families"
python3 scripts/enrich-showcase-for-inferno.py && ok enrich || fail enrich

section "5) load=0 enriched bundles to graph (altfhir IENs)"
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

section "6) load=1 showcase patients (one per priority measure when IEN known)"
# Build a small load1 manifest from showcase-1.tsv graph IENs that already exist on graph,
# plus newly enriched load0 successes.
python3 - <<'PY'
import pathlib, csv
root = pathlib.Path('.')
rows = ['bundle_path\n']
# Prefer enriched bundles that were just ingested (load0 out has paths)
ing = root/'2026/patients/devfhir-ingest-enriched-load0.tsv'
if ing.exists():
    lines = ing.read_text().splitlines()
    hdr = lines[0].split('\t')
    for line in lines[1:]:
        parts = line.split('\t')
        row = {hdr[i]: (parts[i] if i < len(parts) else '') for i in range(len(hdr))}
        if row.get('http_code','').startswith('2') and row.get('bundle_path'):
            rows.append(row['bundle_path']+'\n')
# Also include original CMS165 selected-18 if we want re-score only — skip re-load
out = root/'2026/patients/overnight-load1-manifest.tsv'
# Deduplicate, keep first 24 to bound VistA write load
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
else
  fail "no load1 manifest"
fi

section "7) Hosted Inferno scorecards"
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

# Showcase regressions
run_inferno https://devfhir.vistaplex.org/altfhir 482 \
  "overnight-altfhir-ien482" \
  2026/scorecards/inferno/overnight-altfhir-ien482.json

run_inferno https://devfhir.vistaplex.org/fhir 101090 \
  "overnight-fhir-dfn101090" \
  2026/scorecards/inferno/overnight-fhir-dfn101090.json

# CMS165 selected-18
run_inferno https://devfhir.vistaplex.org/altfhir \
  "492,505,524,529,530,558,567,566,574,576,577,582,607,608,624,644,680,686" \
  "overnight-altfhir-cms165-selected18" \
  2026/scorecards/inferno/overnight-altfhir-cms165-selected18.json

run_inferno https://devfhir.vistaplex.org/fhir \
  "101094,101095,101096,101097,101098,101099,101100,101101,101102,101103,101104,101105,101106,101107,101108,101109,101110,101111" \
  "overnight-fhir-cms165-selected18" \
  2026/scorecards/inferno/overnight-fhir-cms165-selected18.json

# Multi-patient session from overnight load1 DFNs + known showcases
python3 - <<'PY'
import pathlib
ing = pathlib.Path('2026/patients/devfhir-ingest-overnight-load1.tsv')
dfns=[]
iens=[]
if ing.exists():
    lines=ing.read_text().splitlines()
    hdr=lines[0].split('\t')
    for line in lines[1:]:
        parts=line.split('\t')
        row={hdr[i]: (parts[i] if i < len(parts) else '') for i in range(len(hdr))}
        if row.get('http_code','').startswith('2'):
            if row.get('dfn'): dfns.append(row['dfn'])
            if row.get('ien'): iens.append(row['ien'])
# Always include known strong patients
for d in ['101090','101094']:
    if d not in dfns: dfns.insert(0,d)
for i in ['482','492']:
    if i not in iens: iens.insert(0,i)
pathlib.Path('2026/scorecards/inferno/overnight-multi-dfns.txt').write_text(','.join(dfns[:12]))
pathlib.Path('2026/scorecards/inferno/overnight-multi-iens.txt').write_text(','.join(iens[:12]))
print('MULTI_DFNS', ','.join(dfns[:12]))
print('MULTI_IENS', ','.join(iens[:12]))
PY

MULTI_DFNS="$(cat 2026/scorecards/inferno/overnight-multi-dfns.txt 2>/dev/null || echo 101090)"
MULTI_IENS="$(cat 2026/scorecards/inferno/overnight-multi-iens.txt 2>/dev/null || echo 482)"

run_inferno https://devfhir.vistaplex.org/fhir "$MULTI_DFNS" \
  "overnight-fhir-multi-showcase" \
  2026/scorecards/inferno/overnight-fhir-multi-showcase.json

run_inferno https://devfhir.vistaplex.org/altfhir "$MULTI_IENS" \
  "overnight-altfhir-multi-showcase" \
  2026/scorecards/inferno/overnight-altfhir-multi-showcase.json

section "8) Write morning report"
# Quoted heredoc so bash does not expand JSON braces in embedded summaries.
STAMP="$STAMP" python3 - <<'PY'
import json, os, pathlib, datetime as dt
stamp = os.environ["STAMP"]
root = pathlib.Path('.')
lines = []
lines.append(f"# Overnight Marathon Report ({stamp})")
lines.append("")
lines.append(f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}")
lines.append("")
lines.append("## Goal")
lines.append("Advance the September measure×Inferno plan: preclassify all first-wave measures, build CQM packages, enrich showcase patients, load to devfhir, run hosted Inferno.")
lines.append("")
lines.append("## Preclassifier rollup")
pre = root/'2026/cohorts/OVERNIGHT_PRECLASSIFIER_SUMMARY.json'
if pre.exists():
    lines.append('```json')
    lines.append(pre.read_text().strip())
    lines.append('```')
else:
    lines.append("_missing_")
lines.append("")
lines.append("## CQM package build")
cqm = root/'2026/measures/OVERNIGHT_CQM_BUILD_SUMMARY.json'
if cqm.exists():
    lines.append('```json')
    lines.append(cqm.read_text().strip())
    lines.append('```')
else:
    lines.append("_missing_")
lines.append("")
lines.append("## Inferno scorecards")
sc_dir = root/'2026/scorecards/inferno'
for p in sorted(sc_dir.glob('overnight-*.json')):
    try:
        data=json.loads(p.read_text())
    except Exception as e:
        lines.append(f"- `{p.name}`: parse error {e}")
        continue
    results=data.get('results') or []
    # results may be list or dict
    counts={'pass':0,'fail':0,'skip':0,'error':0}
    items = results if isinstance(results, list) else results.get('results') or []
    if isinstance(items, dict):
        items = items.get('results') or []
    for r in items if isinstance(items, list) else []:
        st=str(r.get('result') or r.get('status') or '').lower()
        if st in counts: counts[st]+=1
        elif 'pass' in st: counts['pass']+=1
        elif 'fail' in st: counts['fail']+=1
        elif 'skip' in st: counts['skip']+=1
    url=data.get('session_url','')
    lines.append(f"- `{p.name}`: pass={counts['pass']} fail={counts['fail']} skip={counts['skip']} [session]({url})")
lines.append("")
lines.append("## Load manifests")
for p in [
    '2026/patients/devfhir-ingest-enriched-load0.tsv',
    '2026/patients/devfhir-ingest-overnight-load1.tsv',
]:
    path=root/p
    if path.exists():
        n=max(0, len(path.read_text().splitlines())-1)
        lines.append(f"- `{p}`: {n} rows")
lines.append("")
lines.append("## Log")
lines.append(f"`logs/overnight-marathon-{stamp}.log`")
lines.append("")
lines.append("## Morning checklist")
lines.append("1. Review preclassifier numer counts — pick final showcase DFN/IEN per measure.")
lines.append("2. Inspect CQL batch JSON for measures with expanded value sets.")
lines.append("3. Compare Inferno multi-showcase skip families vs CMS165-only baseline.")
lines.append("4. Activate winning measures in C0FQUAL / Quality AI Consult.")
lines.append("5. Commit scorecards + reports (value_sets.json stays gitignored).")
out = root/f'docs/OVERNIGHT_MARATHON_REPORT_{stamp}.md'
out.write_text('\n'.join(lines)+'\n')
# also stable latest pointer
(root/'docs/OVERNIGHT_MARATHON_REPORT_LATEST.md').write_text(out.read_text())
print(f'REPORT={out}')
PY

section "9) Commit and push overnight artifacts (no VSAC expansions)"
git add \
  scripts/multi-measure-fhir-preclassifier.py \
  scripts/build-cqm-package.js \
  scripts/evaluate-cqm.js \
  scripts/enrich-showcase-for-inferno.py \
  scripts/overnight-marathon.sh \
  docs/OVERNIGHT_MARATHON_REPORT_LATEST.md \
  docs/OVERNIGHT_MARATHON_REPORT_*.md \
  docs/SEPTEMBER_MEASURE_INFERNO_ELEMENT_MAPPING.md \
  2026/cohorts/*/denom/fhir-preclassifier.tsv \
  2026/cohorts/*/numer/fhir-preclassifier.tsv \
  2026/cohorts/*/numer/showcase-1.tsv \
  2026/cohorts/*/numer/selected-18.tsv \
  2026/cohorts/*/reports/*.json \
  2026/cohorts/OVERNIGHT_PRECLASSIFIER_SUMMARY.json \
  2026/measures/OVERNIGHT_CQM_BUILD_SUMMARY.json \
  2026/scorecards/inferno/overnight-*.json \
  2026/scorecards/inferno/overnight-*.md \
  2026/patients/devfhir-ingest-enriched-load0.tsv \
  2026/patients/devfhir-ingest-overnight-load1.tsv \
  2026/patients/overnight-load1-manifest.tsv \
  2026/patients/enriched/overnight-enrich-manifest.tsv \
  package.json \
  2>/dev/null || true
# Never add value_sets.json
if git diff --cached --quiet; then
  echo "Nothing to commit"
else
  git commit -m "$(cat <<'EOF'
Overnight marathon: multi-measure cohorts, CQM builds, Inferno scorecards.

Non-interactive September portfolio progress: preclassify first-wave measures, expand packages, enrich/load showcases, and capture hosted Inferno results.
EOF
)" || true
  git push origin HEAD || fail "git push"
fi

section "DONE"
echo "=== OVERNIGHT MARATHON END $(date -Is) ==="
echo "LOG=$LOG"
echo "REPORT=docs/OVERNIGHT_MARATHON_REPORT_LATEST.md"
