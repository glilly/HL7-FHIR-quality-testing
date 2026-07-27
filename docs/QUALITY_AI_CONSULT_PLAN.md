# Quality AI Consult Plan

Status: first analysis pass after DFN `101090` `/fhir` reached zero hosted US Quality Core failures.

Implementation update:

- `cds-hooks-on-fhir` Stage 2 now supports `/analyze?mode=quality&measure=CMS165v14,CMS122v14`.
- `devfhir` `/aiconsult` now passes `mode` and `measure` through to `cds1`.
- Public smoke succeeded for `https://devfhir.vistaplex.org/aiconsult?dfn=101090&file=0&mode=quality&measure=CMS165v14,CMS122v14`.
- The first slice returns one Quality AI Consult `DiagnosticReport` for `CMS165v14` and one for `CMS122v14`, each with structured pick-list action extensions.
- Filing was intentionally smoked with `file=0`; chart-writing helpers remain the next implementation step.

## Thesis

Quality reporting needs more than a FHIR validator. Real-world users need a system that:

1. tests a patient's current record against a measure cohort,
2. explains whether the patient is outside the denominator, inside the denominator, inside the numerator, or missing evidence,
3. identifies the specific chart facts that would change that status,
4. presents those facts as clinician-reviewed pick lists, and
5. files the selected facts through normal VistA/RPMS record paths with provenance.

This fits naturally as a quality mode of AI Consult in `cds-hooks-on-fhir`. The CDS service can own analysis and pick-list generation. The VistA FHIR stack can own filing, read-back, and validation. The returned `DiagnosticReport` is the contract between those two halves.

## Current Evidence

IEN `482` proved that the source Synthea bundle can satisfy hosted US Quality Core through `/altfhir`:

- `/altfhir` IEN `482`: `447 pass / 0 fail / 51 skip`
- `/fhir` DFN `101090` before getter alignment: `106 pass / 23 fail / 369 skip`
- `/fhir` DFN `101090` after getter alignment: `129 pass / 0 fail / 369 skip`

The zero-fail `/fhir` run is important because it means the active VistA surface can now be validated cleanly. The remaining work is not generic conformance failure repair. It is deciding which skipped resource families matter for quality cohorts and then building safe record-generation helpers for those families.

## Existing Workflow To Reuse

The current AI Consult path already has the right skeleton:

- `/aiconsult?dfn=<dfn>&file=0|1` builds a patient FHIR bundle.
- `C0FWAIS` calls `https://cds1.vistaplex.org/analyze`.
- Returned `DiagnosticReport` resources are decorated as AI Consult reports.
- `file=1` sends the bundle through `/updatepatient`.
- `C0FWDOM` dispatches by resource type to native writeback adapters.
- `C0FWAIC` files AI Consult `DiagnosticReport` content as TIU.
- `C0FWTIU` already supports visit-linked note filing.
- `C0FWENC` already creates or reuses encounters and can file RPMS/PCE visit-linked add-ons.

The next version should extend this pattern instead of inventing a separate quality filing path.

## Proposed Quality Mode Contract

Quality AI Consult should return a FHIR `DiagnosticReport` with:

- `code`: identifies the measure and quality mode, for example `quality-gap-analysis`.
- `subject`: patient.
- `encounter`: optional existing or proposed encounter context.
- `conclusion`: human-readable summary of measure status.
- `conclusionCode`: machine-readable gap and action codes.
- `presentedForm`: markdown explanation for TIU filing.
- `extension`: pick-list actions, grouped by measure and by target VistA domain.

Each pick-list action should include:

- measure id, for example `CMS165v14`;
- cohort role: denominator, numerator, exclusion, exception, support evidence;
- clinical intent: add, attest, document not done, order, result, or note only;
- FHIR resource template to file if accepted;
- VistA/RPMS target domain;
- display text for the clinician;
- evidence source: CQL gap, Inferno skip family, source `/altfhir`, or local heuristic;
- safety level: auto-file prohibited, clinician-reviewed, or configuration-only.

Only clinician-reviewed actions should generate patient chart entries.

## Skip Family Analysis

The DFN `101090` condition-fix run has `369` skips and no failures. The top skipped families are:

