# Phase-0 linked-data walk — metformin, local graph to the open knowledge web

Date: 2026-09-03 · Med chosen by Sam: **metformin** ·
Strategy: `Vista-on-FHIR/docs/LINKED_DATA_STRATEGY.md` (Phase 0) ·
Smoke: `scripts/linked-data-smoke.sh` · Raw responses: `runs/20260903/`

Every hop below is a **real remote link executed today** — no mocks. This is
the seed of the searcher-role demo: start from a medication code inside a
VistA C0X patient graph and enrich it across four open linked-data targets.

## The chain

### 1. Local C0X graph (devfhir.vistaplex.org)

Population SPARQL for the cohort's metformin orders:

```sparql
PREFIX c0x: <urn:c0x:>
SELECT ?resource ?code WHERE {
  VALUES ?code { "860975" }
  ?resource c0x:type "MedicationRequest" .
  ?resource c0x:code ?code .
}
```

Result: **67 MedicationRequest resources across 3 patients (DFNs 101109,
101119, 101124)** carry RxCUI `860975` — "24 HR metformin hydrochloride
500 MG Extended Release Oral Tablet". These are the same DFNs the CMS122
(diabetes A1c) lane knows well.

### 2. RxNav (NLM) — normalize and classify

- `GET rxnav.nlm.nih.gov/REST/rxcui/860975/properties.json` → confirms the
  SCD name and ties it to ingredient RxCUI **6809** (metformin).
- `GET …/rxclass/class/byRxcui.json?rxcui=6809&relaSource=ATC` → ATC class
  **A10BA (biguanides)** under A10B, "blood glucose lowering drugs".

### 3. Wikidata SPARQL — the drug as a linked-data entity

```sparql
SELECT ?drug ?drugLabel ?atc ?conditionLabel WHERE {
  ?drug wdt:P3345 "6809" .              # RxNorm CUI
  OPTIONAL { ?drug wdt:P267 ?atc }      # ATC code
  OPTIONAL { ?drug wdt:P2175 ?condition } # medical condition treated
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
```

Result: **wd:Q19484 (metformin)**, ATC **A10BA02**, conditions treated:
diabetes, hyperglycemia, maturity-onset diabetes of the young type 2. The
RxNorm CUI property (`P3345`) is the join key — the same code family our
graphs already store, which is why this hop needs no mapping table.

### 4. IDSM / ELIXIR SPARQL — chemistry context (PubChem RDF)

`SELECT ?p ?o WHERE { pubchem:CID4091 ?p ?o }` against
`idsm.elixir-czech.cz/sparql/endpoint/idsm` returns the PubChem compound
node for metformin (CID 4091) — typed `vocabulary#Compound` with descriptor
links. From here ChEMBL/DrugBank/ChEBI mirrors are one federated hop away.

### 5. ClinicalTrials.gov API v2 — trials our patients might match

`GET /api/v2/studies?query.intr=metformin&query.cond=type+2+diabetes&filter.overallStatus=RECRUITING`
returned 5 recruiting trials on the first page, e.g. NCT06932874 (metformin
SR in T2D with coronary heart disease) and NCT06120881 (precision dosing of
metformin in youth with T2D). No RDF here — trials arrive as JSON and become
linked data on our side (strategy Phase 3 turns these into `ResearchStudy`
resources and their eligibility criteria into C0X SPARQL + CQL).

## What this proves

- The **join keys already exist in our graphs**: RxNorm codes stored by C0X
  land directly on NLM and Wikidata identifiers with zero translation.
- All four target classes in the strategy (our own C0X node, NLM
  terminology, open SPARQL endpoints, the trial registry) answered real
  queries today; total wall time for the full smoke is under 2 seconds.
- The Phase-3 shape is visible end-to-end for one drug: cohort patients
  (101109/101119/101124, all in the CMS122 diabetes lane) ↔ metformin ↔
  recruiting T2D trials.

## Rerunning

```bash
./scripts/linked-data-smoke.sh            # writes docs/linked-data/runs/YYYYMMDD/
C0X_BASE=https://fhir.vistaplex.org ./scripts/linked-data-smoke.sh /tmp/lds  # other lanes
```

Notes: Wikidata requires a User-Agent header (set in the script). VSAC was
left out of the smoke because it needs a UMLS API key; RxNav covers the NLM
arm without auth.
