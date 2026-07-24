# September Plan: Quality Measures × Inferno US Quality Core Elements

Status date: 2026-07-23  
Audience: engineering + Connectathon prep  
Related: `STRATEGY.md`, `CMS_2026_QUALITY_MEASURES.md`, `SEPTEMBER_CONNECTATHON_RECOMMENDATIONS.md`, `QUALITY_AI_CONSULT_PLAN.md`, Vista-on-FHIR `docs/US_QUALITY_CORE_INFERNO.md`

## Goal

Pass as much of the hosted **Inferno US Quality Core Server v0.5.0** suite as possible by September, using **legitimate CMS eCQM test patients** (denominator + numerator), not synthetic filler-only charts.

Working idea:

> Turn on a small set of quality measures and keep **one strong patient per measure**.  
> Taken together, those patients should exercise the Inferno profile groups that are still missing or skipped today.

This document maps each first-wave measure to the Inferno data-element / profile groups it naturally requires, identifies **new** elements beyond what CMS165 + CMS122 already cover, and recommends which measures to prioritize for September.

## Two Success Criteria (Do Not Collapse Them)

| Layer | Question | Tool |
| --- | --- | --- |
| Clinical legitimacy | Is the patient in IPP / DENOM / NUMER for a real 2026 eCQM? | CQL / DEQM MeasureReport |
| FHIR Quality API | Does `/fhir` (and `/altfhir` source) satisfy US Quality Core search, read, profile, Must Support, and Provenance? | Inferno `us_quality_core_v050` |

A September demo patient must clear **both**. Green Inferno with a clinically nonsense chart is not the goal; green CQL with no Inferno coverage is also not enough.

## Inferno Surface (What “Data Elements” Means Here)

Inferno US Quality Core v0.5.0 currently generates **58 profile groups**. For planning we treat each group as a **data-element family**: resource type + profile semantics that Inferno will search, read, validate, and often Provenance-`_revinclude`.

Families already exercised well by CMS165 / CMS122 work (and VistA vitals/labs):

| Inferno group | Why it already shows up |
| --- | --- |
| Patient | Every cohort |
| Encounter | Qualifying visits |
| Condition Problems Health Concerns | HTN / diabetes problem list |
| Condition Encounter Diagnosis | Visit POV / encounter diagnosis |
| Observation US Core Blood Pressure | CMS165 numerator |
| Observation Laboratory Result | CMS122 HbA1c |
| DiagnosticReport for Laboratory Results Reporting | Lab panels / HbA1c report |
| DocumentReference | Progress / Quality AI Consult notes |
| Organization / Practitioner / Location | Reference resolution (partial) |
| Provenance | Cross-cutting; still incomplete |

Families that still drive large skip counts on showcase patients (see `QUALITY_AI_CONSULT_PLAN.md` skip analysis) and need **measure-motivated** data:

| Inferno group | Typical measure driver |
| --- | --- |
| Observation US Core Smoking Status | CMS138 |
| Observation Screening Assessment | CMS2 (PHQ / depression screen) |
| Observation Clinical Result | CMS131 eye exam / clinical findings |
| Procedure / Procedure Not Done | CMS130, CMS125, CMS131, CMS138 counseling |
| ServiceRequest / Service Not Requested | Follow-up orders (CMS2, CMS22, CMS125, CMS130) |
| CarePlan / Goal / Task | Follow-up plan after positive screen (CMS2) |
| MedicationRequest / Medication Not Requested | CMS68, CMS138 cessation meds |
| Immunization / Immunization Not Done | Immunization-family / CMS22 substitute slot |
| DiagnosticReport for Report and Note Exchange | Mammography / clinical notes as DR Note |
| AllergyIntolerance | Often present in Synthea; keep on at least one patient |
| Specimen | Lab pathway completeness (HbA1c / FIT) |

Out of scope for September measure-driven coverage unless leftover capacity (not needed by the first-wave eCQMs):

- AdverseEvent, Coverage, DeviceRequest(+Not), FamilyMemberHistory, RelatedPerson  
- Pregnancy Intent/Status, Occupation, pediatric BMI/weight/OFC  
- MedicationAdministration / MedicationDispense (+ declined/not-done variants)  
- Observation Cancelled, Simple Observation (unless a measure forces it)

Those can still be filled later with synthetic resources; they should not choose the September measure set.

## Measure → Inferno Element Mapping

For each measure: clinical facts required for legitimate DENOM/NUMER, Inferno groups those facts exercise, and **new** groups relative to a CMS165+CMS122 baseline.

Legend for **New vs baseline**:

