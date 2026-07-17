# CMS147v14 - Influenza Immunization

## Working Summary

Encounter denominator; influenza immunization numerator; verify 2026 EC availability.

## Source Of Truth

Extract the official 2026 eCQM artifacts from the CMS/eCQI 2026 Eligible Clinician specification ZIP before final cohort classification.

## Cohort Targets

- Denominator candidates: `../../cohorts/CMS147v14/denom/`
- Numerator-confirmed patients: `../../cohorts/CMS147v14/numer/`
- MeasureReports: `../../cohorts/CMS147v14/reports/`

## Enrichment Notes

Document the minimal Synthea JSON changes needed to move selected denominator patients into numerator membership. Keep each change tied to the measure logic and value-set evidence.

## Inferno Notes

Record the US Quality Core groups most affected by this measure and whether failures occur on `/altfhir`, `/fhir`, or both.
