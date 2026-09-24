# US Core Inferno rescore — fhirdev — 2026-09-24

Hosted Inferno **FHIR API** only (no SMART) against `https://devfhir.vistaplex.org/fhir`, same nine synthetic DFNs:

`101090,101114,101115,101116,101120,101121,101119,101065,101077`

Plan: [USCORE_INFERNO_NEXT_PASS_PLAN.md](./USCORE_INFERNO_NEXT_PASS_PLAN.md)  
Prior baseline: [USCORE_INFERNO_RESCORE_2026-09-23.md](./USCORE_INFERNO_RESCORE_2026-09-23.md)

## Scorecards

| Suite | Pass | Fail | Error | Skip | vs 09-23 | Summary | Session |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| US Core **6.1.0** | 262 | 13 | 4 | 225 | +1 pass / −1 fail | [uscore-v610-fhirdev-20260924.md](../2026/scorecards/inferno/uscore-v610-fhirdev-20260924.md) | [9xwqWOCxP7x](https://inferno.healthit.gov/suites/us_core_v610/9xwqWOCxP7x) |
| US Core **7.0.0** | 260 | 16 | 4 | 296 | +7 pass / −7 fail | [uscore-v700-fhirdev-20260924.md](../2026/scorecards/inferno/uscore-v700-fhirdev-20260924.md) | [DQpAJA49qc](https://inferno.healthit.gov/suites/us_core_v700/DQpAJA49qc) |

JSON dumps sit beside the `.md` files in `2026/scorecards/inferno/`.

## What we fixed this pass (Codex → fhirdev22)

1. **CapabilityStatement.date** as FHIR dateTime **string** (was FileMan number → Inferno parse fail).
2. **ALTCAP richness**: `instantiates` US Core 6.1/7.0 server CapabilityStatements; `supportedProfile` + search params on 13 resources.
3. **Smoking Observations**: graph emit (`C0FHIRLG`) keeps LOINC `72166-2` as **social-history** + `us-core-smokingstatus` (no longer forced laboratory / quality-core-lab).
4. **Lab Observations**: dual-tag `us-core-observation-lab` ahead of quality-core lab profile (`C0FHIRL` / `C0FHIRLG`).
5. **Cache search**: patient and global search use **newest** cache CID (`NEWEST^C0FWCAC`) so stale sibling caches cannot return outdated Observation shapes.

Nine-patient caches rebuilt with `?dfn=&refresh=1` after deploy.

## Now passing that used to fail

| Theme | Suites |
| --- | --- |
| CapabilityStatement (date / instantiates / structure) | 6.1 + 7.0 |
| Smoking status validation + searches | 6.1 + 7.0 |
| Location name / address searches | **7.0** (five search tests) |

## Still failing

| Theme | Notes |
| --- | --- |
| **Unresolved quality-core profile URLs** | HbA1c / screening Observations still list `http://fhir.org/guides/onc/us-quality-core/...` as a second `meta.profile` — Inferno cannot resolve → lab / clinical-result / simple-observation validation |
| **Specimen** | type ValueSet + read from quality-core lab Observation reference |
| **body_weight category+date search** | new this run — triage next |
| **DiagnosticReport lab category search** | still **error** (harness / synthetichealth family) |
| **DAR** | unchanged data gap |

Skips for CareTeam, Coverage, pregnancy/occupation/pediatric Obs, BMI LOINC, etc. remain **export/data gaps**, not search bugs. Do not expand the cohort for those until builders emit the resources.

## Related

- Kit fit: [INFERNO_QA_TEST_KIT_FIT_2026-09-18.md](./INFERNO_QA_TEST_KIT_FIT_2026-09-18.md)
- Server changes: `VistA-FHIR-Server-Codex` (ALTCAP / C0FHIRLG / C0FHIRL / C0FWCAC) — commit with this rescore