- **Baseline** = already targeted by CMS165/CMS122 + current VistA vitals/labs  
- **New** = primary reason to turn this measure on for Inferno coverage  
- **Shared** = needed by the measure but already in baseline (still must be present on that patient)

### Mapping table (measures × Inferno groups)

| Inferno group (US Quality Core v0.5.0) | CMS165 BP | CMS122 A1c | CMS130 CRC | CMS125 Breast | CMS138 Tobacco | CMS2 Depression | CMS131 Eye | CMS68 Meds | CMS22 BP Screen† |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Patient | Shared | Shared | Shared | Shared | Shared | Shared | Shared | Shared | Shared |
| Encounter | Shared | Shared | Shared | Shared | Shared | Shared | Shared | Shared | Shared |
| Condition Problems / Encounter Dx | HTN | Diabetes | Shared‡ | Shared‡ | Shared‡ | Shared‡ | Diabetes | Shared‡ | Shared‡ |
| Observation Blood Pressure | **Baseline** | — | — | — | — | — | — | — | Shared |
| Observation Laboratory Result | — | **Baseline** (HbA1c) | **New** (FIT/FOBT/stool DNA) | — | — | — | — | — | — |
| DiagnosticReport Lab | — | **Baseline** | **New** (FIT panel) | — | — | — | — | — | — |
| Specimen | — | Shared | Shared | — | — | — | — | — | — |
| Observation Smoking Status | — | — | — | — | **New** | — | — | — | — |
| Observation Screening Assessment | — | — | — | — | — | **New** (PHQ) | — | — | — |
| Observation Clinical Result | — | — | — | — | — | — | **New** (retinal) | — | — |
| Procedure | — | — | **New** (colonoscopy / flex sig) | **New** (mammography) | **New** (cessation counseling) | Shared (follow-up) | **New** (eye exam) | Shared (med review) | Shared (follow-up) |
| Procedure Not Done | — | — | Optional | Optional | Optional | Optional | Optional | — | Optional |
| ServiceRequest / Not Requested | — | — | Optional order | **New** (imaging order) | Optional | **New** (referral) | Optional | — | **New** (follow-up) |
| CarePlan / Goal / Task | — | — | — | — | — | **New** (follow-up plan) | — | — | Optional |
| MedicationRequest / Not Requested | — | — | — | — | **New** (cessation Rx) | — | — | **New** (documented meds) | — |
| DiagnosticReport Note | — | — | — | **New** (mammo report) | — | — | Shared | — | — |
| DocumentReference | Shared | Shared | Shared | Shared | Shared | Shared | Shared | **New** (med-list note) | Shared |
| Immunization / Not Done | — | — | — | — | — | — | — | — | Optional†† |
| AllergyIntolerance | Keep on ≥1 patient (Synthea) | | | | | | | | |
| Provenance | Infrastructure for all patients / all groups | | | | | | | | |

† CMS22v14 is the 2026 substitute for the withdrawn CMS147 immunization slot in the EC QDM ZIP (`CMS_2026_QUALITY_MEASURES.md`).  
‡ Qualifying encounter / age-sex population; problem list not always measure-critical but helps Inferno Condition groups.  
†† Prefer a dedicated immunization patient if CMS22 alone does not force Immunization resources.

### Per-measure “new elements” summary

| Measure | Clinical DENOM / NUMER gist | New Inferno families unlocked | Loader / helper risk |
| --- | --- | --- | --- |
| **CMS165v14** Controlling High Blood Pressure | HTN + ambulatory encounter; controlled BP | *(baseline)* BP Observation components | Low — vitals path exists (`C0FWVIT`) |
| **CMS122v14** Diabetes Glycemic Status >9% | Diabetes + encounter; HbA1c result | *(baseline)* Lab Observation; Lab DiagnosticReport | Medium — `C0FWLAB` / AFICN fixed; keep Specimen/DR tight |
| **CMS130v14** Colorectal Cancer Screening | Age 45–75 + encounter; colonoscopy / FIT / stool DNA | Procedure; FIT Lab Obs/DR | High — Procedure + lab stool tests must survive load |
| **CMS125v14** Breast Cancer Screening | Female age band + encounter; mammography | Procedure; DiagnosticReport Note; ServiceRequest | High — imaging/note DR historically thin in VistA FHIR |
| **CMS138v14** Tobacco Screening & Cessation | Encounter; smoking status; intervention if user | **Smoking Status**; counseling Procedure; cessation MedicationRequest | Medium — social-history Obs often missing on `/fhir` |
| **CMS2v15** Depression Screening & Follow-Up | Age ≥12 + encounter; screen; follow-up if positive | **Screening Assessment**; CarePlan/ServiceRequest | High — new Observation category + follow-up artifacts |
| **CMS131v14** Diabetes Eye Exam | Diabetes + encounter; retinal/eye exam | Procedure; **Clinical Result** Observation | Medium — clinical-result profile distinct from lab |
| **CMS68v15** Documentation of Current Medications | Encounter; med list documented | MedicationRequest completeness; DocumentReference | Medium — MedRequest search/profile gaps |
| **CMS22v14** High BP Screening & Follow-Up | Encounter; BP screen; follow-up when indicated | ServiceRequest / follow-up Procedure (overlaps CMS165) | Medium — follow-up documentation is the new part |

