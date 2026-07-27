#!/usr/bin/env bash
# CMS165 closed loop on fhirdev DFN 101115 (DENOM yes / NUMER no → file controlled BP → CQL → SETPOP).
# Usage: ./scripts/cms165-closed-loop-101115.sh [--skip-file] [--skip-cql]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BASE="${FHIRDEV_HTTP_BASE:-https://devfhir.vistaplex.org}"
DFN=101115
SBP="${CMS165_SBP:-128}"
DBP="${CMS165_DBP:-78}"
SKIP_FILE=0
SKIP_CQL=0
for a in "$@"; do
  case "$a" in
    --skip-file) SKIP_FILE=1 ;;
    --skip-cql) SKIP_CQL=1 ;;
  esac
done
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="logs/cms165-closed-loop-101115-${STAMP}.log"
mkdir -p logs 2026/cohorts/c0x-heuristic/closed-loop
exec > >(tee -a "$LOG") 2>&1
echo "=== CMS165 closed loop DFN=$DFN start $(date -Is) ==="
echo "BASE=$BASE SBP=$SBP DBP=$DBP"

section() { echo; echo "==== $* ===="; date -Is; }

section "0) Preflight: quality pick-list includes record-BP"
AI_JSON="2026/cohorts/c0x-heuristic/closed-loop/aiconsult-${DFN}-pre.json"
curl -sS "$BASE/aiconsult?dfn=$DFN&file=0&mode=quality&measure=CMS165v14" -o "$AI_JSON"
python3 - <<PY
import json,sys
d=json.load(open("$AI_JSON"))
text=json.dumps(d)
assert "cms165-record-blood-pressure" in text, "missing cms165-record-blood-pressure — deploy cds1 Stage 2 with QualityDiagnosticReportFactory fix"
print("OK: pick-list offers cms165-record-blood-pressure")
PY

if [[ "$SKIP_FILE" -eq 0 ]]; then
  section "1) Build quality update Bundle (accepted record-BP)"
  # Stage via aiconsult/update-review if available; else call cds1 /quality/update-bundle through Codex
  UPD_JSON="2026/cohorts/c0x-heuristic/closed-loop/update-review-${DFN}.json"
  # Prefer Codex gateway that wraps cds1
  curl -sS -X POST "$BASE/aiconsult/update-bundle?dfn=$DFN" \
    -H 'Content-Type: application/json' \
    -d "$(python3 - <<PY
import json
print(json.dumps({
  "dfn": $DFN,
  "measure": "CMS165v14",
  "acceptedActions": ["cms165-record-blood-pressure"],
  "actionValues": {
    "cms165-record-blood-pressure": {"systolic": $SBP, "diastolic": $DBP}
  }
}))
PY
)" -o "$UPD_JSON" -w "update-bundle HTTP %{http_code}\n" || true

  # Fallback shapes: try update-review
  if ! python3 -c "import json;d=json.load(open('$UPD_JSON')); assert d.get('resourceType')=='Bundle' or (d.get('updateBundle') or {}).get('resourceType')=='Bundle'" 2>/dev/null; then
    curl -sS -X POST "$BASE/aiconsult/update-review?dfn=$DFN" \
      -H 'Content-Type: application/json' \
      -d "$(python3 - <<PY
import json
print(json.dumps({
  "dfn": $DFN,
  "measure": "CMS165v14",
  "acceptedActions": ["cms165-record-blood-pressure"],
  "actionValues": {
    "cms165-record-blood-pressure": {"systolic": $SBP, "diastolic": $DBP}
  }
}))
PY
)" -o "$UPD_JSON" -w "update-review HTTP %{http_code}\n"
  fi

  python3 - <<PY
import json
from pathlib import Path
d=json.load(open("$UPD_JSON"))
bundle=d if d.get("resourceType")=="Bundle" else d.get("updateBundle") or d.get("fhirBundle") or d
assert bundle and bundle.get("resourceType")=="Bundle", d
Path("2026/cohorts/c0x-heuristic/closed-loop/update-bundle-${DFN}.json").write_text(json.dumps(bundle, indent=2)+"\n")
obs=[e.get("resource") for e in bundle.get("entry") or [] if (e.get("resource") or {}).get("resourceType")=="Observation"]
print(f"Bundle entries={len(bundle.get('entry') or [])} Observations={len(obs)}")
assert obs, "no Observation in update Bundle"
PY

  section "2) File via /updatepatient load=1"
  RESP="2026/cohorts/c0x-heuristic/closed-loop/updatepatient-${DFN}.json"
  curl -sS -X POST "$BASE/updatepatient?dfn=$DFN&load=1" \
    -H 'Content-Type: application/json' \
    --data-binary @"2026/cohorts/c0x-heuristic/closed-loop/update-bundle-${DFN}.json" \
    -o "$RESP" -w "updatepatient HTTP %{http_code}\n"
  python3 - <<PY
