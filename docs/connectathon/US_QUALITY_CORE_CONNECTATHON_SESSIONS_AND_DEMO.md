# US Quality Core Connectathon — Inferno Sessions & Demo Plan

Status date: **2026-07-09** (triage pointer updated **2026-07-27**)  
Connectathon target: **Tuesday, 2026-07-14** (next Tuesday)

**Hosted fhirdev CMS165 remaining fails/skips:** see
[`../INFERNO_FHIRDEV_CMS165_REMAINING_ERRORS_AND_PLAN.md`](../INFERNO_FHIRDEV_CMS165_REMAINING_ERRORS_AND_PLAN.md)
(session [bU76WglB84Q](https://inferno.healthit.gov/suites/us_quality_core_v050/bU76WglB84Q)).

Companion to [`US_QUALITY_CORE_CONNECTATHON_READINESS.md`](./US_QUALITY_CORE_CONNECTATHON_READINESS.md).  
This note freezes the Inferno sessions we have already exercised, the suite-level
summary, and the **recommended live demo path** for next week.

## Demo endpoint (primary)

| Item | Value |
|------|--------|
| Inferno UI | `http://vendev15.vistaplex.org:8088/` |
| FHIR base (from Inferno) | `http://host.docker.internal:5178/fhir` |
| Adapter host | `vendev15` port **5178** |
| Backend | `http://devfhir.vistaplex.org:9080` (`fhirdev22`) |
| Suite | US Quality Core Server **v0.5.0** (`us_quality_core_v050`) |

Sharing results: copy the session URL, or export JSON via  
`GET http://vendev15.vistaplex.org:8088/api/test_sessions/{SESSION_ID}/results`.

Operational note: the HL7 validator service on vendev15 is memory-constrained
(~4 GiB host). It OOM-kills under load; restart with fhirpath stopped when
validation/reference tests error with
`Connection failed to validator at http://hl7_validator_service:3500`.

---

## Known Inferno sessions

### Session `1KOEFHWLEYN`

- **URL:** [http://vendev15.vistaplex.org:8088/us_quality_core_v050/1KOEFHWLEYN](http://vendev15.vistaplex.org:8088/us_quality_core_v050/1KOEFHWLEYN)
- **When:** mid–late work on Condition Encounter Diagnosis / Encounter hardening
  (2026-07-09).
- **Overall (API snapshot):** 70 pass · 64 fail · 55 error · 308 skip  
  High **error** count is largely validator-down during profile / MS-reference
  tests.
- **Notable group outcomes:**

| Group | Pass | Fail | Error | Skip |
|-------|-----:|-----:|------:|-----:|
| Patient | 2 | 0 | 1 | 2 |
| Condition Encounter Diagnosis | 5 | 0 | 2 | 1 |
| Condition Problems Health Concerns | 4 | 0 | 2 | 2 |
| Encounter | 4 | 0 | 2 | 3 |
| Immunization | 4 | 0 | 2 | 1 |
| Observation Lab | 4 | 0 | 2 | 3 |
| DiagnosticReport Lab | 6 | 0 | 2 | 1 |
| Procedure | 3 | 0 | 2 | 3 |
| US Core Blood Pressure | 5 | 0 | 2 | 2 |
| Observation Clinical Result | 0 | 0 | 0 | 9 |

- **Deep links used in triage:**
  - Encounter: `#1.51`
  - Observation Clinical Result: `#us_quality_core_v050-…-observation_clinical_result`  
    (all skip — expected; fixed Inferno `category=exam`, which we do not emit)

### Session `iKg1jPEaCmv`

- **URL:** [http://vendev15.vistaplex.org:8088/us_quality_core_v050/iKg1jPEaCmv](http://vendev15.vistaplex.org:8088/us_quality_core_v050/iKg1jPEaCmv)
- **When:** fuller suite run after later fixes; used as the suite-level snapshot
  below.
- **Overall:** **74 pass · 107 fail · 3 error · 308 skip · 5 cancel**
- **Deep links:**
  - Suite root: `#us_quality_core_v050`
  - Immunization: `#…-us_quality_core_v050_immunization` (all skip — patient
    without immunizations; use **101076**)

Other short-lived / browser-only runs earlier in the week (Condition 1.6, etc.)
were not retained as named session URLs; findings from those runs are folded
into readiness and into the patient matrix below.

---

## Suite summary (`iKg1jPEaCmv`)

### What is working well enough to show

- **Patient** — search/read core path is usable.
- **AllergyIntolerance** — search/read often pass when the patient has allergies.
- **Labs** — Observation Lab + DiagnosticReport Lab are among the strongest groups.
- **Many vitals** — Blood Pressure, Height, Weight, Temperature, Heart Rate,
  Pulse Ox, Respiratory Rate show multiple search/read passes.
- **Condition Problems Health Concerns** — strong partial (search/read/MS work;
  profile validation may still complain).
- **Condition Encounter Diagnosis** — search/read/MS work after V POV mapping
  and Encounter reference hardening (validator errors when service is down).
- **Procedure** — partial / demo-worthy with the right patient.

### What skips (data or scope)

- **Immunization** in `iKg1jPEaCmv` — empty for the patient used in that run
  (not a mapping absence: use **101076**).
- **Observation Clinical Result** — Inferno searches `category=exam`; we only
  emit `laboratory` / `vital-signs`, and `^AUPNVEXM` is empty on fhirdev.
  **Leave out of scope** for Tuesday (same call as readiness doc).
- Screening / SDOH / pregnancy / occupation / pediatric / smoking Observation
  groups — almost all skip.
- **Provenance** — skip across groups (not implemented).
- Request / Task / NotDone families (ServiceRequest, DeviceRequest, Task, etc.) —
  mostly fail/skip; do not demo.

### Main fail buckets (session `iKg1jPEaCmv`)

1. **Search returns OperationOutcome** (~46) — unsupported or unscoped resource
   type searches.
2. **Profile validation failures** (~16) — resource shape / coding / profile
   gaps after search succeeds.
3. **Other** (~47) — Must Support gaps, search matching quirks, reference
   validation, etc.
4. **Validator unavailable** — intermittent on this host; treat as infrastructure,
   not FHIR payload.

### Encounter / Immunization triage notes (2026-07-09)

- **`Encounter?_id=`** had returned OperationOutcome (“requires a patient id…”).
  Fixed in `C0FWCAC` (`REQDFN` / `DFNBYID`). Verified green path after deploy;
  **re-run Encounter group** before demo so the session record matches.
- Encounter date search indexing now includes `period.start` / `period.end`.
- Immunization USQC hardening deployed (`primarySource`, profile, statusReason
  coverage for MS, no bogus CPT `"NO SUCH ENTRY"`, `Encounter/E{id}` refs).
  Needs patient **with** immunizations: **101076**.

---

## Patients to use (and avoid)

| DFN | Use for | Notes |
|-----|---------|--------|
| **101076** | **Primary demo patient** | Immunizations (~23), encounters, labs/vitals. Best single-patient story for Tuesday. |
| **3** | Condition Encounter Diagnosis / Problems | Strong Condition graph; **no** immunizations; **no** exam Observations. |
| **101080** / **101082** | Immunization backup | Also have immunization counts. |
| **34** / **129** | Thin immunization / encounter smoke | Smaller sets. |
| **101086** | Older readiness “demo” DFN | Earlier notes favored this for Patient/labs; **do not** expect Immunization. Prefer **101076** for the live multimodal loop. |
| **8**, **25**, **50** | Avoid for cache search | Known `Patient graph row not found` issues on some paths. |
| **101086** Condition note | Avoid as Condition-empty example | Some IDs have little/no problem-list Condition; verify before demo. |

Working DFNs historically good for Condition search: **1, 3, 30, 100, 100001,
100002, 100003, 100010**.

---

## Recommended Tuesday demo script

Goal: a **credible, narrated** partial-pass — not an all-green suite.

### Setup (before audience)

1. Confirm adapter: `5178` → `devfhir:9080`.
2. Confirm Inferno at `:8088` and validator up (`hl7_validator_service` → HTTP 200
   from worker; stop fhirpath if memory is tight).
3. Warm patient **101076**:  
   `GET …/fhir/Encounter?patient=101076&refresh=1`  
   and/or Condition / Immunization with `refresh=1`.
4. New Inferno session; FHIR URL  
   `http://host.docker.internal:5178/fhir`;  
   **patient_ids = `101076`**.

### Run / show these groups (in order)

1. **Patient** — establishes the endpoint and patient identity.
2. **DiagnosticReport Lab** + **Observation Lab** — strongest “FHIR REST +
   profile intent” story.
3. **Vital signs** (pick 2–3): Blood Pressure, Heart Rate, Body Weight — search
   and read.
4. **Condition Problems Health Concerns** — if time, also **Condition Encounter
   Diagnosis** (narrate V POV → encounter-diagnosis + Encounter refs). On a
   second short run, patient **3** is fine for Conditions only.
5. **Encounter** — patient / `_id` / type / date search; admit MS hospitalization
   / diagnosis POA gaps.
6. **Immunization** — show completed + statusReason MS path after recent fixes;
   Provenance will skip.
7. **Procedure** — if time remains.

### Explicitly do **not** promise / demo live

- Observation Clinical Result (`category=exam`)
- Provenance `_revinclude`
- CarePlan / CareTeam / Coverage / Goal / AdverseEvent
- DeviceRequest / ServiceRequest / Task / *NotDone / *Declined families
- Pediatric / pregnancy / smoking / occupation Observation profiles
- Full-suite green

### How to narrate failures

| Bucket | One-line story |
|--------|----------------|
| Skip / no resources | Patient or domain not in demo scope / no VistA source yet |
| OperationOutcome on search | Resource type not in REST cache surface |
| Profile errors | Mapping hardening in progress; payload exists |
| Validator connection | Host OOM on Inferno validator; restart mid-session |
| Provenance | Not implemented |

### Capture for partners / AI

After each demo group: keep the session URL, and optionally save  
`/api/test_sessions/{id}/results` JSON. Screenshots help for a single failure;
JSON + URL scale better for full-group review.

---

## Monday prep checklist

- [ ] Re-run Encounter group on **101076**; confirm `_id` pass in a fresh session.
- [ ] Re-run Immunization on **101076**; confirm search/read/validation/MS.
- [ ] Spot-check Condition Encounter Diagnosis on **3** (or 101076 if POV present).
- [ ] Validator restart procedure documented for the booth laptop/operator.
- [ ] Keep this file and readiness.md open for “out of scope” answers.

## Related code / ops (this week)

- Encounter-diagnosis Conditions: `C0FHIRD`
- USQC Encounter / supporting resources: `C0FHIR`
- `_id` → DFN resolution + Encounter date index: `C0FWCAC`
- Immunization USQC fields: `C0FHIRM`
- Adapter reference cache: `Vista-on-FHIR/scripts/rpmsfhir-rest-adapter.py`
- Inferno on vendev15: `/opt/us-quality-core-test-kit`