| Family | Skip Pattern | Quality Interpretation | Pick-List Candidate |
| --- | --- | --- | --- |
| `ServiceRequest` / not requested | absent or missing patient/category/code/authored searches | orders, referrals, follow-up plans, or documented not-done services | yes, for follow-up and screening measures |
| `Observation` screening/clinical/simple/lab | absent category/code/date/status searches | screening assessments, lab results, social history, pregnancy, occupation, BMI | yes, when measure-specific |
| `DiagnosticReport` lab/note | absent lab/note report resources | grouped lab/report evidence and AI Consult output | yes for generated reports; careful for actual lab results |
| `Procedure` / not done | absent procedure resources | screenings, eye exams, colonoscopy, counseling procedures, not-done documentation | yes |
| `MedicationRequest` / not requested | absent medication order or not-done records | medication therapy or documented contraindication/refusal | yes |
| `MedicationAdministration` / `MedicationDispense` | absent administration/dispense evidence | usually downstream pharmacy/admin evidence | usually no for first pass |
| `CarePlan`, `Goal`, `Task` | absent planned follow-up artifacts | follow-up plan after screening or abnormal result | yes, but only after clear measure mapping |
| `DeviceRequest` / not requested | absent device orders | device-related numerator or not-done evidence | maybe; defer unless a selected measure needs it |
| `Immunization` not done | absent not-done immunization evidence | refusal/contraindication documentation | yes for immunization measures |
| `SmokingStatus` | absent smoking-status Observation | tobacco screening denominator/numerator evidence | yes |
| `Coverage`, `RelatedPerson`, `FamilyMemberHistory` | absent administrative/context resources | usually not measure-actionable for first shortlist | no for first pass |
| `Organization`, `Practitioner`, `Location`, `PractitionerRole` | missing Must Support details or resources | site/provider configuration and reference quality | no patient pick list |
| `Patient` demographics | suffix/tribal affiliation not present | demographic completeness, not measure-specific clinical gap | no patient pick list for quality mode |
| `Provenance` | revinclude skips | attribution gap for generated/loaded facts | infrastructure requirement |

The main rule: a skipped family becomes a Quality AI Consult pick-list candidate only if a selected measure needs that fact for denominator, numerator, exclusion, exception, or required support evidence.

## First Measure Cohort Matrix

| Measure | Cohort Need | Relevant Skip Families | Quality AI Consult Action Types | VistA/RPMS Helper Priority |
| --- | --- | --- | --- | --- |
| `CMS165v14` Controlling High Blood Pressure | hypertension denominator, BP numerator | `Condition`, BP Observation, Encounter | confirm HTN problem/POV, add reviewed BP, document encounter | already mostly present; refine vitals helper |
| `CMS122v14` Diabetes HbA1c Poor Control | diabetes denominator, HbA1c lab numerator | `Condition`, `Observation_lab`, `DiagnosticReport_lab` | confirm diabetes, add/import HbA1c result, group as lab report | high |
| `CMS130v14` Colorectal Cancer Screening | age/encounter denominator, screening numerator | `Procedure`, `DiagnosticReport_lab`, `Observation_lab`, `ServiceRequest` | document colonoscopy/FIT/FOBT, order or not-done reason | high |
| `CMS125v14` Breast Cancer Screening | age/sex denominator, mammography numerator | `Procedure`, `DiagnosticReport_note`, `ServiceRequest` | document mammogram, order follow-up | high |
| `CMS2v15` Depression Screening and Follow-Up | encounter denominator, screening and follow-up numerator | `Observation_screening_assessment`, `CarePlan`, `ServiceRequest`, `Procedure` | add PHQ screening result, add follow-up plan/referral | high |
| `CMS138v14` Tobacco Use Screening/Cessation | encounter denominator, smoking status and intervention numerator | `SmokingStatus`, `Procedure`, `MedicationRequest`, `ServiceRequest` | add tobacco status, cessation counseling, medication/order | high |
| `CMS68v15` Documentation of Current Medications | encounter denominator, medication review numerator | `MedicationRequest`, `DocumentReference`, `Procedure` | document med list reviewed, optional note/procedure | medium |
| `CMS131v14` Diabetes Eye Exam | diabetes denominator, eye exam numerator | `Procedure`, `Observation_clinical_result`, `DiagnosticReport_note` | document retinal/eye exam result | medium |
| `CMS22v14` / immunization-family replacement | immunization evidence or exception | `Immunization`, `ImmunizationNotDone` | add administered vaccine, refusal, contraindication | medium |

This matrix should be refined against each measure's CQL before implementation. It is good enough to drive the first engineering split.

## Action Safety Classes