import json
d=json.load(open("$RESP"))
print("keys", sorted(d.keys())[:20] if isinstance(d,dict) else type(d))
print(json.dumps(d, indent=2)[:1200])
PY

  section "3) Read-back vitals for controlled BP"
  sleep 2
  curl -sS "$BASE/fhir?dfn=$DFN" -H 'Accept: application/fhir+json' \
    -o "2026/cohorts/c0x-heuristic/closed-loop/fhir-${DFN}-post.json"
  python3 - <<PY
import json
d=json.load(open("2026/cohorts/c0x-heuristic/closed-loop/fhir-${DFN}-post.json"))
found=[]
for e in d.get("entry") or []:
  r=e.get("resource") or {}
  if r.get("resourceType")!="Observation": continue
  codes={c.get("code") for c in (r.get("code") or {}).get("coding") or []}
  if "85354-9" not in codes and "8480-6" not in codes: continue
  s=d_=None
  for comp in r.get("component") or []:
    cc={c.get("code") for c in (comp.get("code") or {}).get("coding") or []}
    v=(comp.get("valueQuantity") or {}).get("value")
    if "8480-6" in cc: s=v
    if "8462-4" in cc: d_=v
  if s is not None and d_ is not None:
    found.append((r.get("id"), r.get("effectiveDateTime"), s, d_, s<140 and d_<90))
found.sort(key=lambda x: x[1] or "", reverse=True)
print("BP readings (newest first):", found[:5])
assert any(x[4] for x in found), "no controlled BP (<140/<90) on /fhir read-back"
print("OK: controlled BP present on /fhir")
PY
else
  echo "SKIP file (--skip-file)"
fi

if [[ "$SKIP_CQL" -eq 0 ]]; then
  section "4) Official CQL on Synthea source + injected controlled BP"
  # Codex /fhir exports are too thin for cqm-execution; inject filed BP into Synthea source.
  SYN_SRC="$(ls 2026/patients/raw/synthea-1000-20260901-20260101/fhir/Adolfo777_Conroy74_*.json | head -1)"
  python3 - <<PY
import json
from pathlib import Path
src=Path("$SYN_SRC")
bundle=json.loads(src.read_text())
pid=next(e["resource"]["id"] for e in bundle["entry"] if e.get("resource",{}).get("resourceType")=="Patient")
obs={
  "resourceType":"Observation","id":"closed-loop-bp-$DFN","status":"final",
  "category":[{"coding":[{"system":"http://terminology.hl7.org/CodeSystem/observation-category","code":"vital-signs"}]}],
  "code":{"coding":[{"system":"http://loinc.org","code":"85354-9","display":"Blood pressure panel"}]},
  "subject":{"reference":f"Patient/{pid}"},"effectiveDateTime":"2026-07-27T12:00:00Z",
  "component":[
    {"code":{"coding":[{"system":"http://loinc.org","code":"8480-6"}]},
     "valueQuantity":{"value":$SBP,"unit":"mm[Hg]","system":"http://unitsofmeasure.org","code":"mm[Hg]"}},
    {"code":{"coding":[{"system":"http://loinc.org","code":"8462-4"}]},
     "valueQuantity":{"value":$DBP,"unit":"mm[Hg]","system":"http://unitsofmeasure.org","code":"mm[Hg]"}}
  ]
}
bundle["entry"].append({"fullUrl":f"urn:uuid:{obs['id']}","resource":obs})
out=Path("2026/cohorts/c0x-heuristic/closed-loop/adolfo-with-controlled-bp.json")
out.write_text(json.dumps(bundle))
man=Path("2026/cohorts/c0x-heuristic/closed-loop/eval-manifest-${DFN}-synthea.tsv")
man.write_text(f"bundle_path\tdfn\n{out.resolve()}\t$DFN\n")
print("CQL input", out, "patient", pid)
PY
  MAN="2026/cohorts/c0x-heuristic/closed-loop/eval-manifest-${DFN}-synthea.tsv"
  node scripts/evaluate-cqm-manifest.js CMS165v14 --manifest "$MAN" | tee "2026/cohorts/c0x-heuristic/closed-loop/cql-${DFN}.log"
  python3 - <<PY