## Coverage Plan: One Patient Per Measure

### Selection rule

For each activated measure, freeze **one showcase patient** that is:

1. In DENOM and NUMER on official (or workspace-verified) CQL for the 2026 definition.  
2. Loaded to VistA (`load=1`) with numerator evidence still visible on `/fhir`.  
3. Hosted-Inferno tested as part of a **multi-patient** Inferno session (comma-separated Patient IDs), so skipped groups on patient A can pass on patient B.

Do **not** expect one patient to green the whole suite. Inferno skips when the selected patients collectively lack a profile family.

### Recommended September portfolio (priority order)

| Priority | Measure | Showcase role | Primary new Inferno coverage | Engineering status (2026-07-23) |
| ---: | --- | --- | --- | --- |
| 1 | CMS165v14 | Anchor vitals / HTN | Blood Pressure (+ Condition/Encounter) | Active; CQL path proven on selected-18; Quality AI Consult BP writeback |
| 2 | CMS122v14 | Anchor labs / diabetes | Lab Observation + Lab DiagnosticReport | Active; Quality AI Consult HbA1c via `C0FWLAB` |
| 3 | CMS138v14 | Unlock smoking status | Smoking Status (+ cessation Procedure/MedRequest) | Cohort pending; high Inferno ROI |
| 4 | CMS2v15 | Unlock screening Obs + follow-up | Screening Assessment + CarePlan/ServiceRequest | Cohort pending; high Inferno ROI |
| 5 | CMS130v14 | Unlock screening Procedure + FIT | Procedure + stool Lab/DR | Cohort pending; high clinical visibility |
| 6 | CMS125v14 | Unlock note/imaging DR | DiagnosticReport Note + mammography Procedure | Cohort pending; harder VistA round-trip |
| 7 | CMS131v14 | Unlock clinical-result Obs | Observation Clinical Result + eye Procedure | After 130/125 Procedure path exists |
| 8 | CMS68v15 | Harden MedicationRequest | MedicationRequest Must Support / code search | After med cache/profile work |
| 9 | CMS22v14 | Follow-up orders (if imm slot empty) | ServiceRequest follow-up; optional Immunization patient | Only if Immunization still uncovered |

**September “turn on” target:** priorities **1–6** as active dashboard measures, each with one Inferno-ready DFN. Priorities 7–9 are stretch.

### Collective Inferno coverage (what the set buys)

With one good patient each for CMS165, CMS122, CMS138, CMS2, CMS130, CMS125:

| Inferno family | Covered by |
| --- | --- |
| Patient, Encounter, Condition | All |
| Blood Pressure | CMS165 (+ CMS22 if used) |
| Lab Observation / Lab DR / Specimen | CMS122 + CMS130 (FIT) |
| Smoking Status | CMS138 |
| Screening Assessment | CMS2 |
| Procedure | CMS130, CMS125, CMS138, CMS2 |
| ServiceRequest | CMS2, CMS125 |
| CarePlan / Goal / Task | CMS2 |
| MedicationRequest | CMS138, later CMS68 |
| DiagnosticReport Note | CMS125 |
| DocumentReference | All (notes / Quality AI Consult) |
| Provenance | Infrastructure on all |

Still likely thin after that set (accept as September backlog unless synthetic):

- Immunization / Not Done (add a dedicated imm patient if needed)  
- Observation Clinical Result (CMS131 stretch)  
- AdverseEvent, Coverage, Device*, FamilyMemberHistory, pediatric/pregnancy/occupation groups  

## Engineering Implications

### Helpers / loader work ordered by measure ROI

