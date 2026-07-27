#!/usr/bin/env bash
# CMS122 closed loop on fhirdev DFN 101096 (DENOM yes / NUMER no → file HbA1c >9 → CQL → SETPOP).
# Measure polarity: poor control — NUMER when most recent HbA1c > 9%.
# Usage: ./scripts/cms122-closed-loop-101096.sh [--skip-file] [--skip-cql] [--heuristic-only]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BASE="${FHIRDEV_HTTP_BASE:-https://devfhir.vistaplex.org}"
DFN=101096
A1C="${CMS122_A1C:-9.2}"
SKIP_FILE=0
SKIP_CQL=0
HEURISTIC_ONLY=0
for a in "$@"; do
  case "$a" in
    --skip-file) SKIP_FILE=1 ;;
    --skip-cql) SKIP_CQL=1 ;;
    --heuristic-only) HEURISTIC_ONLY=1; SKIP_CQL=1 ;;
  esac
done
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="logs/cms122-closed-loop-101096-${STAMP}.log"
mkdir -p logs 2026/cohorts/c0x-heuristic/closed-loop
exec > >(tee -a "$LOG") 2>&1
echo "=== CMS122 closed loop DFN=$DFN start $(date -Is) ==="
echo "BASE=$BASE A1C=$A1C"

section() { echo; echo "==== $* ===="; date -Is; }

section "0) Preflight: quality pick-list includes import-hba1c"
AI_JSON="2026/cohorts/c0x-heuristic/closed-loop/aiconsult-${DFN}-pre.json"
curl -sS "$BASE/aiconsult?dfn=$DFN&file=0&mode=quality&measure=CMS122v14" -o "$AI_JSON"
python3 - <<PY
import json
d=json.load(open("$AI_JSON"))
text=json.dumps(d)
assert "cms122-import-hba1c" in text, "missing cms122-import-hba1c — check cds1 Stage 2 pick-list"
print("OK: pick-list offers cms122-import-hba1c")
PY

if [[ "$SKIP_FILE" -eq 0 ]]; then
  section "1) Build quality update Bundle (accepted import-hba1c)"
  UPD_JSON="2026/cohorts/c0x-heuristic/closed-loop/update-review-${DFN}.json"
  curl -sS -X POST "$BASE/aiconsult/update-bundle?dfn=$DFN" \
    -H 'Content-Type: application/json' \
    -d "$(python3 - <<PY
import json
print(json.dumps({
  "dfn": $DFN,
  "measure": "CMS122v14",
  "acceptedActions": ["cms122-import-hba1c"],
  "actionValues": {
    "cms122-import-hba1c": {"value": $A1C, "unit": "%"}
  }
}))
PY
)" -o "$UPD_JSON" -w "update-bundle HTTP %{http_code}\n" || true

  if ! python3 -c "import json;d=json.load(open('$UPD_JSON')); assert d.get('resourceType')=='Bundle' or (d.get('updateBundle') or {}).get('resourceType')=='Bundle'" 2>/dev/null; then
    curl -sS -X POST "$BASE/aiconsult/update-review?dfn=$DFN" \
      -H 'Content-Type: application/json' \
      -d "$(python3 - <<PY
