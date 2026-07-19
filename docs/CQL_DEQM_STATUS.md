# CQL/DEQM Status

Status date: 2026-07-17

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

## Bridge status (2026-07-19)

Prioritized before more cohort classification:

1. `scripts/fhir-to-qdm-patient.js` converts a FHIR R4 Bundle into a Project Tacoma QDM patient JSON sketch (Patient / Condition / Encounter / Observation including BP components and labs).
2. `scripts/evaluate-cms165-qdm.js` converts selected CMS165 bundles into `2026/cohorts/CMS165v14/qdm-patients/` and, when present, runs `cqm-execution` against:
   - `2026/measures/CMS165v14/cqm/measure.json`
   - `2026/measures/CMS165v14/cqm/value_sets.json`

Important gap: the official eCQI 2026 QDM ZIP contains CQL/ELM libraries under `2026/artifacts/extracted-shortlist/CMS165-v14.0.000-QDM/`, but **not** expanded value sets. `scripts/build-cms165-cqm-package.js` can assemble a best-effort `measure.json` from that ELM; `value_sets.json` still needs either:

1. `VSAC_API_KEY` / `UMLS_API_KEY` when running the builder, or
2. a Bonnie / MADiE export dropped into `2026/measures/CMS165v14/cqm/`.

Until value sets are expanded, the bridge converts patients but does not yet emit trustworthy MeasureReports.

Example:

```bash
node scripts/fhir-to-qdm-patient.js path/to/bundle.json /tmp/patient.qdm.json
VSAC_API_KEY=... node scripts/build-cms165-cqm-package.js
node scripts/evaluate-cms165-qdm.js
```

## Current Cohort Inventory

- Generated Synthea batch: `2026/patients/raw/synthea-1000-20260901-20260101/manifest.tsv`
- Devfhir graph cohort: `2026/patients/devfhir-ingest-load0-success-1000.tsv`
- Hosted Inferno source/round-trip scorecards: `2026/scorecards/inferno/`

## Honesty note (2026-07-18)

CMS165v14 membership currently comes from `scripts/cms165-fhir-preclassifier.py`
(193 denominator / 76 numerator among 1000 bundles). That is a **heuristic FHIR
proxy**, not an official QDM/CQL MeasureReport. September Connectathon docs should
label it as such until `cqm-execution` or FHIR `$evaluate-measure` produces
machine MeasureReports for the selected patients.
