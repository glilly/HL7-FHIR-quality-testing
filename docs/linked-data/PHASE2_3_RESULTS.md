# Phase 2 + 3 results — federation gateway and trial-matching MVP

Date: 2026-09-04 (overnight run) · Strategy:
`Vista-on-FHIR/docs/LINKED_DATA_STRATEGY.md` · Follows
`PHASE1_HOST_READINESS.md`

## Phase 2 — searcher role: federation gateway on cds1

The quality-eval sidecar on `cds1.vistaplex.org` gained a linked-data
gateway (`cds-hooks-on-fhir/services/quality-eval/lib/linked-gateway.js`),
routed by Caddy at `/linked*`:

- **`POST /linked/enrich`** `{code}` — the full Phase-0 metformin walk as
  one server-side call: local C0X cohort → RxNav (name, ingredient, ATC)
  → Wikidata (entity, indications) → ClinicalTrials.gov (recruiting
  trials), joined into one JSON-LD-shaped answer. In-memory TTL cache
  (6 h) so live demos never depend on an uncached remote call.
- **`POST /linked/cohort-count`** `{code|sparql}` — fans one population
  SPARQL query out to the fleet (devfhir, fhir, rpmsfhir by default) and
  returns per-site counts + timings. **Aggregate-only by default**: no
  DFNs leave a site unless the caller passes `includeDfns:true`.
- `GET /linked/healthz` — liveness.

Verified live 2026-09-04:

| call | input | result |
|---|---|---|
| enrich | lisinopril 314076 | 381 orders on devfhir; ATC C09AA; `wd:Q47495698`; treats arterial hypertension; recruiting trials returned |
| cohort-count | metformin 860975 | devfhir 67 orders/3 pts · fhir 20/2 · rpmsfhir 557/1 → 644 matches / 6 patients |
| cohort-count | HCTZ 310798 | 3/3 sites ok, 933 matches / 25 patients |

Existing `/quality/*` routes re-smoked after the container rebuild.

## Phase 3 — trial-matching MVP

Pipeline (`scripts/trial-matching.py` + hand-structured criteria in
`2026/research/trial-criteria.json`):

1. Real trial metadata (title, registry status, verbatim eligibility
   text) pulled from ClinicalTrials.gov API v2 for four recruiting
   trials.
2. Each structured criterion runs as a C0X population SPARQL query
   (multi-code `VALUES`, the round-2 engine work) or a demographic check
   against the hydrated Patient resource. Value thresholds (HbA1c ≥ 8%)
   are presence-only and flagged for the CQL confirmation stage — the
   same two-stage pattern as the quality measures.
3. Output: FHIR R4 `ResearchStudy` per trial, `ResearchSubject`
   (status `candidate`) per eligible patient, `matches.json`, and a
   met/missed report.

Run against devfhir (25-patient synthetic cohort), 2026-09-04:

| trial | focus | pool | eligible | near-miss |
|---|---|---|---|---|
| [NCT06862739](https://clinicaltrials.gov/study/NCT06862739) | T2D triple therapy (T2D + metformin + A1c + 18-80) | 25 | **3** | 6 |
| [NCT06932874](https://clinicaltrials.gov/study/NCT06932874) | Metformin SR in T2D + CHD | 8 | **0** | 3 |
| [NCT06826872](https://clinicaltrials.gov/study/NCT06826872) | SPC1001 in essential HTN (HTN + antihypertensive + 18-75) | 27 | **10** | 15 |
| [NCT05413057](https://clinicaltrials.gov/study/NCT05413057) | FMS/AML fixed-dose combo in HTN | 27 | **14** | 13 |

The honest zero on NCT06932874 is the point: the cohort has no coronary
heart disease diagnoses, and the near-miss report says exactly that
(three patients missing only `chd`).

Published to the devfhir static lane
(`scripts/publish-research.sh` → `/filesystem/research/`):
[matches.json](https://devfhir.vistaplex.org/filesystem/research/matches.json),
`ResearchStudy-*.json`, `ResearchSubjects-*.json`, `report.md`,
`index.json`.

**UI**: the C0X Research panel's trial finder now annotates each hit
with the published match run — eligible count, near-miss count, DFNs —
instead of the "Phase 3" placeholder.

## Known limits

- Criteria are hand-structured for four trials; no automatic parsing of
  eligibility free text.
- Heuristic stage only; CQL confirmation of value thresholds
  (e.g. A1c ≥ 8%) is wired conceptually but not executed per-trial.
- Match run is a batch snapshot, not live per-query matching.
- All patients synthetic; aggregate-only posture enforced at the gateway,
  patient-level detail only inside the trust boundary.
