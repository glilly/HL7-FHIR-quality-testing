# CMS2v15 - Screening for Depression and Follow-Up Plan

## Working Summary

Encounter denominator; screening and follow-up numerator.

## Source Of Truth

Extract the official 2026 eCQM artifacts from the CMS/eCQI 2026 Eligible Clinician specification ZIP before final cohort classification.

## Cohort Targets

- Denominator candidates: `../../cohorts/CMS2v15/denom/`
- Numerator-confirmed patients: `../../cohorts/CMS2v15/numer/`
- MeasureReports: `../../cohorts/CMS2v15/reports/`

## Enrichment Notes

Document the minimal Synthea JSON changes needed to move selected denominator patients into numerator membership. Keep each change tied to the measure logic and value-set evidence.

## Inferno Notes

Record the US Quality Core groups most affected by this measure and whether failures occur on `/altfhir`, `/fhir`, or both.
