#!/usr/bin/env bash
# Phase-0 linked-data smoke (docs/LINKED_DATA_STRATEGY.md in Vista-on-FHIR).
#
# Proves one real outbound link to each open linked-data target, walking one
# cohort medication (metformin, chosen by Sam 2026-09-03) from the local C0X
# graph out to the open knowledge web:
#
#   A. C0X SPARQL (local graph)  — metformin RxCUI 860975 in the cohort
#   B. RxNav (NLM)               — RxNorm properties + ATC class
#   C. Wikidata SPARQL           — drug entity by RxNorm CUI: ATC, indications
#   D. IDSM / ELIXIR SPARQL      — PubChem RDF compound (CID4091)
#   E. ClinicalTrials.gov API v2 — recruiting metformin/T2D trials
#
# Usage: ./scripts/linked-data-smoke.sh [outdir]
# Raw responses land in <outdir> (default docs/linked-data/runs/YYYYMMDD).
# Exit 0 only if every arm passes.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/docs/linked-data/runs/$(date +%Y%m%d)}"
mkdir -p "$OUT"

C0X_BASE="${C0X_BASE:-https://devfhir.vistaplex.org}"
UA="VistaOnFHIR-linked-data-smoke/0.1 (https://github.com/glilly/Vista-on-FHIR)"
RXCUI_SCD="860975"   # 24 HR metformin hydrochloride 500 MG ER Oral Tablet
RXCUI_IN="6809"      # metformin (ingredient)
PUBCHEM_CID="CID4091"

fail=0
pass() { echo "  PASS  $1"; }
bad()  { echo "  FAIL  $1" >&2; fail=1; }

echo "==> linked-data smoke — outputs in $OUT"

# --- A. local C0X graph: metformin orders in the population index ------------
Q_C0X='PREFIX c0x: <urn:c0x:>
SELECT ?resource ?code WHERE {
  VALUES ?code { "'"$RXCUI_SCD"'" }
  ?resource c0x:type "MedicationRequest" .
  ?resource c0x:code ?code .
}
LIMIT 200'
curl -sS --max-time 60 -G "$C0X_BASE/c0x/sparql" \
  --data-urlencode "query=$Q_C0X" --data-urlencode 'population=1' \
  -o "$OUT/a-c0x-metformin.json"
if python3 -c "
import json,sys
d=json.load(open('$OUT/a-c0x-metformin.json'))
assert d.get('candidates',0)>0, 'no candidates'
print('     candidates=%s' % d['candidates'])
" 2>/dev/null; then pass "A c0x local graph ($C0X_BASE)"; else bad "A c0x local graph"; fi

# --- B. RxNav: properties + ATC class ---------------------------------------
curl -sS --max-time 30 "https://rxnav.nlm.nih.gov/REST/rxcui/$RXCUI_SCD/properties.json" \
  -o "$OUT/b-rxnav-properties.json"
curl -sS --max-time 30 "https://rxnav.nlm.nih.gov/REST/rxclass/class/byRxcui.json?rxcui=$RXCUI_IN&relaSource=ATC" \
  -o "$OUT/b-rxnav-atc.json"
if grep -q 'metformin hydrochloride 500 MG Extended Release' "$OUT/b-rxnav-properties.json" \
   && grep -q 'A10B' "$OUT/b-rxnav-atc.json"; then
  pass "B RxNav properties + ATC"
else bad "B RxNav"; fi

# --- C. Wikidata: drug entity by RxNorm CUI ----------------------------------
Q_WD='SELECT ?drug ?drugLabel ?atc ?conditionLabel WHERE {
  ?drug wdt:P3345 "'"$RXCUI_IN"'" .
  OPTIONAL { ?drug wdt:P267 ?atc }
  OPTIONAL { ?drug wdt:P2175 ?condition }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
} LIMIT 25'
curl -sS --max-time 60 -H 'Accept: application/sparql-results+json' -H "User-Agent: $UA" \
  -G 'https://query.wikidata.org/sparql' --data-urlencode "query=$Q_WD" \
  -o "$OUT/c-wikidata-metformin.json"
if grep -q 'A10BA02' "$OUT/c-wikidata-metformin.json"; then
  pass "C Wikidata SPARQL (RxNorm $RXCUI_IN -> ATC A10BA02 + indications)"
else bad "C Wikidata SPARQL"; fi

# --- D. IDSM / ELIXIR: PubChem RDF compound ----------------------------------
Q_IDSM='SELECT ?p ?o WHERE { <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/'"$PUBCHEM_CID"'> ?p ?o } LIMIT 25'
curl -sS --max-time 60 -H 'Accept: application/sparql-results+json' \
  -G 'https://idsm.elixir-czech.cz/sparql/endpoint/idsm' --data-urlencode "query=$Q_IDSM" \
  -o "$OUT/d-idsm-pubchem.json"
if grep -q 'pubchem/vocabulary#Compound' "$OUT/d-idsm-pubchem.json"; then
  pass "D IDSM SPARQL (PubChem $PUBCHEM_CID)"
else bad "D IDSM SPARQL"; fi

# --- E. ClinicalTrials.gov v2: recruiting metformin/T2D trials ---------------
curl -sS --max-time 30 \
  'https://clinicaltrials.gov/api/v2/studies?query.intr=metformin&query.cond=type+2+diabetes&filter.overallStatus=RECRUITING&pageSize=5&fields=NCTId,BriefTitle,OverallStatus' \
  -o "$OUT/e-ctgov-trials.json"
if python3 -c "
import json
d=json.load(open('$OUT/e-ctgov-trials.json'))
assert len(d.get('studies',[]))>0
print('     trials=%d (first: %s)' % (len(d['studies']),
  d['studies'][0]['protocolSection']['identificationModule']['nctId']))
" 2>/dev/null; then pass "E ClinicalTrials.gov v2"; else bad "E ClinicalTrials.gov v2"; fi

if [[ $fail -eq 0 ]]; then echo "LINKED-DATA SMOKE OK"; else echo "LINKED-DATA SMOKE FAIL" >&2; fi
exit $fail
