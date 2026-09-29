# Daily quality rotate — evidence

Produced by `scripts/daily-quality-rotate.sh` in this repo.

| File | Meaning |
|------|---------|
| `YYYY-MM-DD-<host>.md` | Human report (PASS/FAIL table + measure SUM) |
| `YYYY-MM-DD-<host>.json` | Machine twin (`daily-quality-rotate/v1`) |
| `LATEST.md` | Copy of the most recent run’s markdown |

Host rotation (UTC day-of-year `% 6`):
`showfhir` → `fhirdev` → `vehu10` → `rpms-candidate` → `rpmsfhir` → `wvehr`.

Default reeval (`QUALITY_REEVAL=auto`): cds1 CQL reeval only on
`showfhir`, `vehu10`, `rpms-candidate`. Public shared lanes stay read-only unless
`QUALITY_REEVAL=1`.
