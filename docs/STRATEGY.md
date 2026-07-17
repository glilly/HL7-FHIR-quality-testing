# HL7 FHIR Quality Testing Strategy

## Goal

Capture the July HL7/CMS Connectathon learnings and turn them into a reproducible September Connectathon development loop: create CMS eCQM-focused Synthea cohorts, validate source bundles and VistA round-tripped FHIR through hosted Inferno, and use the failures to drive loader/server hardening.

## Runtime Target

Use `devfhir` for all authoritative testing so hosted Inferno can reach the endpoint.

- Host: `devfhir.vistaplex.org` / container `fhirdev22`
- Graph/source endpoint: `https://devfhir.vistaplex.org/altfhir`
- VistA-generated endpoint: `https://devfhir.vistaplex.org/fhir`
- Intake endpoint: `https://devfhir.vistaplex.org/addpatient?load=0|1`

## Pipeline

1. Generate 1000 Synthea FHIR R4 transaction bundles.
2. POST them to `devfhir` with `load=0` so each bundle gets a graph IEN before VistA filing.
3. Run CQL/DEQM `$evaluate-measure` using 2026 CMS eCQM definitions to classify denominator/numerator membership.
4. Enrich selected bundles so each first-wave measure has about 18 patients in both denominator and numerator.
5. Validate graph-source bundles through hosted Inferno against `/altfhir`.
6. Load winning cohorts into VistA with `load=1`, then validate the VistA-generated `/fhir` output through hosted Inferno.
7. Fix high-value loader/server gaps, rerun, and freeze the best September demo set.

## Validation Roles

| Layer | Question | Tool |
| --- | --- | --- |
| Clinical | Is the patient in initial population, denominator, numerator, exclusions? | CQL/DEQM MeasureReport |
| FHIR shape | Does the endpoint satisfy US Quality Core searches, reads, profiles, and Must Support? | Inferno US Quality Core v0.5.0 |
| Round-trip | What was lost or changed when source Synthea loaded into VistA? | `/altfhir` vs `/fhir` diff plus Inferno delta |

## September Demo Selection

Prefer 3-5 measures with strong evidence across all three layers: confirmed MeasureReports, hosted Inferno scorecards on `/altfhir`, and hosted Inferno scorecards on `/fhir` after VistA load.
