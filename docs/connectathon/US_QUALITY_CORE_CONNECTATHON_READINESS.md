# US Quality Core Connectathon Readiness

Status date: 2026-07-06

This plan maps the Inferno **US Quality Core Server v0.5.0** FHIR API tests to
the current VistA/RPMS FHIR bundle and REST-adapter capabilities, then lays out
the work needed to demonstrate meaningful progress at next week's connectathon.

The goal is not an all-green run. The near-term goal is a credible demo loop:

1. Select patients with known data.
2. Run targeted US Quality Core FHIR API groups.1
3. 
4. Show which FHIR REST interactions work now.
5. Explain remaining gaps as profile, terminology, data coverage, or unsupported
  domain work.



## Current Server Capabilities

Current deployed capabilities are strongest for patient-scoped bundle-backed
FHIR reads. The cache layer can build a full patient bundle, index it, and
answer REST-style search/read requests from that cache.

Supported REST resource types in the cache/search layer:

- `Patient`
- `Observation`
- `Condition`
- `DiagnosticReport`
- `Organization`
- `Encounter`
- `AllergyIntolerance`
- `Immunization`
- `Procedure`
- `MedicationRequest`
- `Medication`
- `DocumentReference`

Supported search parameters are generic, not profile-specific:

- References: `patient`, `subject`, `encounter`
- Tokens: `_id`, `identifier`, `code`, `category`, `status`,
`clinical-status`
- Dates: `date`, `recorded-date`, `authored`
- Patient strings: `name`, `family`, `given`
- Patient demographics: `gender`, `birthdate`

The adapter now bridges common Inferno behavior:

- `GET /fhir/{Resource}?patient=...`
- `POST /fhir/{Resource}/_search` with form bodies
- `GET /fhir/{Resource}/{id}` for resources already found in searches
- Reference resolution for `DiagnosticReport.result` and
`DiagnosticReport.performer` resources loaded from the patient bundle

Current bundle generation includes these domains:

- Patient demographics
- Encounters
- Conditions / problem list
- Vitals Observations
- Lab Observations
- Lab DiagnosticReports
- Reminder DiagnosticReports
- AllergyIntolerance
- MedicationRequest
- Immunization
- Procedure
- DocumentReference
- Supporting Organization for lab reports



## Inferno Test Pattern

Each generated US Quality Core group generally contains:

- Search tests, usually patient/subject plus one or more fixed search
parameters such as `category`, `code`, `date`, `status`, or `type`.
- Read test for a resource discovered by search.
- Profile validation through the HL7 FHIR validator and `tx.fhir.org`.
- Must Support coverage against resources returned in previous tests.
- Reference resolution tests for Must Support references.
- Provenance `_revinclude` tests where applicable.

This matters because we can often pass early search/read tests for resource
types we generate, while still failing profile validation or Provenance.

## Test Groups We Can Demonstrate Now



### Demo-Ready

These are the best connectathon demo targets because recent Inferno work has
already exercised them.

- `Patient`
  - Likely pass: `_id` search, read, much of profile validation, and many
  Must Support demographics for selected patients.
  - Known risks: terminology lookups can time out; language coding was
  intentionally left text-only after validator timeouts.
  - Demo patient: `101086` on `devfhir` is currently the strongest tested
  patient.
- `DiagnosticReport Lab`
  - Likely pass: patient search, patient + category, patient + category +
  date, patient + code, read, Must Support fields, and result/performer
  reference resolution.
  - Recent fixes: `Patient/{id}` subject references, `Organization/VISTA-LAB`
  performer, LOINC panel code, generated narrative, POST `_search`.
  - Known risks: terminology validation may report `tx.fhir.org` cache errors
  independent of payload shape.
- `Observation Lab`
  - Likely partial pass: patient/category/date search, read, subject reference
  resolution, and basic profile metadata for lab Observations.
  - Known risks: not all lab Observations have LOINC codes; profile validation
  and code search coverage depend heavily on source lab coding.



### Strong Partial Candidates

These are worth running during the connectathon, but should be presented as
profile-hardening work rather than finished conformance.

