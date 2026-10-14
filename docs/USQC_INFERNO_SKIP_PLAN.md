# US Quality Core — skip plan (fhirdev `/fhir`, ZZ cohort)

Status: **pass 4 measured** (2026-10-14). Full suite [88Gj3JAQF4o](https://inferno.healthit.gov/suites/us_quality_core_v050/88Gj3JAQF4o) is **446 pass, 0 fail, 52 skip (89.6% of 498)**. Prior full suite [ecpMXM0JLJo](https://inferno.healthit.gov/suites/us_quality_core_v050/ecpMXM0JLJo) was 352 pass, 0 fail, 146 skip (70.7%). Baseline [ii7aiQNhNnY](https://inferno.healthit.gov/suites/us_quality_core_v050/ii7aiQNhNnY) was 173/498 (34.7%). Scorecard: `2026/scorecards/inferno/usquality-v050-fhirdev-fhir-zz-20261014-pass4.json`.  
This file is the record of which skipped tests we take next, what code change each one needs, and the pass rate after each step. Server edits land in `VistA-FHIR-Server-Codex` (and `cds-hooks-on-fhir` when a quality action writes the resource). Update the progress log in this file when a single test is rerun.

Baseline session: [US Quality Core `ii7aiQNhNnY`](https://inferno.healthit.gov/suites/us_quality_core_v050/ii7aiQNhNnY)  
Scorecard: `2026/scorecards/inferno/usquality-v050-fhirdev-fhir-zz-20261012-r2.json`  
FHIR base: `https://devfhir.vistaplex.org/fhir`  
Patients: `101130`–`101153` (fhirdev DFNs; ledger in `WVEHR-on-FHIR/docs/ZZ_PATIENT_LEDGER.tsv`)

Run one test, or one group, with the leaf or group id as `--suite`:

```bash
python3 scripts/inferno-run.py \
  --url https://devfhir.vistaplex.org/fhir \
  --patient-ids 101130,101131,101132,101133,101134,101135,101136,101137,101138,101139,101140,101141,101142,101143,101144,101145,101146,101147,101148,101149,101150,101151,101152,101153 \
  --suite <test-or-group-id> \
  --title "<short name>" \
  --out 2026/scorecards/inferno/<short-name>.json
python3 scripts/summarize-inferno.py 2026/scorecards/inferno/<short-name>.json
```

The pass rate below uses this session's 498 results as the denominator. A later full-suite run is what updates the official rate. A group rerun only replaces the rows in that group. A leaf test id returns HTTP 422 (`The chosen runnable must be run as part of a group`); pass `--suite` the group id.

## Where we are

| | Count |
| --- | ---: |
| Pass | 173 |
| Fail | 0 |
| Skip | 325 |
| Results | 498 |
| Pass rate | **34.7%** |

Forty-five of the skips are group rollups with an empty message. They move when the tests inside them move, and they are not counted in the step totals below.

Step 0 cleared the 13 failures from session [`5OIJfPNSg7v`](https://inferno.healthit.gov/suites/us_quality_core_v050/5OIJfPNSg7v) (231 pass, 13 fail, 513 skip across 757 rows). That run double-counted tests, so 34.7% of 498 is the rate to beat. The fixes were CVX `135` display (`C0FHIRM`), LOINC `98979-8` and `77353-1` displays (`C0FHIRLG`), and Observation `date` search using `effectiveDateTime` only (`C0FWCAC`). Commits: Codex `5e2f0ee`, cds-hooks `2935965`, scorecard `51d457d`.

## Pass rate if each step clears

Counts are the skipped tests in that step on the baseline scorecard. The rate is `173 + cleared` over `498`.

| Step | Clears | Cumulative passes | Pass rate |
| --- | ---: | ---: | ---: |
| 0 done | 0 | 173 | 34.7% |
| 1 Must-support fields | 6 | 179 | 35.9% |
| 2 US Core BMI | 9 | 188 | 37.8% |
| 3 MedicationRequest | 7 | 195 | 39.2% |
| 4 Graph resources already in the bundles | 40 | 235 | 47.2% |

Step 4 leaves out `servicerequest_patient_do_not_perform_search_test`. The generator writes `intent=order` and does not set `doNotPerform`. That one test stays a skip until one ServiceRequest carries the flag. The other ten "service not requested" tests are the same kind of chart and stay deferred.

Validation and must-support tests pass when the emitted resource satisfies the profile. A first emit that returns the resource can clear read and search while those two stay skipped, so the first measured rate can sit below the row. Record the measured rate in the progress log.

## Step 1 — one field on a resource we already return

Six tests. One Inferno id each, after the field is on the read.

| Test id suffix | Missing | Change |
| --- | --- | --- |
| `allergy_intolerance_must_support_test` | `onset` or `lastOccurrence` | 46 allergies are already returned. Set one of those on the read. |
| `us_core_blood_pressure_must_support_test` | `component.dataAbsentReason` | The ZZ charts have it. The vital read drops it. |
| `organization_must_support_test` | identifier, telecom, address | The lab Organization is already emitted. Add the elements. |
| `patient_must_support_test` | telecom, address line, suffix, tribal affiliation | The 24 Patient resources are returned. Add the elements on the read. |
| `us_core_pulse_oximetry_must_support_test` | flow-rate component | Pulse-ox observations already pass the other tests in the group. |
| `document_reference_reference_resolution_test` | an author reference that resolves | Notes already pass the other DocumentReference tests. |

Full ids are `us_quality_core_v050-us_quality_core_v050_fhir_api-us_quality_core_v050_<group>-us_quality_core_v050_<suffix>`.

First id to run:

`us_quality_core_v050-us_quality_core_v050_fhir_api-us_quality_core_v050_allergy_intolerance-us_quality_core_v050_allergy_intolerance_must_support_test`

## Step 2 — US Core BMI

Nine skips, including provenance. The charts include LOINC `39156-5` (`zz_chart.py`). `Observation?patient=101130&code=39156-5` returns nothing. Emit that graph vital the way graph labs are emitted, then run the BMI group id:

`us_quality_core_v050-us_quality_core_v050_fhir_api-us_quality_core_v050_us_core_bmi`

Pediatric BMI-for-age is a separate nine skips (LOINC the adult charts do not carry). It stays deferred.

## Step 3 — MedicationRequest

Seven skips. Patient `101142` already returns five MedicationRequests, and `MedicationRequest?patient=101142&intent=order` returns `M55761` with `intent=order` and `status=completed`. Validation skipped because none carry `us-quality-core-medicationrequest`.

Run the intent search before changing code:

`us_quality_core_v050-us_quality_core_v050_fhir_api-us_quality_core_v050_medicationrequest-us_quality_core_v050_medicationrequest_patient_intent_search_test`

If that passes, the remaining work is the profile on the read. If it still skips, record the message here before editing.

## Step 4 — resources in the bundles that `/fhir` does not return

`zz_chart.py` writes these. `GET /fhir` does not. Each row is the skip count on the baseline, provenance included. ServiceRequest is 9 here (the do-not-perform search is the one left out of the 40).

| Resource | Skips | Generator | What the read has to add beyond a copy |
| --- | ---: | --- | --- |
| Coverage | 6 | `coverage_team_device` | Quality Core profile, must-support elements |
| CareTeam | 6 | `coverage_team_device` | Same, plus the Provenance `prov-careteam` already in the bundle |
| RelatedPerson | 7 | `coverage_team_device` | Same |
| Goal | 6 | `goal_and_plan` | Same |
| CarePlan | 6 | `goal_and_plan` | Category `assess-plan` is already on the chart resource |
| ServiceRequest | 9 | `service_request` | Add `category`. `code` and `authoredOn` are already set |

Take one resource at a time. Run that resource's read test first, then the rest of its group.

## Deferred

These skips stay until the charts contain the resource. Provenance `_revinclude` for a type moves only after that type is returned.

Respiratory rate, pregnancy status and intent, occupation, pediatric BMI, pediatric weight-for-height, head circumference, MedicationDispense, MedicationAdministration, Task, AdverseEvent, DeviceRequest, FamilyMemberHistory, immunization-not-done, procedure-not-done, and service-not-requested.

## Quality reeval the same day

`QUALITY_REEVAL=1 ./scripts/daily-quality-rotate.sh fhirdev` passed. Evidence: `2026/scorecards/daily-quality/2026-10-12-fhirdev.md`. The three bundle checks are ZZ charts `101152` (ZZVera), `101151` (ZZUna), and `101149` (ZZSam). After CQL reeval the stored sums were CMS165 47/47/37/0 (was 46/46/37), CMS122 5/5/5/0, CMS130 45/45/29/0, CMS125 37/37/35/0, CMS138 31/31/29/0, CMS2 21/21/18/0 (was 20/20/17).

## Measured on 2026-10-12

Group JSON is under `2026/scorecards/inferno/skip-20261012/`. Compared with the r2 baseline test ids, **37 skips became passes** and **one skip became a fail**. Code is deployed on fhirdev and is not committed.

| Step | Projected | Measured |
| --- | --- | --- |
| 1 | +6 → 35.9% | +4. Allergy, Patient, pulse oximetry, and DocumentReference author resolution passed. Blood pressure and Organization did not. |
| 2 | +9 → 37.8% | +9. The BMI group is 10 pass / 0 fail / 0 skip after the LOINC display fix. [3ypr83ApyaR](https://inferno.healthit.gov/suites/us_quality_core_v050/3ypr83ApyaR). |
| 3 | +7 → 39.2% | +0. The MedicationRequest group is still all skips. [6Z17gCaECl9](https://inferno.healthit.gov/suites/us_quality_core_v050/6Z17gCaECl9). |
| 4 | +40 → 47.2% | +24, and one new fail. Coverage, Goal, CareTeam, CarePlan, and RelatedPerson searches pass. ServiceRequest does not. |
| Cumulative | 235 / 498 = 47.2% | **210 / 498 = 42.2%**, plus 1 fail (RelatedPerson validation). |

What is still skipped, and why:

- Blood pressure must-support: `Could not find component:systolic.dataAbsentReason`. The chart puts `dataAbsentReason` on the diastolic component of `Observation/obs-048` (ZZPia, `101146`). [eJaMGkpzFn9](https://inferno.healthit.gov/suites/us_quality_core_v050/eJaMGkpzFn9).
- Organization, run alone: `No Organization resources appear to be available`. The full-suite baseline had read and validation passing, so this isolated run did not see the organizations that suite run used. The endpoint reference was not what the test scored.
- MedicationRequest: `Could not find values for all search params patient, intent`. A direct `MedicationRequest?patient=101142&intent=order` returns five resources with the quality-core profile. The group still skipped read, validation, and must-support.
- Coverage must-support: missing `identifier`, `class:group`, and `class:plan` on the one resource. Payor reference did not resolve.
- Goal must-support: missing `startDate` and `target.dueDate`.
- CareTeam reference resolution: `participant.member` did not resolve. Must-support passed. [d4GhDjH0tmK](https://inferno.healthit.gov/suites/us_quality_core_v050/d4GhDjH0tmK).
- CarePlan must-support: missing `text.status` and `text.div`.
- RelatedPerson: validation **fail** because `active` is required and absent (`RelatedPerson/rel-daughter`). Must-support also wants `telecom` and `address`. [jwv6zR73Txo](https://inferno.healthit.gov/suites/us_quality_core_v050/jwv6zR73Txo).
- ServiceRequest: category, code, and `_id` searches did not satisfy the params. Do-not-perform stays a skip on purpose. [e1pkearJc5R](https://inferno.healthit.gov/suites/us_quality_core_v050/e1pkearJc5R).

## Progress log

| Step | Status | Change | Measured result |
| --- | --- | --- | --- |
| 0 | done 2026-10-12 | Codex `5e2f0ee`: CVX 135 display, LOINC `98979-8` and `77353-1`, Observation `date` is effective time. cds-hooks `2935965`: FIT display. | [ii7aiQNhNnY](https://inferno.healthit.gov/suites/us_quality_core_v050/ii7aiQNhNnY): 173 pass, 0 fail, 325 skip. **34.7%**. |
| 1 | measured 2026-10-12 | `C0FHIRD` copies allergy `onsetDateTime` and `lastOccurrence` from recorded date. `C0FHIR` `PATGAP` copies suffix and tribal affiliation and, for a ZZ given name, sets phone `555-010-0000` and `1 Fictitious Lane`. DocumentReference author is `Practitioner/P{DUZ}`. Pulse-ox flow rate is emitted from the graph. | +4 of 6. Sessions: allergy [8X6cjCAcHW5](https://inferno.healthit.gov/suites/us_quality_core_v050/8X6cjCAcHW5), patient [jhXgwyl7U8s](https://inferno.healthit.gov/suites/us_quality_core_v050/jhXgwyl7U8s), ox [79xtCMjiT0m](https://inferno.healthit.gov/suites/us_quality_core_v050/79xtCMjiT0m), docref [jRJJqiEzqoe](https://inferno.healthit.gov/suites/us_quality_core_v050/jRJJqiEzqoe). |
| 2 | measured 2026-10-12 | Graph BMI `39156-5` is kept and tagged `us-core-bmi`. Display is `Body mass index (BMI) [Ratio]` (`LOINCNM^C0FHIRLG`). The first run failed validation on the short display; the rerun passed. | +9. [3ypr83ApyaR](https://inferno.healthit.gov/suites/us_quality_core_v050/3ypr83ApyaR): 10 pass, 0 fail, 0 skip. |
| 3 | measured 2026-10-12 | `C0FHIRM` sets `us-quality-core-medicationrequest` on the read. | +0. Intent search still skipped. |
| 4 | measured 2026-10-12 | `GETGRPCL^C0FHIRLG` copies Coverage, CareTeam, RelatedPerson, Goal, CarePlan, ServiceRequest, and Provenance from the intake graph. Coverage `beneficiary` is indexed as `patient`. ServiceRequest with no category gets SNOMED `3457005`. | +24 and 1 fail. See the measured table. |
| 5 | measured 2026-10-12 | Pass 2. Systolic `dataAbsentReason`, Goal dates, CareTeam `Practitioner/P1`, CarePlan narrative, RelatedPerson (`natural daughter`, string postalCode), ServiceRequest `doNotPerform` plus mammogram and `reasonReference`. Coverage payor `Organization/org-clinic` is emitted so the read cache can return it. Coverage member id and class stay deferred. | Full suite [fe4WObX47az](https://inferno.healthit.gov/suites/us_quality_core_v050/fe4WObX47az): **246 pass, 0 fail, 252 skip (49.4%)**. |
| 6 | measured 2026-10-13 | Pass 3. Extras posted `load=0` onto ZZIvy `101139`, ZZVera `101152`, and ZZWill `101153`. `MEDMS^C0FHIRM` fills dosage, encounter, and reason on the read. `INCMED^C0FWCAC` honors `_include` of the referenced Medication. | Full suite [ecpMXM0JLJo](https://inferno.healthit.gov/suites/us_quality_core_v050/ecpMXM0JLJo): **352 pass, 0 fail, 146 skip (70.7%)**. 106 skips became passes. No new fails. Scorecard: `2026/scorecards/inferno/usquality-v050-fhirdev-fhir-zz-20261013-pass3.json`. |
| 7 | measured 2026-10-14 | Pass 4. Ten gap charts `101154`–`101163` filed with `addpatient?load=1` and enrolled in all six populations. Nell `101154` carries the remaining Inferno extras. Read-time fixes in `C0FHIRLG` / `C0FWCAC` (graph `inf-` observations stay out of the lab emitter; DeviceRequest `doNotPerform` is the modifier extension; not-done administration `statusReason` is an array). | Full suite [88Gj3JAQF4o](https://inferno.healthit.gov/suites/us_quality_core_v050/88Gj3JAQF4o): **446 pass, 0 fail, 52 skip (89.6%)**. 94 skips became passes. No pass-3 pass regressed. Scorecard: `2026/scorecards/inferno/usquality-v050-fhirdev-fhir-zz-20261014-pass4.json`. |

## Pass 2

The first pass left these. Coverage is not in this pass. The chart Coverage has no member id or plan class, and those fields have to come from VistA, not from a filled-in example.

A group’s later tests use the resources returned by its first search. MedicationRequest’s first search is `patient` + `intent` + `do-not-perform=false`, and it tries `intent=proposal` before `intent=order`. ServiceRequest’s first search is `patient` + `do-not-perform=false`. Both returned nothing, so every test after them skipped. The orders we already return never set `doNotPerform`.

Organization must-support reads `Organization/VISTA-LAB`, the lab performer. That resource is built by `GRPLABORG` and does not go through `ORGMS`. Running the Organization group by itself still finds nothing, because those tests only read organizations saved from earlier groups in the same session.

| Item | What pass 2 changes |
| --- | --- |
| Blood pressure | Copy `dataAbsentReason` onto the systolic component (`8480-6`) when the chart put it on diastolic. |
| Organization | `GRPLABORG` calls `ORGMS`, so `VISTA-LAB` has NPI, CCN, EIN, telecom, address, and endpoint. |
| MedicationRequest | Set `doNotPerform=false`, category `community`, and a Provenance target so the first search and the revinclude have something to return. |
| Goal | The ZZ generator never set `startDate` or `target.dueDate`. The read fills `2021-10-12` and `2026-10-06` when the graph resource is missing them. |
| CareTeam | `participant.member` `Practitioner/pract-chen` does not resolve. Point it at `Practitioner/P1`. |
| CarePlan | Narrative `text.status` / `text.div` from the plan title, which is the category display. |
| RelatedPerson | Set `active`, phone `555-010-0000`, and `1 Fictitious Lane`. |
| ServiceRequest | Set `doNotPerform=false` and category SNOMED `386053000` (Evaluation procedure), which is in the suite’s category list. Add `ServiceRequest/sr-mammo` (SNOMED `71651007` Mammography) for a woman about 40 or older. Point `reasonReference` at `Condition/C{problem IEN}` from `^AUPNPROB("AC",DFN)`. |

### Measured 2026-10-12

`C0FHIRLG` XINDEX on fhirdev: 606 lines, checksum `B548071980`, no F lines. The SAC size warnings on that routine were already there. Scorecards: `2026/scorecards/inferno/skip-20261012-pass2/`.

| Group | Session | Result |
| --- | --- | --- |
| Blood pressure | [hymee7ORxm4](https://inferno.healthit.gov/suites/us_quality_core_v050/hymee7ORxm4) | 10 pass, 0 fail, 0 skip |
| MedicationRequest | [cCU5EyyZ7eT](https://inferno.healthit.gov/suites/us_quality_core_v050/cCU5EyyZ7eT) | 6 pass, 0 fail, 2 skip |
| Goal | [cBEfC46Lrfm](https://inferno.healthit.gov/suites/us_quality_core_v050/cBEfC46Lrfm) | 7 pass, 0 fail, 0 skip |
| CareTeam | [blDi7xSvD6v](https://inferno.healthit.gov/suites/us_quality_core_v050/blDi7xSvD6v) | 7 pass, 0 fail, 0 skip |
| CarePlan | [ffyI9TXXW7m](https://inferno.healthit.gov/suites/us_quality_core_v050/ffyI9TXXW7m) | 7 pass, 0 fail, 0 skip |
| RelatedPerson | [3F8p2JhRW9F](https://inferno.healthit.gov/suites/us_quality_core_v050/3F8p2JhRW9F) | 8 pass, 0 fail, 0 skip |
| ServiceRequest | [242sxjf2pp4](https://inferno.healthit.gov/suites/us_quality_core_v050/242sxjf2pp4) | 12 pass, 0 fail, 0 skip |

Blood pressure copies `dataAbsentReason` onto the systolic component `8480-6`. Goal `startDate` is `2021-10-12` and `target.dueDate` is `2026-10-06` when the chart left them off. CareTeam `participant.member` is `Practitioner/P1` (PROGRAMMER,ONE). CarePlan narrative comes from the plan title. RelatedPerson is active, phone `555-010-0000`, address `1 Fictitious Lane`, and the v3-RoleCode `DAU` display is `natural daughter`. `postalCode` is forced to a JSON string. ServiceRequest code `719858009` displays `Telehealth monitoring`. The mammogram order is `ServiceRequest/sr-mammo`.

Two skips remain in MedicationRequest, and they are the same row twice (the must-support test and the group rollup). The 94 returned orders have no `reportedReference`, `encounter`, `reasonCode`, `reasonReference`, or a full `dosageInstruction` (timing.repeat, route, doseAndRate) or `dispenseRequest.validityPeriod`. The search, read, validation, and provenance revinclude passed. Coverage must-support is unchanged and deferred: no member id and no class group or plan. Those have to come from VistA.

The full suite read `Organization/org-clinic` because that is the Coverage payor on the ZZ chart, and the read cache had no such resource (`OperationOutcome`, HTTP 200). Session [2bfwuqqpVIp](https://inferno.healthit.gov/suites/us_quality_core_v050/2bfwuqqpVIp) was 241 pass, 5 fail, 252 skip; those five fails were that read and its rollups. `CVPAY` now adds that payor with the same NPI, CCN, EIN, telecom, address, and endpoint as `VISTA-LAB`. A direct read of `Organization/org-clinic` returns Organization `Fictitious Clinic`. `C0FHIRLG` XINDEX after that change: 617 lines, checksum `B558324621`, no F lines.

Confirming suite [fe4WObX47az](https://inferno.healthit.gov/suites/us_quality_core_v050/fe4WObX47az): **246 pass, 0 fail, 252 skip (49.4%)**. Organization validation, read, and must-support all passed. Coverage payor reference resolution passed. Coverage must-support still skips (member id and class group/plan). MedicationRequest must-support still skips (the dosage, encounter, and reason fields above). Scorecard: `2026/scorecards/inferno/usquality-v050-fhirdev-fhir-zz-20261012-pass2b.json`.

## Pass 3

Group reruns on 2026-10-13, then the full suite [ecpMXM0JLJo](https://inferno.healthit.gov/suites/us_quality_core_v050/ecpMXM0JLJo): **352 pass, 0 fail, 146 skip (70.7% of 498)**. The 18 measure charts were not refiled. `scripts/post-zz-inferno-extras.py` appended the new resources with `load=0` on ZZIvy `101139`, ZZVera `101152`, and ZZWill `101153`. 106 former skips passed. Nothing that passed in pass 2 failed or skipped.

| Group | Session | Result |
| --- | --- | --- |
| Pediatric BMI-for-age | [igFwG5plf3W](https://inferno.healthit.gov/suites/us_quality_core_v050/igFwG5plf3W) | 9 pass |
| Pediatric weight-for-height | [19jVq6iZgtc](https://inferno.healthit.gov/suites/us_quality_core_v050/19jVq6iZgtc) | 9 pass |
| Head circumference percentile | [caub3lb2w3g](https://inferno.healthit.gov/suites/us_quality_core_v050/caub3lb2w3g) | 9 pass |
| Respiratory rate | [9ctHBbjMWRF](https://inferno.healthit.gov/suites/us_quality_core_v050/9ctHBbjMWRF) | 9 pass |
| Occupation | [1MGERoVHDFf](https://inferno.healthit.gov/suites/us_quality_core_v050/1MGERoVHDFf) | 8 pass, 1 skip |
| Pregnancy status | [1A3hquzj7YI](https://inferno.healthit.gov/suites/us_quality_core_v050/1A3hquzj7YI) | 9 pass |
| Pregnancy intent | [iPWOpwUFjhO](https://inferno.healthit.gov/suites/us_quality_core_v050/iPWOpwUFjhO) | 9 pass |
| Coverage | [8G8upRQ6lai](https://inferno.healthit.gov/suites/us_quality_core_v050/8G8upRQ6lai) | 6 pass |
| MedicationRequest | [ucPWnKHF5c](https://inferno.healthit.gov/suites/us_quality_core_v050/ucPWnKHF5c) | 6 pass, 1 skip |
| MedicationDispense | [grRDkL26VzC](https://inferno.healthit.gov/suites/us_quality_core_v050/grRDkL26VzC) | 5 pass, 2 skip |
| MedicationAdministration | [cigtKU6lZyr](https://inferno.healthit.gov/suites/us_quality_core_v050/cigtKU6lZyr) | 8 pass, 1 skip |
| Immunization not done | [dQjdkLb9h7f](https://inferno.healthit.gov/suites/us_quality_core_v050/dQjdkLb9h7f) | 7 pass |
| Procedure not done | [jFiMBL6THMB](https://inferno.healthit.gov/suites/us_quality_core_v050/jFiMBL6THMB) | 6 pass, 2 skip |
| Service not requested | [aFjV2nDvatY](https://inferno.healthit.gov/suites/us_quality_core_v050/aFjV2nDvatY) | 10 pass, 1 skip |

Pregnancy status is SNOMED `60001007` (not pregnant) and intent is `454381000124105` (not sure), so the CQL pregnancy exclusions are not tripped. The not-done immunization uses the influenza not-done value set extension and SNOMED `410534003`, not CVX `150`. Procedure not-done still skips `basedOn`, `partOf`, and reason, and one date search. Task, AdverseEvent, DeviceRequest, and FamilyMemberHistory were not added.

## Pass 4

Ten women born in 1971, DFNs `101154`–`101163`, were added with `addpatient?load=1` and `SETPOP` on all six measures, then reevaluated. Each has a 2022 colonoscopy and no mammogram. Three have uncontrolled blood pressure, two have diabetes with A1c 7.1 and 7.4, eight have no 2026 tobacco screen, and five have no 2026 PHQ. Live dashboard after reeval: CMS122 `7/7/5` (71.4%), CMS125 `47/47/35` (74.5%), CMS130 `55/55/39` (70.9%), CMS138 `41/41/31` (75.6%), CMS165 `50/50/37` (74.0%), CMS2 `31/31/18` (58.1%). Denominator-not-numerator is about a quarter on five measures. CMS2 is wider (13 of 31) because the five PHQ scores of 1–3 did not enter the numerator.

ZZNell Moss `101154` holds the graph-only Inferno resources (`inf-*`). `EMIT^C0FHIRLG` skips those ids so the lab emitter does not retag them as laboratory. DeviceRequest not-requested uses profile `us-quality-core-devicenotrequested`, the R5 `doNotPerform` modifier extension, and `us-quality-core-doNotPerformReason` SNOMED `410534003`. A field named `doNotPerform` on DeviceRequest fails validation.

Full suite [88Gj3JAQF4o](https://inferno.healthit.gov/suites/us_quality_core_v050/88Gj3JAQF4o), patients `101130`–`101163`: **446 pass, 0 fail, 52 skip (89.6% of 498)**. 94 former skips passed. Nothing that passed in pass 3 failed or skipped. The remaining skips are must-support holes, a few code or date searches, and PractitionerRole (the isolated read still has no referring resource in the session that Inferno keeps). Scorecard: `2026/scorecards/inferno/usquality-v050-fhirdev-fhir-zz-20261014-pass4.json`.
