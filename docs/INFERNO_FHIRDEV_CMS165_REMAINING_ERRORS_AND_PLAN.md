# Hosted Inferno remaining errors & skips — fhirdev CMS165 cohort

Status date: **2026-07-27**  
Primary session (baseline): [bU76WglB84Q](https://inferno.healthit.gov/suites/us_quality_core_v050/bU76WglB84Q)  
Post–Phase 1 re-run: [6mxkzqWWNgp](https://inferno.healthit.gov/suites/us_quality_core_v050/6mxkzqWWNgp)  
Post–Phase 1b (remaining-4 cleared): [b4k7IkH6Spc](https://inferno.healthit.gov/suites/us_quality_core_v050/b4k7IkH6Spc)  
Post–Phase 2 Encounter MS: [ciGSfwD025U](https://inferno.healthit.gov/suites/us_quality_core_v050/ciGSfwD025U) (MS pass; validation failed on rank/POA)  
Post–Phase 2b Encounter MS fixed: [bA7DlEQpQLi](https://inferno.healthit.gov/suites/us_quality_core_v050/bA7DlEQpQLi)  
FHIR base: `https://devfhir.vistaplex.org/fhir`  
Cohort: CMS165 selected-18 **+ DFN 101090** (19 patients)  
Scorecard: `2026/scorecards/inferno/fhirdev-fhir-cms165-selected18-plus101090.json`  
Post–Phase 1: `2026/scorecards/inferno/fhirdev-fhir-cms165-selected18-plus101090-post-phase1.json`  
Post–Phase 1b: `2026/scorecards/inferno/fhirdev-fhir-cms165-selected18-plus101090-post-phase1b.json`  
Post–Phase 2: `2026/scorecards/inferno/inferno-fhirdev-cms165-20260727T204751Z-post-phase2-encounter-ms.json`  
Post–Phase 2b: `2026/scorecards/inferno/inferno-fhirdev-cms165-20260727T211824Z-post-phase2b-encounter-ms.json`  
Machine triage: `2026/scorecards/inferno/fhirdev-fhir-cms165-selected18-plus101090-triage.json`

Related earlier run (selected-18 only): [hOd61vtVwJF](https://inferno.healthit.gov/suites/us_quality_core_v050/hOd61vtVwJF) — 114p / 25f / 354s / 5e.

---

## Suite scoreboard


| Scope                    | Pass    | Fail   | Skip    | Error | Notes                                                   |
| ------------------------ | ------- | ------ | ------- | ----- | ------------------------------------------------------- |
| **Baseline suite (API)** | 117     | 23     | 353     | 5     | Includes `test_group` aggregate rows                    |
| **Baseline leaf**        | **115** | **12** | **310** | **1** | Actionable triage set                                   |
| **Post–Phase 1 suite**   | 129     | 11     | 358     | 0     | Session `6mxkzqWWNgp`                                   |
| **Post–Phase 1 leaf**    | **123** | **4**  | **311** | **0** | Vitals/DocRef/encounter-search cleared                  |
| **Post–Phase 1b suite**  | 136     | 0      | 362     | 0     | Session `b4k7IkH6Spc`                                   |
| **Post–Phase 1b leaf**   | **128** | **0**  | **310** | **0** | Phase 1 validation exit met                             |
| **Post–Phase 2b suite**  | 138     | 0      | 360     | 0     | Session `bA7DlEQpQLi` — Encounter MS + validation green |


Inferno marks a parent group `fail` when a child validation fails, which inflates fail/error/skip counts. **Use leaf counts for planning.**

---

## What already works (keep green)

Leaf groups with **no fails** and meaningful passes on this cohort:

- **Patient**, **Condition Encounter Diagnosis** (8/8), **Provenance**
- **AllergyIntolerance**, **Location**, **Organization**, **Practitioner** (search/read mostly green; Must Support still skips)
- Vital **search/read** paths largely pass; failures are concentrated in **validation** tests

CMS165-oriented evidence (encounters, vitals, hypertension conditions, immunizations, labs, notes) is present enough for Inferno to exercise those families — the remaining work is **shape/coding quality**, not “no data at all” for the CMS165 core.

---

## Leaf fails (12) — root causes

All 12 leaf fails are **profile validation** tests (not search). They collapse into **six fix buckets**:

### Bucket A — Vitals Quantity missing UCUM `system` + `code` (7 fails)


| Group                      | Profile                        |
| -------------------------- | ------------------------------ |
| `us_core_blood_pressure`   | us-core-blood-pressure|6.1.0   |
| `us_core_body_height`      | us-core-body-height|6.1.0      |
| `us_core_body_weight`      | us-core-body-weight|6.1.0      |
| `us_core_heart_rate`       | us-core-heart-rate|6.1.0       |
| `us_core_respiratory_rate` | us-core-respiratory-rate|6.1.0 |
| `us_core_body_temperature` | us-core-body-temperature|6.1.0 |
| `us_core_pulse_oximetry`   | us-core-pulse-oximetry|6.1.0   |


**Dominant validator errors** (thousands of instances across resources):

- `valueQuantity.system` / `valueQuantity.code` minimum required = 1, found 0
- BP components: `component:systolic|diastolic.value[x].system|code` missing
- BP also: top-level `Observation.value` emitted as **string** while profile expects Quantity slices
- Pulse ox additionally: missing `Observation.code.coding:O2Sat` LOINC slice (e.g. 2708-6 / 59408-5)

**Likely code:** Codex vitals export (`C0FWVIT` / observation builders used by `/fhir`) emits `unit` text (e.g. `mm[Hg]`) without `http://unitsofmeasure.org` + UCUM `code`.

**Impact if fixed:** Clears **7/12** leaf fails in one change family. Highest ROI.

### Bucket B — Condition code system mismatch (1 fail)

`condition_problems_health_concerns_validation_test`

- SNOMED codes (e.g. `38341003`, `73211009`) published under `http://hl7.org/fhir/sid/icd-10-cm` or ICD-9 systems → “Unknown code in CodeSystem”
- ~83 errors / ~392 warnings on this test alone

**Likely code:** problem-list / Condition export maps VistA coded values into the wrong FHIR `Coding.system`.

### Bucket C — DocumentReference missing category + type (1 fail)

`document_reference_validation_test` vs us-core-documentreference6.1.0

- `DocumentReference.category` required, found 0 (**823** resources)
- `DocumentReference.type` required from US Core DocumentReference Type VS (**823** resources)

**Likely code:** TIU → DocumentReference read path omits clinical-note category (LOINC 34133-9 class) and note type coding.

### Bucket D — Immunization CVX display strings (1 fail)

`immunization_validation_test`

- CVX code OK; **display** wrong (VistA/CVX long name vs HL7 preferred display for #208, #207, etc.)
- ~34 errors

**Fix:** map CVX → canonical display (or omit `display` and let clients resolve).

### Bucket E — JSON primitive types (2 fails)


| Group             | Symptom                                                                                               |
| ----------------- | ----------------------------------------------------------------------------------------------------- |
| `observation_lab` | `Observation.value[x]: Error parsing JSON: the primitive value must be a string` (2 lab Observations) |
| `encounter`       | `Encounter.type[0].coding[0].code`: primitive must be a string (`Encounter/E16602`)                   |


**Likely cause:** M/`XLFJSON` (or custom encoder) emits numeric JSON for FHIR string elements (`code`, and possibly some `value` forms). Validator then rejects the resource.

**Note:** The suite **error** on Encounter `patient+type` search (`casecmp?` for Integer) is almost certainly the same root cause — Inferno’s token matcher assumes string codes.

---

## Leaf errors (1)


| Test                                 | Message                                                                                                           |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `encounter_patient_type_search_test` | `undefined method 'casecmp?' for an instance of Integer` in `us_quality_core_test_kit-0.1.2` `search_test.rb:892` |


**Classification:** Triggered by our payload (non-string `Encounter.type.coding.code`), surfaces as an Inferno kit crash. Fixing Bucket E should clear this without waiting on an Inferno patch. Optionally file upstream against the test kit.

---

## Leaf skips (310) — taxonomy


| Class                                             | Count   | Meaning                                                                        |
| ------------------------------------------------- | ------- | ------------------------------------------------------------------------------ |
| **A. Cohort lacks resource type**                 | **233** | Inferno: “No X resources appear to be available / were found”                  |
| **B. Must Support / referenced elements missing** | **76**  | Resources exist, but required MS elements not present in any returned instance |
| **Other**                                         | 1       | Provenance author reference resolve                                            |


### Class A — expected for a CMS165 vitals/HTN cohort

Most skips are **not defects** for this patient list. The selected-18 (+101090) set was built for CMS165 CQL/IPP, not US Quality Core completeness.

Missing resource types driving Class A (from skip messages): Observation subtypes (smoking, BMI, pregnancy, clinical-result, screening), Medication*, Procedure*, ServiceRequest*, Task*, DeviceRequest*, DiagnosticReport*, CarePlan/CareTeam, Coverage, Goal, RelatedPerson, Specimen, PractitionerRole, AdverseEvent, FamilyMemberHistory, etc.

**Plan implication:** Do **not** chase Class A skips inside the CMS165 cohort. Chase them via **September showcase patients** (one patient per Inferno family) per `SEPTEMBER_MEASURE_INFERNO_ELEMENT_MAPPING.md`.

### Class B — Must Support gaps on resources we *do* return

High-value MS skips (resources present, MS incomplete):


| Group                                  | Missing Must Support (abridged)                                                                       |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Patient                                | `name.suffix`, `extension:tribalAffiliation`                                                          |
| Encounter                              | ~~`priority`, `reasonReference`, `diagnosis`, `hospitalization*`, POA extension~~ **done (Phase 2b)** |
| DocumentReference                      | `identifier`, `content.attachment.url`, `content.format`, `context.period`                            |
| Observation lab                        | `issued`, `valueCodeableConcept`, `specimen`                                                          |
| BP                                     | `component.dataAbsentReason` (systolic/diastolic)                                                     |
| Pulse ox                               | `component` FlowRate slice + quantities                                                               |
| Condition (problems)                   | `abatementDateTime`                                                                                   |
| AllergyIntolerance                     | `onset[x]`, `lastOccurrence`                                                                          |
| Location / Organization / Practitioner | address/telecom/NPI-style identifiers                                                                 |


These are the skip rows worth engineering after Bucket A–E validation fails are green.

---

## Attack plan

### Phase 0 — Re-baseline (½ day)

1. Keep session [bU76WglB84Q](https://inferno.healthit.gov/suites/us_quality_core_v050/bU76WglB84Q) as the baseline.
2. After each phase, re-run hosted Inferno on the **same 19 DFNs** and diff leaf fail/error counts.
3. Track leaf metrics only (ignore group-row inflation).

**Success:** repeatable scripted export of leaf pass/fail/skip/error.

### Phase 1 — Clear validation fails (Codex `/fhir` shape) — target: **12 → ≤2 leaf fails**

**Status 2026-07-27:** Code synced to fhirdev22; key DFN caches rebuilt (`INV^C0FWCAC` + `REFRESH` for 101090/101095/101096/101115/101122). Live smoke green for Condition SCT, lab/vital UCUM, CVX 208 display, Encounter string `code`. **Hosted Inferno re-run still needed** to confirm leaf fail counts.

Order by ROI:


| Step | Bucket | Change                                                                                                                  | Verify                                                                             |
| ---- | ------ | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| 1.1  | A      | Emit UCUM `system` + `code` on all vital `valueQuantity` / BP components; stop emitting BP panel `value` as bare string | BP/height/weight/HR/RR/temp validation pass                                        |
| 1.2  | A′     | Pulse ox: LOINC O2Sat coding slice + UCUM; FlowRate component if data exists                                            | pulse ox validation pass                                                           |
| 1.3  | E      | Force FHIR string JSON for `Coding.code` (Encounter.type, etc.) and fix lab `value[x]` encoding                         | encounter + lab validation pass; encounter patient+type search no longer **error** |
| 1.4  | B      | Condition Coding: SNOMED → `http://snomed.info/sct`; ICD-10/9 → correct sid; never put SCT codes under ICD systems      | problems/health-concerns validation pass                                           |
| 1.5  | C      | DocumentReference: `category` clinical-note + `type` from TIU title/LOINC map                                           | DocRef validation pass                                                             |
| 1.6  | D      | Immunization: CVX canonical display (or drop display)                                                                   | immunization validation pass                                                       |


**Owner surface:** `VistA-FHIR-Server-Codex` observation/condition/document/immunization export routines (vitals path centered on `C0FWVIT` / related Observation builders).

**Exit criteria:** leaf **fail ≤ 2**, leaf **error = 0** on same cohort.

### Phase 2 — Must Support enrichment for families we already emit (1–2 weeks)

Prioritize MS that unblock Inferno “could not find … in the N provided resource(s)” for **green families**:

1. **Encounter** — **done (Phase 2b / `bA7DlEQpQLi`)**: diagnosis, reasonReference, priority, hospitalization, POA
2. **DocumentReference** — type already in Phase 1; add `content.format`, `context.period`, attachment url or stable contentType
3. **Observation lab** — **done (`2ZWFBO4q4fD`)**: issued, specimen, valueString/valueCodeableConcept showcase
4. **Organization / Practitioner / Location** — telecom/address/NPI slices
5. **Patient** — only if easy wins; tribalAffiliation/suffix are low clinical value for demo

**Exit criteria:** MS skip count on Encounter/DocRef/Lab/Org/Pract drops; no new validation fails.

### Phase 3 — Cohort / showcase expansion for Class A skips (September track)

Do **not** overload the CMS165 19. Instead:

1. Maintain a **showcase DFN matrix** (one patient covering each missing Inferno family) — already sketched in `SEPTEMBER_MEASURE_INFERNO_ELEMENT_MAPPING.md`.
2. Prefer Synthea enrichment + `load=1` for Procedure, SmokingStatus, MedicationRequest, ServiceRequest, DiagnosticReport Lab, CarePlan as needed for CMS130/138/122 demos.
3. Run Inferno with a **union patient ID list** (CMS165 core + showcase add-ons) when measuring suite completeness.

**Exit criteria:** Class A skips for first-wave September measures move to exercised (pass or MS-gap Class B), not “no resources.”

### Phase 4 — Upstream / hygiene

1. File Inferno test-kit issue for `casecmp?` Integer crash (with repro Encounter JSON).
2. Optionally suppress or downgrade noisy Condition category draft-CodeSystem infos once coding is fixed.
3. Refresh connectathon session doc with new leaf scoreboard after Phase 1.

---

## Suggested sprint sequencing

```
Week 1: Phase 1.1–1.3 (UCUM + JSON string types) → re-run Inferno
Week 1–2: Phase 1.4–1.6 (Condition/DocRef/Imm) → re-run Inferno
Week 2–3: Phase 2 MS for Encounter + DocRef + Lab
Parallel: Phase 3 showcase patients for CMS130/138/smoking/meds
```

**Demo narrative after Phase 1:** “CMS165 cohort on fhirdev: search/read green for core US Quality Core families; validation green for vitals/conditions/notes/imm/labs; remaining skips are deliberate non-coverage outside the HTN cohort.”

---

> ## Appendix — leaf fail checklist
>
> Phase 1 code deployed to fhirdev **2026-07-27** (`C0FHIRD` SCTFROM + UCUM/VDEFU, `C0FHIRL` LABQTY, `C0FHIRM` CVXDISP, `C0FHIRBU` FORCESTR valueString, Encounter `"code","\s"`). Stale `fhir-dataframe` cache hid lab UCUM until INV+rebuild. **Re-run Inferno session to confirm leaf counts.**
>
> Smoke after deploy+cache rebuild (no `refresh=` required):
>
>
> | Resource              | Result                                            |
> | --------------------- | ------------------------------------------------- |
> | `Condition/C2577`     | SNOMED `38341003` (was ICD-10)                    |
> | Labs DFN 101122       | `valueQuantity` with UCUM `mg/dL` (was unit-only) |
> | Imm CVX 208           | `COVID-19, mRNA, LNP-S, PF, 30 mcg/0.3 mL dose`   |
> | Pain vitals           | UCUM `{score}`                                    |
> | BP components         | UCUM `mm[Hg]`                                     |
> | Encounter type coding | JSON string `code` (no unquoted numerics)         |
> | DocRef category/type  | Already green on live before this slice           |
>

- [x] `us_core_blood_pressure_validation_test` — UCUM on components (live smoke)
- [x] `us_core_body_height_validation_test` — UCUM (live smoke)
- [x] `us_core_body_weight_validation_test` — UCUM (live smoke)
- [x] `us_core_heart_rate_validation_test` — UCUM `/min` (live smoke)
- [x] `us_core_respiratory_rate_validation_test` — UCUM `/min` (live smoke)
- [x] `us_core_body_temperature_validation_test` — UCUM (live smoke)
- [x] `us_core_pulse_oximetry_validation_test` — LOINC 59408-5+2708-6 + UCUM `%` (live smoke)
- [x] `condition_problems_health_concerns_validation_test` — SNOMED system fix (live smoke; re-run Inferno)
- [x] `document_reference_validation_test` — category+type already present (live smoke)
- [x] `immunization_validation_test` — CVX 208 display (live smoke; re-run Inferno)
- [x] `observation_lab_validation_test` — creat value type (live smoke; re-run Inferno)
- [x] `encounter_validation_test` — string `code` (live smoke E16602)
- [x] `encounter_patient_type_search_test` (**error** → expect pass after string `code`)

---

## Appendix — how this was produced

```bash
python3 - <<'PY'
# leaf = results with test_id; classify fail messages / skip "No X resources"
# artifact: 2026/scorecards/inferno/fhirdev-fhir-cms165-selected18-plus101090-triage.json
PY
```

