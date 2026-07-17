# CMS 2026 Quality Measure Definitions - First-Wave Research

Status date: 2026-07-17

CMS publishes 2026 performance-period eCQM specifications through the eCQI Resource Center. The Eligible Clinician page lists 49 eCQMs for the 2026 performance period and links the official 2026 specifications ZIP and measure table. Measures are subject to CMS rulemaking; this workspace treats the eCQI specification ZIP as the implementation source of truth.

Primary sources:

- eCQI Eligible Clinician eCQMs: https://ecqi.healthit.gov/ep-ec/ecqms
- 2026 EC eCQM specification ZIP: https://ecqi.healthit.gov/2026-ecqm-specifications-eligible-clinicians-zip
- 2026 EC measures table: https://ecqi.healthit.gov/sites/default/files/2026-EligibleClinician-MeasuresTable-v2.pdf

## First-Wave Shortlist

| CMS ID | Measure | Why It Is In The First Wave | Key FHIR/Synthea Data Needed |
| --- | --- | --- | --- |
| CMS122v14 | Diabetes: Glycemic Status Assessment Greater Than 9% | Common ambulatory diabetes outcome; Synthea usually creates diabetes, encounters, and lab Observations. | Diabetes Condition, qualifying encounter, HbA1c Observation with LOINC, result value and date. |
| CMS165v14 | Controlling High Blood Pressure | High-value vital-sign measure and strong Inferno vital-sign overlap. | Hypertension Condition, qualifying encounter, Blood Pressure Observation with systolic/diastolic components. |
| CMS130v14 | Colorectal Cancer Screening | Screening measure with Procedure/Observation coverage and clear numerator events. | Age 45-75, qualifying encounter, colonoscopy/sigmoidoscopy/FIT/stool DNA procedure or lab. |
| CMS125v14 | Breast Cancer Screening | Screening measure with Imaging/Procedure-style numerator; useful for testing Procedure/DiagnosticReport gaps. | Female patients in target age range, qualifying encounter, mammography Procedure or DiagnosticReport. |
| CMS147v14 | Preventive Care and Screening: Influenza Immunization | Immunization path is already a July demo anchor; confirm 2026 eligibility during ZIP extraction. | Qualifying encounter and influenza Immunization with CVX/date in flu season. |
| CMS2v15 | Screening for Depression and Follow-Up Plan | Tests screening Observation/Questionnaire-like data and follow-up plan gaps. | Age >=12, qualifying encounter, depression screening Observation, follow-up intervention if positive. |
| CMS68v15 | Documentation of Current Medications in the Medical Record | MedicationRequest/MedicationStatement-adjacent workflow and common MIPS measure. | Qualifying encounter and medication documentation/review evidence. |
| CMS138v14 | Tobacco Use: Screening and Cessation Intervention | Tests social history Observation and intervention paths that may be thin today. | Tobacco status screening Observation and cessation counseling/medication for users. |
| CMS134v14 | Diabetes nephropathy / kidney-health sibling | Diabetes kidney measure family; verify exact 2026 title and logic from ZIP before cohort finalization. | Diabetes Condition, urine albumin/creatinine or nephropathy evidence, kidney-related lab/procedure. |
| CMS131v14 | Diabetes: Eye Exam | Diabetes screening measure; good for Procedure/Observation enrichment. | Diabetes Condition, qualifying encounter, retinal/eye exam Procedure or Observation. |

## Implementation Notes

For each measure, extract from the official 2026 ZIP:

1. Human-readable HTML specification.
2. ELM/JSON logic or CQL.
3. Value sets and direct-reference codes.
4. Initial population, denominator, numerator, denominator exclusions, and exceptions.
5. Required encounter types and measurement-period boundaries.

Each measure directory under `2026/measures/<CMSID>/` should include a focused README with:

- Denominator summary.
- Numerator summary.
- Exclusion/exception summary.
- Synthea source signals.
- Enrichment recipe.
- Inferno groups likely affected.

## Current Risk Flags

- CMS147v14 and CMS134v14 must be rechecked against the downloaded 2026 ZIP before final cohort work. If CMS147 is absent from the final 2026 EC table, substitute CMS22v14 blood pressure screening.
- CMS eCQM success is not identical to Inferno success. CQL membership confirms measure logic; Inferno confirms US Quality Core FHIR API behavior. Both are required for the September demo set.
- Some numerator evidence may not survive VistA load unless the Data-Loader supports the resource/domain. Those gaps should be captured as `/altfhir` green but `/fhir` red.
