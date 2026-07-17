# HL7 FHIR Quality Testing

Workspace for preparing VistA/RPMS FHIR quality testing for the September HL7 Connectathon. The repo combines CMS eCQM cohort work, Synthea patient enrichment, hosted Inferno US Quality Core validation, and scorecards for `devfhir`.

## Runtime Target

Authoritative validation runs use public `devfhir` endpoints so hosted Inferno can reach the server:

- Source-bundle phase: `https://devfhir.vistaplex.org/altfhir`
- VistA round-trip phase: `https://devfhir.vistaplex.org/fhir`
- Intake: `https://devfhir.vistaplex.org/addpatient?load=0|1`
- Direct listener for `/altfhir` hosted validation: `http://devfhir.vistaplex.org:9080/altfhir`

Local containers are useful for smoke testing, but scorecards in this repo should come from hosted Inferno against `devfhir`.

## Structure

- `docs/STRATEGY.md` - strategy and implementation plan.
- `docs/CMS_2026_QUALITY_MEASURES.md` - first-wave CMS eCQM research notes.
- `docs/connectathon/` - migrated July Connectathon and US Quality Core notes.
- `2026/measures/` - per-measure denominator/numerator notes and cohort requirements.
- `2026/cohorts/` - cohort manifests and MeasureReports.
- `2026/scorecards/inferno/` - hosted Inferno result summaries.
- `scripts/` - cohort generation, classification, enrichment, Inferno, and loading helpers.
- `openapi/vista-fhir-server.yaml` - OpenAPI entry for the VistA FHIR server surface used by this project.

## First-Wave Measures

The initial shortlist focuses on ambulatory measures that map well to Synthea and current VistA FHIR domains: diabetes A1c, blood pressure control, colorectal and breast screening, flu immunization, depression screening, medication documentation, tobacco screening, nephropathy/kidney-health, and diabetes eye exam.