- Vital-sign Observation groups:
  - `us_core_blood_pressure`
  - `us_core_body_height`
  - `us_core_body_weight`
  - `us_core_body_temperature`
  - `us_core_heart_rate`
  - `us_core_pulse_oximetry`
  - `us_core_respiratory_rate`
  - `us_core_bmi`
  - Likely pass: patient/category/date and patient/code searches when the
  selected patient has matching vitals and LOINC mapping.
  - Known risks: BP component shape, profile-specific category/status
  requirements, value units, and missing generated narratives.
- `Condition Problems Health Concerns`
  - Likely pass: patient search, patient + category, possibly patient + code
  when SNOMED or ICD coding is present.
  - Known risks: current category is `problem-list-item`; Quality Core may
  split encounter diagnosis vs problem/health concern profile expectations.
  Some older RPMS data contains invalid ICD text and must rely on SNOMED.
- `AllergyIntolerance`
  - Likely pass: patient search and read when the selected patient has
  allergies.
  - Known risks: local VUID/allergy codes are not ideal for US Core
  validation; reaction manifestation coding may be incomplete.
- `Immunization`
  - Likely pass: patient search, patient + status, read when CVX is present.
  - Known risks: not-done profile split, manufacturer/location/performer
  references, and source system data coverage.
- `Procedure`
  - Likely pass: patient search, patient + date, patient + status, read for
  patients with CPT/radiology/surgery/clinical procedure data.
  - Known risks: code systems, category, performer references, and possible
  profile mismatch for procedure-not-done.
- `Encounter`
  - Likely pass: patient search, patient + date, `_id`, and read for patients
  with visits.
  - Known risks: encounter type coding, participant/location references, and
  profile completeness.
- `MedicationRequest`
  - Likely partial pass: patient + intent and read for patients with active or
  historical medication orders.
  - Known risks: the cache indexes generic `code`, but medication code lives in
  `medicationCodeableConcept`, so patient + code tests may not pass until
  cache indexing handles medication-specific paths.



### Data-Dependent Or Thin

These groups may produce skips or a few passes if a chosen patient happens to
have matching data, but they are not reliable demo anchors yet.

- `DocumentReference`
  - We have a bundle resource type and cache REST support.
  - Needs confirmation of current generated profile shape, category/type
  coding, date fields, and content attachment behavior.
- `DiagnosticReport Note`
  - Reminder DiagnosticReports are available, but they are local reminder
  reports rather than note DiagnosticReports.
  - Treat as exploratory only unless we map TIU notes into DiagnosticReport
  Note profile semantics.
- `Organization`
  - Supporting lab Organization can read successfully.
  - Useful mainly for reference resolution, not as a standalone conformance
  story.
- `Location`, `Practitioner`, `PractitionerRole`, `RelatedPerson`,
`Specimen`, `Provenance`
  - Current bundle/search support is either absent or too thin for reliable
  standalone groups.
  - Add only as supporting resources when needed for references.



### Out Of Scope For Next Week

These are not current bundle domains and should not be promised for the
connectathon demo:

- `AdverseEvent`
- `CarePlan`
- `CareTeam`
- `Coverage`
- `DeviceRequest`
- `DeviceNotRequested`
- `FamilyMemberHistory`
- `Goal`
- `MedicationAdministration`
- `MedicationAdministrationNotDone`
- `MedicationDispense`
- `MedicationDispenseDeclined`
- `MedicationNotRequested`
- `Observation Clinical Result`
- `Observation Screening Assessment`
- `ObservationCancelled`
- `PregnancyIntent`
- `PregnancyStatus`
- `Occupation`
- `Pediatric BMI for Age`
- `Pediatric Weight for Height`
- `ProcedureNotDone`
- `ServiceRequest`
- `ServiceNotRequested`
- `Task`
- `TaskRejected`

Some of these can be implemented later with synthetic/demo resources, but doing
that before the connectathon would distract from hardening the resources we
already have.

## Connectathon Demo Strategy



### Primary Demo Script

1. Start with `devfhir` through the `vendev15` adapter:
  - Inferno endpoint: `http://host.docker.internal:5178/fhir`
  - Current demo patient: `101086`
2. Run only these groups first:
  - Patient
  - DiagnosticReport Lab
  - Observation Lab
  - Blood Pressure
  - Body Height
  - Body Weight
  - Body Temperature
  - Heart Rate
  - Pulse Oximetry
  - Respiratory Rate
  - Condition Problems Health Concerns
  - Encounter
  - Immunization
  - Procedure