| Work item | Unlocks measures | Inferno groups |
| --- | --- | --- |
| Keep BP vitals + HTN Condition solid | CMS165, CMS22 | Blood Pressure, Condition, Encounter |
| Keep HbA1c lab + AFICN/ICN path solid | CMS122 | Lab Observation, Lab DR, Specimen |
| Smoking-status Observation on `/fhir` | CMS138 | Smoking Status |
| Screening-assessment Observation (PHQ LOINC) | CMS2 | Observation Screening Assessment |
| Procedure load/read for colonoscopy, mammo, eye, counseling | CMS130, CMS125, CMS131, CMS138 | Procedure |
| ServiceRequest (referral / imaging / follow-up) | CMS2, CMS125, CMS22, CMS130 | ServiceRequest |
| CarePlan or Task for positive depression follow-up | CMS2 | CarePlan / Task |
| DiagnosticReport Note for mammography | CMS125 | DiagnosticReport Note |
| MedicationRequest profile + `code` search | CMS68, CMS138 | MedicationRequest |
| Provenance generation + cache invalidation | All | Provenance `_revinclude` |

### Validation loop (per measure patient)

1. CQL MeasureReport: IPP/DENOM/NUMER.  
2. Hosted Inferno on `/altfhir` (source).  
3. `load=1` into VistA.  
4. Hosted Inferno on `/fhir` (round-trip).  
5. Record pass/fail/skip delta; only promote to September demo set when clinical + `/fhir` Inferno are both acceptable.

Track results in `SEPTEMBER_CONNECTATHON_RECOMMENDATIONS.md`.

## Suggested Inferno Multi-Patient Session Shape

Once showcase DFNs exist:

```text
patient_ids = <CMS165>,<CMS122>,<CMS138>,<CMS2>,<CMS130>,<CMS125>
```

Run full `us_quality_core_v050` against `https://devfhir.vistaplex.org/fhir` (and the `/altfhir` source set for the same graph IENs). Compare skip families before/after each new measure patient is added — the skip count for that family should drop when the new patient contributes the missing resource type.

## Decision Summary

1. **Keep CMS165 + CMS122 as the baseline pair** (vitals + labs + conditions).  
2. **Add CMS138 and CMS2 next** — they unlock unique Inferno Observation profiles (Smoking Status, Screening Assessment) and follow-up artifacts.  
3. **Add CMS130 and CMS125** to force Procedure + FIT lab + DiagnosticReport Note pathways.  
4. **Treat CMS131, CMS68, CMS22/immunization as stretch** once Procedure/MedRequest/ServiceRequest helpers exist.  
5. Use **one legitimate NUMER patient per activated measure**, combined in one Inferno session, to cover missing elements collectively rather than overloading a single chart.

## Open Items Before Freeze

- Confirm 2026 kidney-health replacement if that slot is still desired (CMS134 absent from EC QDM ZIP).  
- Decide whether Immunization coverage is a seventh showcase patient or folded into CMS22.  
- Produce the six showcase DFN/IEN pairs and paste them into `SEPTEMBER_CONNECTATHON_RECOMMENDATIONS.md`.  
- Re-run hosted Inferno after each patient is added; update the mapping table’s “engineering status” column.

## Appendix A — Full Inferno Group Catalog (v0.5.0)

Generated from `us-quality-core-test-kit` `metadata.yml` (58 groups):

AdverseEvent; AllergyIntolerance; CarePlan; CareTeam; Condition Encounter Diagnosis; Condition Problems Health Concerns; Coverage; DeviceRequest; Device Not Requested; DiagnosticReport Note; DiagnosticReport Lab; DocumentReference; Encounter; FamilyMemberHistory; Goal; Immunization; Immunization Not Done; Location; Medication; MedicationAdministration; MedicationAdministration Not Done; MedicationDispense; MedicationDispense Declined; MedicationRequest; Medication Not Requested; Observation Clinical Result; Observation Simple; Observation Screening Assessment; Observation Cancelled; Pregnancy Intent; Pregnancy Status; Smoking Status; Observation Lab; Occupation; Blood Pressure; BMI; Pediatric BMI for Age; Body Height; Body Temperature; Body Weight; Head OFC Percentile; Heart Rate; Pulse Oximetry; Respiratory Rate; Pediatric Weight for Height; Organization; Patient; Practitioner; PractitionerRole; Procedure; Procedure Not Done; Provenance; RelatedPerson; ServiceRequest; Service Not Requested; Specimen; Task; Task Rejected.

## Appendix B — First-Wave Measure IDs

From `CMS_2026_QUALITY_MEASURES.md` / `2026/measures/`:

`CMS165v14`, `CMS122v14`, `CMS130v14`, `CMS125v14`, `CMS138v14`, `CMS2v15`, `CMS131v14`, `CMS68v15`, `CMS22v14` (plus reserved slots CMS134/CMS147 marked absent or substituted in the 2026 EC ZIP).
