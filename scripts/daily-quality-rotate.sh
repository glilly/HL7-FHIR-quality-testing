#!/usr/bin/env bash
# Daily rotating quality lane — the showfhir sequence (C0X POPIDX → SPARQL IPP →
# measure SUM → /fhir JSON parse), one host per day across the active fleet.
#
# Evidence (committed when the night/day lane chooses):
#   2026/scorecards/daily-quality/YYYY-MM-DD-<host>.md
#   2026/scorecards/daily-quality/YYYY-MM-DD-<host>.json
#   2026/scorecards/daily-quality/LATEST.md  (copy of today's report)
#
# Usage:
#   ./scripts/daily-quality-rotate.sh              # today's host by day-of-year
#   ./scripts/daily-quality-rotate.sh showfhir     # force host
#   QUALITY_ROTATE_HOST=vehu10 ./scripts/daily-quality-rotate.sh
#   QUALITY_REEVAL=1 ./scripts/daily-quality-rotate.sh   # also POST reeval
#   QUALITY_REEVAL=auto  (default) — reeval on showfhir/vehu10/rpms-candidate only
#   QUALITY_REEVAL=0     — never reeval (read stored SUM only)
#
# Exit 0 only when every gated check passes.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${QUALITY_EVIDENCE_DIR:-$ROOT/2026/scorecards/daily-quality}"
MEASURES=(CMS165v14 CMS122v14 CMS130v14 CMS125v14 CMS138v14 CMS2v15)
# Rotation order (day-of-year % N). Local Docker hosts need the container up.
HOSTS=(showfhir fhirdev vehu10 rpms-candidate rpmsfhir wvehr)
REEVAL_DEFAULT_OK=(showfhir vehu10 rpms-candidate)

DAY="$(date -u +%Y-%m-%d)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$OUT_DIR" /tmp/daily-quality-rotate
WORKDIR="$(mktemp -d /tmp/daily-quality-rotate/run.XXXXXX)"
trap 'rm -rf "$WORKDIR"' EXIT

host_base() {
  case "$1" in
    showfhir|sofi) echo "https://showfhir.vistaplex.org" ;;
    fhirdev) echo "https://devfhir.vistaplex.org" ;;
    vehu10) echo "http://127.0.0.1:9085" ;;
    rpms-candidate|rpms-rebuild-candidate|rpms) echo "http://127.0.0.1:9088" ;;
    rpmsfhir|rpms-fhir) echo "https://rpmsfhir.vistaplex.org" ;;
    wvehr|fhirprod|fhir) echo "https://fhir.vistaplex.org" ;;
    *) return 1 ;;
  esac
}

