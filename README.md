# HL7 FHIR Quality Testing

Workspace for preparing VistA/RPMS FHIR quality testing for the September HL7 Connectathon. The repo combines CMS eCQM cohort work, Synthea patient enrichment, hosted Inferno US Quality Core validation, and scorecards for `devfhir`.

## Runtime Target

Authoritative validation runs use public `devfhir` endpoints so hosted Inferno can reach the server:

- Source-bundle phase: `https://devfhir.vistaplex.org/altfhir`
- VistA round-trip phase: `https://devfhir.vistaplex.org/fhir`
- Intake: `https://devfhir.vistaplex.org/addpatient?load=0|1`

Local containers are useful for smoke testing, but scorecards in this repo should come from hosted Inferno against `devfhir`.

## Structure

- `docs/STRATEGY.md` - strategy and implementation plan.
- `docs/INFERNO_QA_TEST_KIT_FIT_2026-09-18.md` - which Inferno QA kits we can use, later, or skip (Quality vs Coding).
- `docs/CMS165_HTN_R69_PLAN_POINTER.md` - CMS165 HTN coded as R69; canonical plan in WVEHR-on-FHIR (CQL 5/5/5 after repair).
- `docs/WVEHR_CODING_GAP_PLAN_POINTER.md` - multi-measure coding-gap scan/plan on WorldVistA EHR (`fhir.vistaplex.org`).
- `docs/RPMS_CODING_GAP_PLAN_POINTER.md` - multi-measure coding-gap scan/plan on RPMS (`rpmsfhir.vistaplex.org`).
- `docs/IRIS_CODING_GAP_PLAN_POINTER.md` - multi-measure coding-gap scan/plan on Iris (`irisfhir.vistaplex.org`).
- `docs/CMS_2026_QUALITY_MEASURES.md` - first-wave CMS eCQM research notes.
- `docs/connectathon/` - migrated July Connectathon and US Quality Core notes.
- `2026/measures/` - per-measure denominator/numerator notes and cohort requirements.
- `2026/cohorts/` - cohort manifests and MeasureReports.
- `2026/scorecards/inferno/` - hosted Inferno result summaries.
- `scripts/` - cohort generation, classification, enrichment, Inferno, and loading helpers.
- `openapi/vista-fhir-server.yaml` - OpenAPI entry for the VistA FHIR server surface used by this project.

## First-Wave Measures

The initial shortlist focuses on ambulatory measures that map well to Synthea and current VistA FHIR domains: diabetes A1c, blood pressure control, colorectal and breast screening, flu immunization, depression screening, medication documentation, tobacco screening, nephropathy/kidney-health, and diabetes eye exam.