import json
from pathlib import Path
rows=Path("2026/cohorts/CMS165v14/c0x-cql/cql-results.tsv").read_text().splitlines()[1:]
row=[r for r in rows if r.startswith("$DFN\t")]
assert row, "no CQL row for $DFN"
parts=row[0].split("\t")
ipp,denom,numer,denex=map(int, parts[2:6])
print(f"CQL $DFN ipp={ipp} denom={denom} numer={numer} denex={denex}")
Path("2026/cohorts/c0x-heuristic/closed-loop/cql-${DFN}.json").write_text(
  json.dumps({"dfn":$DFN,"ipp":ipp,"denom":denom,"numer":numer,"denex":denex}, indent=2)+"\n")
assert numer==1 and denom==1 and ipp==1, "expected CQL 1/1/1 after controlled BP inject"
print("OK: official CQL NUMER=1")
PY

  section "5) Patch SETPOP_MANIFEST + apply + SETSUM"
  python3 - <<'PY'
from pathlib import Path
import json
man=Path("2026/cohorts/SETPOP_MANIFEST.tsv")
cql=json.loads(Path("2026/cohorts/c0x-heuristic/closed-loop/cql-101115.json").read_text())
dfn=str(cql["dfn"])
lines=man.read_text().splitlines()
out=[]
for line in lines:
  if not line.startswith("CMS165v14\t"+dfn+"\t"):
    out.append(line); continue
  p=line.split("\t")
  p[2]=str(cql["ipp"]); p[3]=str(cql["denom"]); p[4]=str(cql["numer"]); p[5]=str(cql["denex"])
  p[6]=f"closed-loop BP file cql={cql['ipp']}/{cql['denom']}/{cql['numer']}/{cql['denex']}"
  p[7]="official-cql"
  out.append("\t".join(p))
  print("patched", out[-1])
man.write_text("\n".join(out)+"\n")
# recompute CMS165 SUM from all POP rows for that measure
ipp=denom=numer=denex=n=0
for line in out[1:]:
  if not line.startswith("CMS165v14\t"): continue
  p=line.split("\t"); n+=1
  ipp+=int(p[2]); denom+=int(p[3]); numer+=int(p[4]); denex+=int(p[5])
Path("2026/cohorts/c0x-heuristic/closed-loop/sum165.json").write_text(
  json.dumps({"n":n,"ipp":ipp,"denom":denom,"numer":numer,"denex":denex}, indent=2)+"\n")
print("CMS165 SUM", n, ipp, denom, numer, denex)
PY
  ./scripts/fhirdev-apply-setpop.sh
  # bump SUM to match recomputed POP
  python3 - <<'PY' > /tmp/setsum165.m
import json
from datetime import date
s=json.load(open("2026/cohorts/c0x-heuristic/closed-loop/sum165.json"))
print('ZL "C0FQUAL"')
print(f'D SETSUM^C0FQUAL("CMS165v14",{s["n"]},{s["ipp"]},{s["denom"]},{s["numer"]},{s["denex"]},"{date.today().isoformat()}","closed-loop 101115")')
print('W "SUM=",$G(^C0FQUAL("SUM","CMS165v14")),!')
print('W "POP115=",$G(^C0FQUAL("POP","CMS165v14",101115)),!')
print('H')
PY
  ssh -o BatchMode=yes root@devfhir.vistaplex.org \
    "docker exec -i -u vehu fhirdev22 bash -lc 'source /home/vehu/etc/env; cd /home/vehu/p; mumps -dir'" \
    </tmp/setsum165.m
else
  echo "SKIP cql (--skip-cql)"
fi

section "6) Dashboard smoke"
curl -sS "$BASE/fhir-quality-dashboards/CMS165v14" | python3 -c "
import sys,re
t=sys.stdin.read()
print('rate line', re.search(r'rate <strong>[^<]+', t))
print('101115 row', '101115' in t)
m=re.search(r'101115</td><td>[^<]*</td><td>([^<]*)</td><td>([^<]*)</td><td>([^<]*)</td>', t)
print('101115 flags', m.groups() if m else 'parse-fail')
"
echo "=== DONE log=$LOG ==="
