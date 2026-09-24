# US Core Inferno rescore — fhirdev — 2026-09-23

Hosted Inferno **FHIR API** only (no SMART) against `https://devfhir.vistaplex.org/fhir`, nine synthetic DFNs:

`101090,101114,101115,101116,101120,101121,101119,101065,101077`

## Scorecards

| Suite | Pass | Fail | Error | Skip | Summary | Session |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| US Core **6.1.0** | 261 | 14 | 4 | 225 | [uscore-v610-fhirdev-20260923.md](../2026/scorecards/inferno/uscore-v610-fhirdev-20260923.md) | [79Xp8I6E6MH](https://inferno.healthit.gov/suites/us_core_v610/79Xp8I6E6MH) |
| US Core **7.0.0** | 253 | 23 | 4 | 296 | [uscore-v700-fhirdev-20260923.md](../2026/scorecards/inferno/uscore-v700-fhirdev-20260923.md) | [5HDVWXegFQw](https://inferno.healthit.gov/suites/us_core_v700/5HDVWXegFQw) |

JSON dumps sit beside the `.md` files in `2026/scorecards/inferno/`.

Baseline before this fix pass (same cohort, same day earlier): **6.1.0** about **234 pass / 38 fail / 5 error**, dominated by CapabilityStatement `OperationOutcome`, patient-less search `OperationOutcome`s, and wrong-field date/class/location filters.

## What we fixed (Codex → fhirdev22)

Committed in **VistA-FHIR-Server-Codex** as `9f32c0a`:

1. **`GET /fhir/metadata`** → `ALTCAP^C0FHIR` CapabilityStatement (`fhirVersion` 4.0.1), not an OperationOutcome.
2. **Patient-less search** for Patient / Practitioner / Organization / Location (and `_id` / `identifier`) by unioning cache indexes.
3. **Typed search filters**: `onset-date`, `asserted-date`, `abatement-date`, `authoredon`, Encounter `class` / `location`, DocumentReference `period`; Organization/Location address tokens.
4. **Profile builders**: MedicationRequest drop display-only coding; ServiceRequest SNOMED Imaging + `urn:va:cpt`; Specimen omit invalid FileMan dates; Observation codes forced to strings; smoking LOINC display corrected.

Nine-patient caches were rebuilt with `refresh=1` after deploy.

## Now passing that used to fail

- CapabilityStatement `fhirVersion` (no longer OO)
- Patient / Practitioner / Organization name, identifier, address searches
- Condition onset / asserted / abatement date searches
- MedicationRequest `authoredon` search
- Encounter `class` search
- MedicationRequest, ServiceRequest, Specimen profile validation

## Still failing (next pass)

| Theme | Notes |
| --- | --- |
| **CapabilityStatement richness** | Thin `ALTCAP` — missing US Core `instantiates` and profile support list |
| **Observation validation** | Mostly Synthea/graph resources: wrong LOINC displays, missing survey / social-history category slices (lab, simple, clinical-result, smoking) |
| **DataAbsentReason** | No DAR extension / code system in these charts (same family as other skips) |
| **Location (7.0)** | Earlier OO fixed in code after the scored run; re-run Location group to confirm |
| **DiagnosticReport client error** | Inferno `synthetichealth` constant — harness-side, not our Bundle |

Skips for CareTeam, CarePlan, pregnancy/occupation/pediatric observations, Provenance, etc. remain **data gaps**, not search bugs.

## Next

- Done: [USCORE_INFERNO_RESCORE_2026-09-24.md](./USCORE_INFERNO_RESCORE_2026-09-24.md) · plan [USCORE_INFERNO_NEXT_PASS_PLAN.md](./USCORE_INFERNO_NEXT_PASS_PLAN.md)

## Related

- Kit fit / which Inferno suites matter: [INFERNO_QA_TEST_KIT_FIT_2026-09-18.md](./INFERNO_QA_TEST_KIT_FIT_2026-09-18.md)
- Server changes: `VistA-FHIR-Server-Codex` commit `9f32c0a`
