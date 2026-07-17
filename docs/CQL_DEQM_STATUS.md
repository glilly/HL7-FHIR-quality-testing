# CQL/DEQM Status

Status date: 2026-07-17

The Synthea generation and `devfhir` graph-ingest steps are complete for the initial 1000-patient working cohort. The exact denominator/numerator classifier is wired as `scripts/cohort-classify.py`, which expects a FHIR R4 measure server supporting `$evaluate-measure` with the official 2026 CMS/eCQI Measure and Library artifacts loaded.

Current state:

- Generated 1000-patient Synthea batch with additional generated bundles available for retry/top-off.
- Loaded at least 1000 unique bundles into `devfhir` graph storage with `load=0`.
- Wrote capped success manifest: `2026/patients/devfhir-ingest-load0-success-1000.tsv`.
- Created measure directories and cohort report locations under `2026/cohorts/<CMSID>/`.
- Created `scripts/cohort-classify.py` to call `$evaluate-measure` and write denominator/numerator manifests once the measure server is available.

Remaining validator dependency:

- Download/extract the official 2026 CMS Eligible Clinician eCQM specification ZIP.
- Load the Measure/Library/CQL/value-set package into cqf-ruler or an equivalent FHIR R4 measure server.
- Run `scripts/cohort-classify.py` for each first-wave CMS ID.

Until that measure server is available, the graph IEN manifest is the source cohort inventory and hosted Inferno is the active conformance validator.
