# CQL/DEQM Status

Status date: 2026-07-23 (VSAC expand + first cqm-execution batch)

The official 2026 Eligible Clinician eCQM package is downloadable from eCQI as:

- `https://ecqi.healthit.gov/sites/default/files/2026-EligibleClinician-eCQM_v2.zip`

Inspection shows the package contains 49 inner `*-QDM.zip` files. The first-wave available QDM measures are:

- `CMS122-v14.0.000-QDM`
- `CMS125-v14.0.000-QDM`
- `CMS130-v14.0.000-QDM`
- `CMS131-v14.0.000-QDM`
- `CMS138-v14.0.000-QDM`
- `CMS165-v14.0.000-QDM`
- `CMS2-v15.0.000-QDM`
- `CMS22-v14.0.000-QDM`
- `CMS68-v15.0.000-QDM`

`CMS147v14` and `CMS134v14` were not present in the 2026 EC ZIP. `CMS22v14` is the planned first substitute, and the diabetes kidney-health slot should be reselected from the final 2026 table after measure-owner review.

## Evaluator Architecture

The CMS EC artifacts are QDM/CQL, not FHIR-native DEQM `Measure` resources. Therefore machine denominator/numerator verification needs one of these paths:

1. **QDM execution path:** Convert each Synthea FHIR bundle to a CQM/QDM patient JSON model, then run `cqm-execution` against the official QDM CQL/ELM/value-set package.
2. **FHIR-native path:** Locate or author equivalent FHIR `Measure`/`Library` packages for the target measures, then run cqf-ruler or another FHIR R4 `$evaluate-measure` server.

The repository now installs `cqm-execution`/`cql-execution` and includes `scripts/fetch-2026-ecqm-artifacts.py` to fetch/extract official QDM packages.

## Bridge status (2026-07-23)

1. `scripts/fhir-to-qdm-patient.js` converts a FHIR R4 Bundle into a Project Tacoma QDM patient JSON sketch (Patient / Condition / Encounter / Observation including BP components and labs).
2. `scripts/build-cms165-cqm-package.js` assembles `measure.json` from eCQI ELM and, with `VSAC_API_KEY` / `UMLS_API_KEY`, expands all CMS165 ELM value sets via VSAC SVS into local `value_sets.json` (**gitignored**; do not publish expansions).
3. `scripts/evaluate-cms165-qdm.js` converts selected CMS165 bundles and **awaits** `cqm-execution.Calculator.calculate`.

**VSAC gate (cleared 2026-07-23):** 37/37 value sets expanded (5079 concepts). Key lives in `~/ops/secrets/`; load with `eval "$(~/ops/scripts/load-vsac-api-key.sh)"`. Full run notes: `docs/VSAC_CMS165_RUN_2026-07-23.md`.

**selected-18 after FHIR→QDM fixes (same day):** IPP **15** / DENOM **15** / NUMER **15** (of 18). Converter now keeps active Condition prevalence open-ended, expands BP panel components to SBP/DBP Physical Exam with `mm[Hg]`, and uses `urn:oid:` code systems. Broader preclassifier cohorts stay labeled **heuristic proxy** until a full-cohort CQL pass is reviewed.

Example:

```bash
eval "$(~/ops/scripts/load-vsac-api-key.sh)"
node scripts/build-cms165-cqm-package.js
node scripts/evaluate-cms165-qdm.js
```

## Current Cohort Inventory

- Generated Synthea batch: `2026/patients/raw/synthea-1000-20260901-20260101/manifest.tsv`
- Devfhir graph cohort: `2026/patients/devfhir-ingest-load0-success-1000.tsv`
- Hosted Inferno source/round-trip scorecards: `2026/scorecards/inferno/`

## Honesty note (2026-07-23)

CMS165v14 cohort lists from `scripts/cms165-fhir-preclassifier.py`
(193 denominator / 76 numerator among 1000 bundles) remain a **heuristic FHIR
proxy** at cohort scale. On the curated `selected-18` set, official
`cqm-execution` now reports **15 NUMER** after VSAC expand + converter fixes.
Connectathon messaging may cite that validated subset; do not equate the full
preclassifier counts with CQL MeasureReports until a wider pass is done.
