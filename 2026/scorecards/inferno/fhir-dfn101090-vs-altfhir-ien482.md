# DFN 101090 `/fhir` vs IEN 482 `/altfhir`

- Source graph IEN: `482`
- VistA DFN: `101090`
- `/altfhir` baseline: `https://inferno.healthit.gov/suites/us_quality_core_v050/dHSqcAyBTrh`
- `/fhir` round-trip: `https://inferno.healthit.gov/suites/us_quality_core_v050/bM8KKB31fM0`
- `/fhir` after getter alignment: `https://inferno.healthit.gov/suites/us_quality_core_v050/aGzCC7IG17c`

## Result Counts

| Endpoint | Patient ID | Pass | Fail | Skip |
| --- | --- | ---: | ---: | ---: |
| `/altfhir` | `482` | 447 | 0 | 51 |
| `/fhir` | `101090` | 106 | 23 | 369 |
| `/fhir` after getter alignment | `101090` | 129 | 0 | 369 |

## Alignment Iterations

| Run | Pass | Fail | Skip |
| --- | ---: | ---: | ---: |
| Baseline `/fhir` round-trip | 106 | 23 | 369 |
| Vital getter fix | 122 | 11 | 365 |
| Pulse oximetry coding fix | 123 | 9 | 366 |
| DocumentReference getter fix | 126 | 7 | 365 |
| Immunization CVX display fix | 128 | 5 | 365 |
| Condition code-system fix | 129 | 0 | 369 |

## Live Smoke Checks

- `GET /fhir/Patient/101090`: single Patient resource.
- `GET /fhir/Patient?_id=101090`: one-entry searchset Bundle.
- `POST /fhir/Patient/_search` with `_id=101090`: one-entry searchset Bundle.
- `GET /fhir/Observation?patient=101090&_count=5`: five Observations.
- `GET /fhir/Condition?patient=101090`: six Conditions.
- `GET /fhir/AllergyIntolerance?patient=101090`: one AllergyIntolerance.

## Main Round-Trip Findings

- `/altfhir` proves the source IEN 482 bundle can satisfy hosted US Quality Core with zero failures after graph-source search/read fixes.
- `/fhir` confirms the same patient is loaded and reachable in VistA, but the round-trip data surface is much smaller.
- Many `/altfhir` active groups become `/fhir` skips because the VistA loader/server does not currently round-trip those resource families or search shapes from VistA.
- The original `/fhir` failures were mostly profile validation failures for resources that do exist, not route failures.
- Getter-side alignment cleared all hosted US Quality Core failures for the loaded VistA patient surface represented by DFN `101090`.

## Fixed `/fhir` Failure Themes

- Vitals now emit US Core profiles, UCUM `system`/`code`, BP component quantities, and no BP top-level `valueString`.
- Pulse oximetry now emits the required oxygen saturation LOINC coding in addition to the US Core pulse-ox code.
- DocumentReference now emits a US Core profile, LOINC note type, and clinical-note category.
- Immunization now normalizes CVX `197` display to the validator-accepted string.
- Problem-list Conditions now avoid labeling ICD-10-CM codes as SNOMED.

## Remaining Practical Targets

1. Decide which skipped `/altfhir` resource families should be worth VistA loader/getter round-trip support for September.
2. Prioritize high-value resource families whose data can naturally fit VistA/RPMS without fragile synthetic-only shims.
3. Continue using `/altfhir` as the source-truth validator and `/fhir` as the round-trip loss detector.
