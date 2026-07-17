# CMS134v14 - Diabetes nephropathy / kidney-health sibling

## Working Summary

Diabetes denominator; kidney-health evidence numerator; verify exact 2026 title.

## Source Of Truth

Extract the official 2026 eCQM artifacts from the CMS/eCQI 2026 Eligible Clinician specification ZIP before final cohort classification.

## Cohort Targets

- Denominator candidates: `../../cohorts/CMS134v14/denom/`
- Numerator-confirmed patients: `../../cohorts/CMS134v14/numer/`
- MeasureReports: `../../cohorts/CMS134v14/reports/`

## Enrichment Notes

Document the minimal Synthea JSON changes needed to move selected denominator patients into numerator membership. Keep each change tied to the measure logic and value-set evidence.

## Inferno Notes

Record the US Quality Core groups most affected by this measure and whether failures occur on `/altfhir`, `/fhir`, or both.