| Class | Meaning | Examples | Filing Rule |
| --- | --- | --- | --- |
| Chart fact | clinician can attest and file as structured record | BP, smoking status, depression screen, historical procedure | pick-list may file after review |
| Order/request | clinician intends future action | mammogram order, colonoscopy referral, follow-up service request | pick-list may create order/request only if helper is explicit |
| Not done | clinician documents reason not performed | immunization refused, service not requested, procedure not done | pick-list may file with required reason |
| Result/import | objective result from lab/report | HbA1c, FIT/FOBT result | do not synthesize for real users; import or attest source |
| Configuration | site/provider metadata | NPI, CCN, address, practitioner role | not a patient pick list |
| Validator-only | optional Must Support not needed by measure | dataAbsentReason on complete BP, tribal affiliation | not a quality action |

## Architecture

1. **Measure gap analyzer in `cds-hooks-on-fhir`**
   - Input: patient Bundle from `/fhir`, optional source Bundle from `/altfhir`, selected measure ids.
   - Output: `DiagnosticReport` with summary plus pick-list extensions.
   - Responsibilities: CQL/measure interpretation, denominator/numerator gap classification, action ranking.

2. **Quality mode endpoint**
   - Extend the existing AI Consult call path with `mode=quality` and optional `measure=CMS165v14,CMS122v14`.
   - Keep `file=0` as preview-only.
   - Use `file=1` only after the clinician has selected actions.

3. **Pick-list UI**
   - CDS Hooks cards should show one card per measure or per high-priority gap.
   - Card suggestions should carry action ids, display text, and target helper type.
   - The UI must support accept/reject/edit before filing.

4. **DiagnosticReport action carrier**
   - The `DiagnosticReport` should be displayable as a TIU summary.
   - Structured pick-list actions should remain machine-readable in extensions.
   - The same report should be safe to file as an audit trail even if no chart facts are filed.

5. **Encounter generating helpers**
   - Existing `C0FWENC` should create/reuse a visit.
   - Existing C0FW adapters should file supported resources.
   - New helpers should be added only for missing high-value families: screening Observation, lab DiagnosticReport/Observation, ServiceRequest, not-done Procedure/Medication/Immunization, CarePlan/Goal.

6. **Read-back validation**
   - After filing, `/fhir` must expose the accepted facts.
   - Hosted Inferno and measure-specific CQL checks become the regression loop.

## Helper Backlog

| Helper | Purpose | Existing Support | Priority |
| --- | --- | --- | --- |
| Screening Observation writer | PHQ, tobacco, pregnancy, occupation, simple clinical assessments | vitals/labs exist but not general screening Observation | high |
| Lab result/report writer | HbA1c and screening lab evidence | `C0FWLAB` exists; lab report read-back needs measure focus | high |
| Procedure writer/not-done writer | colonoscopy, mammography, eye exam, counseling, not-done reasons | `C0FWPRC` exists; not-done profile likely needs extension | high |
| ServiceRequest writer/not-requested writer | referrals/orders/follow-up | no first-class support in dispatch | high |
| CarePlan/Goal writer | follow-up plans after positive screens | `C0FWCP` exists; needs quality-specific shape | medium |
| MedicationRequest not-done support | contraindication/refusal/therapy not ordered | medication adapter exists; not-done profile needs explicit support | medium |
| Immunization not-done support | contraindication/refusal | immunization adapter exists; not-done profile needs explicit support | medium |
| Provenance generator | attribution for AI-generated recommendations and accepted writebacks | generated Provenance exists for `/fhir` bundles; writeback provenance should be persisted | high |
| Configuration completer | NPI, location, organization, practitioner role | server getter/config work | low for pick-list mode |

## Implementation Plan

### Phase 1: Quality DiagnosticReport Schema

- Define the `DiagnosticReport` extension shape for pick-list actions.
- Add `mode=quality` and `measure=` parameters to the AI Consult gateway path.
- Keep output compatible with current `C0FWAIC` TIU filing.
- Add sample reports for `CMS165v14`, `CMS122v14`, `CMS2v15`, and `CMS138v14`.

Success criteria:

- `file=0` returns a patient plus a Quality AI Consult `DiagnosticReport`.
- The report includes measure status and structured actions.
- `file=1` can file the report as TIU without filing chart facts.

### Phase 2: Measure Gap Classifier

- Build a measure-resource map from the shortlist.
- For each measure, classify gaps as denominator, numerator, exclusion, exception, support evidence, or non-actionable.
- Use `/altfhir` as source-truth evidence when testing synthetic cohorts.
- Use `/fhir` as the real chart surface for round-trip loss detection.

Success criteria:

- For a selected patient, the analyzer can explain why each proposed item matters.
- Skipped Inferno families are only surfaced when they are relevant to the selected measure.

### Phase 3: Pick-List UI and CDS Hooks Cards

- Add quality-mode cards in `cds-hooks-on-fhir`.
- Card suggestions should carry action ids and proposed FHIR resource templates.
- UI should allow accept, reject, and edit.
- Accepted actions should be posted back as a Bundle through the existing update path.