pick_host() {
  local forced="${1:-${QUALITY_ROTATE_HOST:-}}"
  if [[ -n "$forced" ]]; then
    echo "$forced"
    return 0
  fi
  local doy idx
  doy=$(date -u +%j)
  doy=$((10#$doy))
  idx=$((doy % ${#HOSTS[@]}))
  echo "${HOSTS[$idx]}"
}

want_reeval() {
  local h="$1" mode="${QUALITY_REEVAL:-auto}"
  case "$mode" in
    0|no|false|off) return 1 ;;
    1|yes|true|on) return 0 ;;
    auto)
      local x
      for x in "${REEVAL_DEFAULT_OK[@]}"; do
        [[ "$x" == "$h" ]] && return 0
      done
      return 1
      ;;
    *)
      echo "unknown QUALITY_REEVAL=$mode (use auto|0|1)" >&2
      return 1
      ;;
  esac
}

HOST="$(pick_host "${1:-}")"
BASE="$(host_base "$HOST")" || { echo "unknown host: $HOST" >&2; exit 2; }
BASE="${BASE%/}"
EV_MD="$OUT_DIR/${DAY}-${HOST}.md"
EV_JSON="$OUT_DIR/${DAY}-${HOST}.json"
CHECKS_JSON="$WORKDIR/checks.json"
RAW_DIR="$WORKDIR/raw"
mkdir -p "$RAW_DIR"

echo "==> daily-quality-rotate host=$HOST base=$BASE day=$DAY stamp=$STAMP"
echo "    evidence → $EV_MD"

fail=0
pass() { echo "  PASS  $1"; }
bad()  { echo "  FAIL  $1" >&2; fail=1; }

# Accumulate machine-check rows as JSON lines for the report writer.
: >"$WORKDIR/rows.jsonl"
row() {
  # row status key detail [extra-json-object]
  python3 - "$WORKDIR/rows.jsonl" "$1" "$2" "$3" "${4:-{}}" <<'PY'
import json, sys
path, status, key, detail, extra = sys.argv[1:6]
obj = {"status": status, "key": key, "detail": detail}
try:
    obj.update(json.loads(extra))
except Exception:
    pass
with open(path, "a", encoding="utf-8") as f:
    f.write(json.dumps(obj, ensure_ascii=False) + "\n")
PY
}

http_get() {
  # http_get outpath url [max-time]
  local out="$1" url="$2" t="${3:-60}"
  local code
  code=$(curl -sS -o "$out" -w "%{http_code}" --max-time "$t" "$url" || echo 000)
  echo "$code"
}

# --- 1) FHIR metadata -------------------------------------------------------
code=$(http_get "$RAW_DIR/metadata.json" "$BASE/fhir/metadata" 30)
if [[ "$code" == "200" ]]; then
  pass "fhir/metadata"
  row pass fhir-metadata "HTTP 200"
else
  bad "fhir/metadata HTTP $code"
  row fail fhir-metadata "HTTP $code"
fi

# --- 2) C0X POPIDX ----------------------------------------------------------
code=$(http_get "$RAW_DIR/index-stat.json" "$BASE/c0x/index/stat" 30)
POP=0
CODES=0
if [[ "$code" == "200" ]]; then
  read -r POP CODES < <(python3 - "$RAW_DIR/index-stat.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
print(int(d.get("populationIndexed") or 0), int(d.get("popidxDistinctCodes") or 0))
PY
)
  if [[ "$POP" -ge 1 && "$CODES" -ge 1 ]]; then
    pass "c0x/index/stat pop=$POP codes=$CODES"
    row pass popidx "populationIndexed=$POP popidxDistinctCodes=$CODES" \
      "{\"populationIndexed\":$POP,\"popidxDistinctCodes\":$CODES}"
  else
    bad "c0x/index/stat pop=$POP codes=$CODES"
    row fail popidx "populationIndexed=$POP popidxDistinctCodes=$CODES" \
      "{\"populationIndexed\":$POP,\"popidxDistinctCodes\":$CODES}"
  fi
else
  bad "c0x/index/stat HTTP $code"
  row fail popidx "HTTP $code"
fi

code=$(http_get "$RAW_DIR/presets.json" "$BASE/c0x/presets" 45)
if [[ "$code" == "200" ]] && python3 - "$RAW_DIR/presets.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
ps = d.get("presets") or {}
items = []
if isinstance(ps, dict):
    for k, v in ps.items():
        if str(k).isdigit() and int(k) > 0 and isinstance(v, dict):
            items.append(v)
elif isinstance(ps, list):
    items = [x for x in ps if isinstance(x, dict)]
ids = {p.get("id") for p in items if p.get("id")}
need = {"CMS165v14", "CMS122v14", "CMS130v14", "CMS125v14", "CMS138v14", "CMS2v15"}
missing = sorted(need - ids)
sys.exit(1 if missing else 0)
PY
then
  pass "c0x/presets (6 active measures)"
  row pass c0x-presets "6 active measure presets present"
else
  bad "c0x/presets missing active measures or HTTP $code"
  row fail c0x-presets "HTTP $code or missing presets"
fi

# --- 3) SPARQL IPP (heuristic cohort) for each measure ----------------------
declare -A IPP_COUNTS=()
SAMPLE_DFNS=()
for m in "${MEASURES[@]}"; do
  code=$(http_get "$RAW_DIR/cohort-$m.json" "$BASE/c0x/cohort?measure=$m" 90)
  if [[ "$code" != "200" ]]; then
    bad "c0x/cohort $m HTTP $code"
    row fail "ipp-$m" "HTTP $code"
    IPP_COUNTS[$m]=-1
    continue
  fi
  ipp=$(python3 - "$RAW_DIR/cohort-$m.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
print(int(d.get("ippCount") or 0))
PY
)
  IPP_COUNTS[$m]=$ipp
  if [[ "$ipp" -ge 0 ]]; then
    pass "c0x/cohort $m ippCount=$ipp"
    row pass "ipp-$m" "ippCount=$ipp" "{\"ippCount\":$ipp}"
  else
    bad "c0x/cohort $m bad body"
    row fail "ipp-$m" "unreadable ippCount"
  fi
  # Collect a few DFNs for JSON encode check (first measure with patients).
  if [[ ${#SAMPLE_DFNS[@]} -lt 3 ]]; then
    mapfile -t more < <(python3 - "$RAW_DIR/cohort-$m.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
pts = d.get("patients") or {}
out = []
if isinstance(pts, dict):
    for k, v in pts.items():
        if not str(k).isdigit() or int(k) < 1:
            continue
        if isinstance(v, dict) and v.get("dfn"):
            out.append(str(v["dfn"]))
        if len(out) >= 5:
            break
print("\n".join(out))
PY
)
    for dfn in "${more[@]:-}"; do
      [[ -n "$dfn" ]] || continue
      SAMPLE_DFNS+=("$dfn")
      [[ ${#SAMPLE_DFNS[@]} -ge 3 ]] && break
    done
  fi
done

# --- 4) Measure SUM from dashboards (stored aggregates) ---------------------
declare -A SUM_IPP=() SUM_DENOM=() SUM_NUMER=() SUM_DENEX=()
for m in "${MEASURES[@]}"; do
  code=$(http_get "$RAW_DIR/dash-$m.html" "$BASE/fhir-quality-dashboards/$m" 60)
  if [[ "$code" != "200" ]]; then
    bad "dashboard $m HTTP $code"
    row fail "sum-$m" "dashboard HTTP $code"
    continue
  fi
  read -r ipp denom numer denex < <(python3 - "$RAW_DIR/dash-$m.html" <<'PY'
import re, sys
h = open(sys.argv[1], encoding="utf-8", errors="replace").read()
nums = dict(re.findall(r"(IPP|DENOM|NUMER|DENEX)\s*<strong>(\d+)</strong>", h))
print(
    nums.get("IPP", "-1"),
    nums.get("DENOM", "-1"),
    nums.get("NUMER", "-1"),
    nums.get("DENEX", "-1"),
)
PY
)
  SUM_IPP[$m]=$ipp
  SUM_DENOM[$m]=$denom
  SUM_NUMER[$m]=$numer
  SUM_DENEX[$m]=$denex
  if [[ "$ipp" == "-1" || "$denom" == "-1" ]]; then
    bad "dashboard $m missing IPP/DENOM"
    row fail "sum-$m" "missing IPP/DENOM in HTML"
    continue
  fi
  ok=1
  if [[ "$denom" -gt "$ipp" ]]; then ok=0; fi
  if [[ "$numer" != "-1" && "$numer" -gt "$denom" ]]; then ok=0; fi
  if [[ "$denex" != "-1" && "$denex" -gt "$denom" ]]; then ok=0; fi
  detail="$ipp/$denom/$numer/$denex"
  if [[ "$ok" == "1" ]]; then
    pass "SUM $m $detail"
    row pass "sum-$m" "$detail" \
      "{\"ipp\":$ipp,\"denom\":$denom,\"numer\":$numer,\"denex\":$denex}"
  else
    bad "SUM $m nesting broken $detail"
    row fail "sum-$m" "nesting $detail" \
      "{\"ipp\":$ipp,\"denom\":$denom,\"numer\":$numer,\"denex\":$denex}"
  fi
done

# --- 5) Optional CQL reeval (cds1) ------------------------------------------
REEVAL_RAN=0
if want_reeval "$HOST"; then
  REEVAL_RAN=1
  echo "  … QUALITY_REEVAL: posting fhir-quality-reeval for ${#MEASURES[@]} measures"
  for m in "${MEASURES[@]}"; do
    code=$(curl -sS -o "$RAW_DIR/reeval-$m.json" -w "%{http_code}" --max-time 60 \
      -X POST -H 'Content-Type: application/json' -d '{}' \
      "$BASE/fhir-quality-reeval?measure=$m" || echo 000)
    if [[ "$code" != "200" ]]; then
      bad "reeval accept $m HTTP $code"
      row fail "reeval-$m" "accept HTTP $code"
      continue
    fi
    # Poll dashboard status / re-read SUM after background work (up to ~6 min).
    done_ok=0
    for _ in $(seq 1 40); do
      sleep 9
      st=$(curl -sS --max-time 30 "$BASE/fhir-quality-dashboards/$m" 2>/dev/null \
        | grep -oE 'id="reevalStatus"[^>]*>[^<]+' | head -1 | sed 's/.*>//' || true)
      case "$st" in
        done*|Done*) done_ok=1; break ;;
        error*|Error*) break ;;
      esac
      # Also treat nested SUM present after accept as progress if status blank.
      [[ -z "$st" ]] && continue
      case "$st" in
        running*|starting*) continue ;;
      esac
    done
    code=$(http_get "$RAW_DIR/dash-after-$m.html" "$BASE/fhir-quality-dashboards/$m" 60)
    read -r ipp denom numer denex < <(python3 - "$RAW_DIR/dash-after-$m.html" <<'PY'
import re, sys
h = open(sys.argv[1], encoding="utf-8", errors="replace").read()
nums = dict(re.findall(r"(IPP|DENOM|NUMER|DENEX)\s*<strong>(\d+)</strong>", h))
print(
    nums.get("IPP", "-1"),
    nums.get("DENOM", "-1"),
    nums.get("NUMER", "-1"),
    nums.get("DENEX", "-1"),
)
PY
)
    SUM_IPP[$m]=$ipp
    SUM_DENOM[$m]=$denom
    SUM_NUMER[$m]=$numer
    SUM_DENEX[$m]=$denex
    detail="$ipp/$denom/$numer/$denex status=${st:-unknown}"
    if [[ "$done_ok" == "1" || ( "$ipp" != "-1" && "$denom" != "-1" ) ]]; then
      pass "REEVAL $m $detail"
      row pass "reeval-$m" "$detail" \
        "{\"ipp\":$ipp,\"denom\":$denom,\"numer\":$numer,\"denex\":$denex}"
    else
      bad "REEVAL $m $detail"
      row fail "reeval-$m" "$detail"
    fi
  done
else
  echo "  … QUALITY_REEVAL skipped for $HOST (set QUALITY_REEVAL=1 to force)"
  row pass reeval-skipped "QUALITY_REEVAL not requested for $HOST"
fi

# --- 6) /fhir?dfn= JSON integrity (encode-tail regression) ------------------
JSON_OK=0
JSON_FAIL=0
if [[ ${#SAMPLE_DFNS[@]} -eq 0 ]]; then
  bad "json-parse: no sample DFNs from cohort"
  row fail json-parse "no sample DFNs"
else
  for dfn in "${SAMPLE_DFNS[@]}"; do
    code=$(http_get "$RAW_DIR/fhir-$dfn.json" "$BASE/fhir?dfn=$dfn" 120)
    if [[ "$code" != "200" ]]; then
      bad "fhir?dfn=$dfn HTTP $code"
      row fail "json-$dfn" "HTTP $code"
      JSON_FAIL=$((JSON_FAIL + 1))
      continue
    fi
    if python3 - "$RAW_DIR/fhir-$dfn.json" <<'PY'
import json, sys
raw = open(sys.argv[1], "rb").read()
# Strict: one JSON value, no trailing junk (the showfhir encode-tail bug).
decoder = json.JSONDecoder()
obj, idx = decoder.raw_decode(raw.decode("utf-8", "replace").lstrip())
tail = raw.decode("utf-8", "replace").lstrip()[idx:].strip()
if tail:
    print(f"trailing junk len={len(tail)}", file=sys.stderr)
    raise SystemExit(1)
if not isinstance(obj, dict) or obj.get("resourceType") != "Bundle":
    print(f"not a Bundle: {type(obj)} {getattr(obj,'get',lambda*_:None)('resourceType')}", file=sys.stderr)
    raise SystemExit(1)
PY
    then
      pass "fhir?dfn=$dfn JSON Bundle OK"
      row pass "json-$dfn" "strict Bundle parse OK"
      JSON_OK=$((JSON_OK + 1))
    else
      bad "fhir?dfn=$dfn Invalid JSON / trailing junk"
      row fail "json-$dfn" "Extra data or non-Bundle"
      JSON_FAIL=$((JSON_FAIL + 1))
    fi
  done
fi

# --- Write evidence ---------------------------------------------------------
python3 - "$EV_MD" "$EV_JSON" "$OUT_DIR/LATEST.md" \
  "$HOST" "$BASE" "$DAY" "$STAMP" "$POP" "$CODES" "$REEVAL_RAN" "$fail" \
  "$WORKDIR/rows.jsonl" <<'PY'
import json, sys, pathlib
from collections import OrderedDict

(
    ev_md, ev_json, latest_md, host, base, day, stamp, pop, codes, reeval_ran, fail, rows_path
) = sys.argv[1:13]

rows = []
for line in open(rows_path, encoding="utf-8"):
    line = line.strip()
    if line:
        rows.append(json.loads(line))

measures = {}
for r in rows:
    k = r.get("key") or ""
    for prefix in ("ipp-", "sum-", "reeval-"):
        if k.startswith(prefix):
            mid = k[len(prefix) :]
            measures.setdefault(mid, {})
            if prefix == "ipp-":
                measures[mid]["ippCount"] = r.get("ippCount", r.get("detail"))
            if prefix in ("sum-", "reeval-") and "ipp" in r:
                measures[mid].update(
                    {
                        "ipp": r.get("ipp"),
                        "denom": r.get("denom"),
                        "numer": r.get("numer"),
                        "denex": r.get("denex"),
                    }
                )

payload = OrderedDict(
    [
        ("schema", "daily-quality-rotate/v1"),
        ("day", day),
        ("stamp", stamp),
        ("host", host),
        ("base", base),
        ("verdict", "FAIL" if int(fail) else "PASS"),
        ("populationIndexed", int(pop)),
        ("popidxDistinctCodes", int(codes)),
        ("reevalRan", bool(int(reeval_ran))),
        ("measures", measures),
        ("checks", rows),
        ("command", "./scripts/daily-quality-rotate.sh " + host),
    ]
)

pathlib.Path(ev_json).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

lines = [
    f"# Daily quality rotate — {day} — `{host}`",
    "",
    f"**Verdict:** **{payload['verdict']}**  ",
    f"**Base:** `{base}`  ",
    f"**Stamp (UTC):** `{stamp}`  ",
    f"**POPIDX:** populationIndexed={pop}, popidxDistinctCodes={codes}  ",
    f"**CQL reeval:** {'ran' if payload['reevalRan'] else 'skipped'}  ",
    "",
    "## Checks",
    "",
    "| Status | Key | Detail |",
    "|--------|-----|--------|",
]
for r in rows:
    lines.append(f"| {r.get('status','').upper()} | `{r.get('key','')}` | {r.get('detail','')} |")

lines += [
    "",
    "## Measure table",
    "",
    "| Measure | SPARQL ippCount | SUM IPP/DENOM/NUMER/DENEX |",
    "|---------|-----------------|---------------------------|",
]
for mid in ("CMS165v14", "CMS122v14", "CMS130v14", "CMS125v14", "CMS138v14", "CMS2v15"):
    m = measures.get(mid, {})
    ippc = m.get("ippCount", "—")
    if all(k in m for k in ("ipp", "denom", "numer", "denex")):
        summ = f"{m['ipp']}/{m['denom']}/{m['numer']}/{m['denex']}"
    else:
        summ = "—"
    lines.append(f"| {mid} | {ippc} | {summ} |")

lines += [
    "",
    "## Reproduce",
    "",
    "```bash",
    f"cd HL7-FHIR-quality-testing && ./scripts/daily-quality-rotate.sh {host}",
    "```",
    "",
    f"JSON twin: `{pathlib.Path(ev_json).name}`",
    "",
]
text = "\n".join(lines)
pathlib.Path(ev_md).write_text(text, encoding="utf-8")
pathlib.Path(latest_md).write_text(text, encoding="utf-8")
print(f"wrote {ev_md}")
print(f"wrote {ev_json}")
print(f"wrote {latest_md}")
PY

echo ""
if [[ "$fail" -ne 0 ]]; then
  echo "daily-quality-rotate: FAIL ($HOST) — see $EV_MD" >&2
  exit 1
fi
echo "daily-quality-rotate: PASS ($HOST) — evidence $EV_MD"
exit 0
