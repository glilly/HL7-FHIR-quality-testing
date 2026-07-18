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

The repository now installs `cqm-execution`/`cql-execution` and includes `scripts/fetch-2026-ecqm-artifacts.py` to fetch/extract official QDM packages. The next implementation step is the FHIR-to-QDM bridge for the highest-yield measures, starting with `CMS165v14` because its logic maps cleanly to FHIR Conditions, Encounters, and Blood Pressure Observations.

## Current Cohort Inventory

- Generated Synthea batch: `2026/patients/raw/synthea-1000-20260901-20260101/manifest.tsv`
- Devfhir graph cohort: `2026/patients/devfhir-ingest-load0-success-1000.tsv`
- Hosted Inferno source/round-trip scorecards: `2026/scorecards/inferno/`