import json
print(json.dumps({
  "dfn": $DFN,
  "measure": "CMS122v14",
  "acceptedActions": ["cms122-import-hba1c"],
  "actionValues": {
    "cms122-import-hba1c": {"value": $A1C, "unit": "%"}
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
codes=set()
for o in obs:
  for c in (o.get("code") or {}).get("coding") or []:
    codes.add(c.get("code"))
print("Observation codes", sorted(codes))
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

  section "3) Read-back labs for HbA1c"
  sleep 2
  # Default /fhir omits many labs; domain=labs returns LABADD results (codes may be empty).
  curl -sS "$BASE/fhir?dfn=$DFN&domain=labs" -H 'Accept: application/fhir+json' \
    -o "2026/cohorts/c0x-heuristic/closed-loop/fhir-${DFN}-labs-post.json"
  python3 - <<PY
import json
A1C_CODES={"4548-4","17856-6","17855-8","4549-2"}
d=json.load(open("2026/cohorts/c0x-heuristic/closed-loop/fhir-${DFN}-labs-post.json"))
found=[]
for e in d.get("entry") or []:
  r=e.get("resource") or {}
  if r.get("resourceType")!="Observation": continue
  codes={str(c.get("code")) for c in (r.get("code") or {}).get("coding") or []}
  text=((r.get("code") or {}).get("text") or "").upper()
  v=(r.get("valueQuantity") or {}).get("value")
  looks_a1c=bool(codes & A1C_CODES) or "A1C" in text or "HEMOGLOBIN A1C" in text or r.get("id","").startswith("LCH-")
  if not looks_a1c and v is None: continue
  if looks_a1c or (v is not None and float(v)>9):
    found.append((r.get("id"), r.get("effectiveDateTime"), v, codes, text[:40]))
found.sort(key=lambda x: x[1] or "", reverse=True)
print("Lab Observations (newest first):", found[:8])
assert any(x[2] is not None and float(x[2])>9 for x in found), "no HbA1c >9 on /fhir?domain=labs read-back"
print("OK: HbA1c >9 present on /fhir?domain=labs")
PY
else
  echo "SKIP file (--skip-file)"
fi

section "3b) Heuristic POST /fhir-quality-recompute (UI closed-loop path)"
RECOMP="2026/cohorts/c0x-heuristic/closed-loop/recompute-${DFN}.json"
curl -sS -X POST "$BASE/fhir-quality-recompute?dfn=$DFN&measure=CMS122v14" \
  -H 'Content-Type: application/json' \
  -d "$(python3 - <<PY
import json
print(json.dumps({
  "dfn": $DFN,
  "acceptedActions": ["cms122-import-hba1c"],
  "actionValues": {"cms122-import-hba1c": {"value": $A1C, "unit": "%"}}
}))
PY
)" -o "$RECOMP" -w "recompute HTTP %{http_code}\n"
python3 - <<PY
import json
d=json.load(open("$RECOMP"))
print(json.dumps(d, indent=2)[:1500])
assert d.get("status") in ("ok","noop"), d
if d.get("status")=="ok":
  assert int(d.get("pop",{}).get("numer",0))==1, "heuristic NUMER expected 1 for A1c>9"
  print("OK: heuristic SETPOP NUMER=1 rate", d.get("sum",{}).get("rate"))
PY

if [[ "$SKIP_CQL" -eq 0 ]]; then
  section "4) Official CQL on Synthea source + injected HbA1c >9"
  SYN_SRC="$(ls 2026/patients/raw/synthea-1000-20260901-20260101/fhir/Alline927_*Baumbach*.json | head -1)"
  python3 - <<PY
import json
from pathlib import Path
src=Path("$SYN_SRC")
bundle=json.loads(src.read_text())
pid=next(e["resource"]["id"] for e in bundle["entry"] if e.get("resource",{}).get("resourceType")=="Patient")
obs={
  "resourceType":"Observation","id":"closed-loop-a1c-$DFN","status":"final",
  "category":[{"coding":[{"system":"http://terminology.hl7.org/CodeSystem/observation-category","code":"laboratory"}]}],
  "code":{"coding":[{"system":"http://loinc.org","code":"4548-4","display":"Hemoglobin A1c/Hemoglobin.total in Blood"}]},
  "subject":{"reference":f"Patient/{pid}"},"effectiveDateTime":"2026-07-27T12:00:00Z",
  "valueQuantity":{"value":$A1C,"unit":"%","system":"http://unitsofmeasure.org","code":"%"}
}
bundle["entry"].append({"fullUrl":f"urn:uuid:{obs['id']}","resource":obs})
out=Path("2026/cohorts/c0x-heuristic/closed-loop/alline-with-high-a1c.json")
out.write_text(json.dumps(bundle))
man=Path("2026/cohorts/c0x-heuristic/closed-loop/eval-manifest-${DFN}-synthea.tsv")
man.write_text(f"bundle_path\tdfn\n{out.resolve()}\t$DFN\n")
print("CQL input", out, "patient", pid)
PY
  MAN="2026/cohorts/c0x-heuristic/closed-loop/eval-manifest-${DFN}-synthea.tsv"
  node scripts/evaluate-cqm-manifest.js CMS122v14 --manifest "$MAN" | tee "2026/cohorts/c0x-heuristic/closed-loop/cql-${DFN}.log"
  python3 - <<PY
import json
from pathlib import Path
rows=Path("2026/cohorts/CMS122v14/c0x-cql/cql-results.tsv").read_text().splitlines()[1:]
row=[r for r in rows if r.startswith("$DFN\t")]
assert row, "no CQL row for $DFN"
parts=row[0].split("\t")
ipp,denom,numer,denex=map(int, parts[2:6])
print(f"CQL $DFN ipp={ipp} denom={denom} numer={numer} denex={denex}")
Path("2026/cohorts/c0x-heuristic/closed-loop/cql-${DFN}.json").write_text(
  json.dumps({"dfn":$DFN,"ipp":ipp,"denom":denom,"numer":numer,"denex":denex}, indent=2)+"\n")
assert numer==1 and denom==1 and ipp==1, "expected CQL 1/1/1 after HbA1c>9 inject"
print("OK: official CQL NUMER=1")
PY

  section "5) Patch SETPOP_MANIFEST + apply + SETSUM"
  python3 - <<'PY'
from pathlib import Path
import json
man=Path("2026/cohorts/SETPOP_MANIFEST.tsv")
cql=json.loads(Path("2026/cohorts/c0x-heuristic/closed-loop/cql-101096.json").read_text())
dfn=str(cql["dfn"])
lines=man.read_text().splitlines()
out=[]
for line in lines:
  if not line.startswith("CMS122v14\t"+dfn+"\t"):
    out.append(line); continue
  p=line.split("\t")
  p[2]=str(cql["ipp"]); p[3]=str(cql["denom"]); p[4]=str(cql["numer"]); p[5]=str(cql["denex"])
  p[6]=f"closed-loop A1c file cql={cql['ipp']}/{cql['denom']}/{cql['numer']}/{cql['denex']}"
  p[7]="official-cql"
  out.append("\t".join(p))
  print("patched", out[-1])
man.write_text("\n".join(out)+"\n")
ipp=denom=numer=denex=n=0
for line in out[1:]:
  if not line.startswith("CMS122v14\t"): continue
  p=line.split("\t"); n+=1
  ipp+=int(p[2]); denom+=int(p[3]); numer+=int(p[4]); denex+=int(p[5])
Path("2026/cohorts/c0x-heuristic/closed-loop/sum122.json").write_text(
  json.dumps({"n":n,"ipp":ipp,"denom":denom,"numer":numer,"denex":denex}, indent=2)+"\n")
print("CMS122 SUM", n, ipp, denom, numer, denex)
PY
  ./scripts/fhirdev-apply-setpop.sh
  python3 - <<'PY' > /tmp/setsum122.m
import json
from datetime import date
s=json.load(open("2026/cohorts/c0x-heuristic/closed-loop/sum122.json"))
print('ZL "C0FQUAL"')
print(f'D SETSUM^C0FQUAL("CMS122v14",{s["n"]},{s["ipp"]},{s["denom"]},{s["numer"]},{s["denex"]},"{date.today().isoformat()}","closed-loop 101096")')
print('W "SUM=",$G(^C0FQUAL("SUM","CMS122v14")),!')
print('W "POP096=",$G(^C0FQUAL("POP","CMS122v14",101096)),!')
print('H')
PY
  ssh -o BatchMode=yes root@devfhir.vistaplex.org \
    "docker exec -i -u vehu fhirdev22 bash -lc 'source /home/vehu/etc/env; cd /home/vehu/p; mumps -dir'" \
    </tmp/setsum122.m
else
  echo "SKIP cql (--skip-cql)"
fi

section "6) Dashboard smoke"
curl -sS "$BASE/fhir-quality-dashboards/CMS122v14" | python3 -c "
import sys,re
t=sys.stdin.read()
print('rate line', re.search(r'rate <strong>[^<]+', t))
print('101096 row', '101096' in t)
m=re.search(r'101096</td><td>[^<]*</td><td>([^<]*)</td><td>([^<]*)</td><td>([^<]*)</td>', t)
print('101096 flags', m.groups() if m else 'parse-fail')
"
echo "=== DONE log=$LOG ==="