Success criteria:

- A clinician can preview gaps and choose actions without filing.
- Accepted actions produce a deterministic update Bundle.

### Phase 4: Encounter and Domain Helpers

- Start with high-value helpers:
  - screening Observation,
  - lab Observation/DiagnosticReport,
  - Procedure/not-done,
  - ServiceRequest/not-requested,
  - CarePlan/Goal,
  - Provenance.
- Reuse `C0FWENC` to create/reuse the encounter.
- Extend `C0FWDOM` only when a new resource family is ready.

Success criteria:

- Accepted pick-list actions are filed as structured VistA/RPMS records where appropriate.
- `/fhir` read-back shows the filed facts.
- A rerun of hosted Inferno or measure-specific CQL shows the expected newly active group.

### Phase 5: Measure Cohort Rollout

- Start with `CMS165v14`, `CMS122v14`, `CMS2v15`, and `CMS138v14`.
- For each measure:
  - define denominator/numerator gap rules,
  - generate candidate actions,
  - implement needed helper(s),
  - test on Synthea cohort through `/altfhir`,
  - load and validate through `/fhir`.

Success criteria:

- At least one patient per measure demonstrates: gap detected, pick-list generated, action accepted, record filed, `/fhir` read-back improved, measure status changed.

## Recommended First Slice

The first slice should be `CMS165v14` plus `CMS122v14`.

Why:

- `CMS165v14` already aligns with the now-clean BP/vitals path.
- `CMS122v14` forces the lab Observation/DiagnosticReport path, which is a common blocker for many measures.
- Together they test both existing helper strength and the highest-value missing helper.

Deliverable:

- A Quality AI Consult report that can say:
  - this patient has denominator evidence,
  - this patient is missing numerator evidence,
  - here are the exact reviewed items that would satisfy the numerator,
  - here is what will be filed if the clinician accepts.

First-slice status:

- Implemented as deterministic quality mode in the Stage 2 CDS service.
- `CMS165v14` currently checks hypertension evidence and systolic/diastolic BP evidence.
- `CMS122v14` currently checks diabetes evidence and HbA1c evidence.
- Generated pick-list actions are advisory and `clinician-reviewed`; none are default-selected.
- Update Bundle + apply-review path files Encounter / DocumentReference / Condition; vitals via `C0FWVIT`.
- **2026-07-18:** `C0FWLAB` now files laboratory `Observation` through `LABADD^SYNDHP63` / ISI. HTTP smoke on DFN `101090` loaded HbA1c `7.4` and `/fhir` laboratory search returned it. Quality UI apply for `cms122-import-hba1c` is the remaining morning confirmation.
- **2026-07-27:** CMS165 closed loop on DFN **101115** (was DENOM yes / NUMER no): cds1 offers `cms165-record-blood-pressure` when BP is uncontrolled; HTTP update-bundle + `/updatepatient` filed **128/78** via GMVDCSAV; `/fhir` read-back OK; official CQL on Synthea+injected BP → **1/1/1**; dashboard SETPOP/SUM **16/16 (100%)**. See `docs/CMS165_CLOSED_LOOP_101115.md`.
- **2026-07-27 (same day):** rehmp Finish Note / Send now calls `POST /fhir-quality-recompute` (Codex `WSRECOMP^C0FQUAL`) for heuristic SETPOP/SUM refresh after accepted quality actions (CMS165 controlled BP; CMS122 HbA1c **>9%**). Gateway proxies recompute to `QUALITY_BACKEND` (fhirdev).
- **2026-07-27:** CMS122 closed loop on DFN **101096** (was DENOM yes / NUMER no): filed HbA1c **9.2** via `C0FWLAB`/`LABADD`; heuristic recompute + official CQL → **1/1/1**; dashboard SUM **5/4/1 (25%)**. See `docs/CMS122_CLOSED_LOOP_101096.md` and `scripts/cms122-closed-loop-101096.sh`. Remaining: Codex `/fhir` alone still too thin for CQL (use Synthea+inject or denser export).

## Open Questions

- Should Quality AI Consult call a real CQL engine first, or start with a local measure-resource classifier and add CQL execution as the verification layer?
- Should accepted actions file only structured records, or also file a TIU summary note for every quality intervention?
- Which domains are allowed to be documented by clinician attestation versus requiring external source import?
- Do we want one `DiagnosticReport` per measure or one aggregate report with per-measure action groups?
- Where should persistent writeback Provenance live: graph only, VistA TIU text, FHIR read-back, or all three?