3. Capture screenshots and exported results after each group.
4. Explain failures using four buckets:
  - unsupported domain
  - missing data for selected patient
  - profile mapping gap
  - external terminology validator behavior



### Secondary Demo Script

Run the same selected groups against:

- `rpmsfhir` through adapter `5177`
- `fhir.vistaplex.org` through adapter `5179`

The purpose is comparison, not all-green validation. Use the same patient IDs
already known to have rich data on each server.

## Preparation Plan



### Day 1: Freeze The Demo Surface

- Pick one primary server for live demo: `devfhir` through `5178`.
- Pick two backup servers: `rpmsfhir` through `5177` and `fhir.vistaplex.org`
through `5179`.
- Confirm adapter processes are supervised or documented well enough to
restart during the event.
- Record the exact patient IDs to use for each server.

Success criterion: one command or short checklist can restore the demo endpoint
and adapter ports.

### Day 2: Build A Patient Coverage Inventory

For each candidate patient, record whether the bundle has:

- Patient demographics
- Encounters
- Conditions
- Vitals by type
- Labs
- Lab DiagnosticReports
- Allergies
- Immunizations
- Procedures
- MedicationRequests
- Documents

Success criterion: choose the best patient for each targeted Inferno group,
instead of relying on one patient for everything.

### Day 3: Patch High-Value Index Gaps

Add cache indexing for resource-specific fields that are already generated but
not indexed by the generic cache layer:

- `MedicationRequest.medicationCodeableConcept` as `code`
- `Immunization.vaccineCode` as `code`
- `Procedure.performedDateTime` as `date`
- `DocumentReference.type`, `category`, and `date`
- Vital Observation component codes for Blood Pressure, if Inferno expects
component-specific validation

Success criterion: patient + code/date/category searches return resources that
Inferno can verify against its own extracted search values.

### Day 4: Patch Low-Risk Profile Warnings

Add generated narrative and stable `Patient/{id}` subject references across
the demo resource types still using bundle UUID references.

Prioritize:

- vital Observations
- Conditions
- Encounters
- Immunizations
- Procedures
- MedicationRequests
- AllergyIntolerance

Success criterion: profile validation failures are about real coding/profile
content, not missing narrative or unresolved local references.

### Day 5: Baseline Runs

Run the selected groups on the primary demo server and save:

- group result screenshots
- request/response examples for one passing search and read per group
- a short failure notes file grouped by the four buckets above

Success criterion: connectathon demo can be repeated without discovering new
first-order failures live.

### Day 6: Backups And Public Demo

- Repeat a reduced test set against `5177` and `5179`.
- Verify the adapter script deployed on `vendev15` matches this repo.
- Verify `tx.fhir.org` behavior; note whether failures are payload issues or
terminology server cache/timeouts.

Success criterion: if `devfhir` has trouble during the event, there is a
fallback story using another server.

## Implementation Backlog For Better Results



### Highest Value

- Add resource-specific cache indexing for common search fields beyond the
generic paths.
- Emit stable relative references (`Patient/{id}`, `Encounter/{id}`,
`Organization/{id}`) consistently across generated resources.
- Add generated narratives to all demo resource types.
- Add CapabilityStatement entries that reflect the supported resource/search
surface so Inferno sees the intended API.



### Medium Value

- Add supporting resources for references:
  - Organization
  - Practitioner
  - PractitionerRole
  - Location
  - Specimen
- Add minimal Provenance resources or deliberately document `_revinclude` as
out of current scope.
- Improve LOINC/SNOMED/CVX/RxNorm coding coverage for demo patients.



### Defer

- New unsupported domains such as CarePlan, CareTeam, Coverage, DeviceRequest,
Task, ServiceRequest, and the not-done/declined variants.
- Full US Quality Core all-green ambitions.
- Broad synthetic resource fabrication that is not backed by VistA/RPMS data.



## Expected Connectathon Message

The demo should be framed as:

> We have a VistA/RPMS-backed FHIR bundle generator that now supports REST
> search/read behavior over cached patient bundles. We can demonstrate live
> Inferno US Quality Core partial conformance for Patient, DiagnosticReport
> Lab, labs/vitals Observations, and selected clinical domains. The remaining
> work is profile hardening, richer terminology mapping, support resources, and
> domains not yet generated from VistA/RPMS.

That is a strong connectathon posture: honest, reproducible, and centered on
working code rather than slideware.