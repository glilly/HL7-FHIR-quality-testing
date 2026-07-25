# Recovery + overnight follow-through Report (20260725)

Generated: 2026-07-25T11:35:00-04:00

## Goal

Recover from the failed 2026-07-23 overnight marathon: restore VSAC expansions, finish CQL for the September shortlist, capture Inferno scorecards (hosted + vendev15), and publish CMS165/CMS122 aggregates to `/fhir-quality-dashboards`.

## What failed overnight (2026-07-23)

- VSAC DNS (`EAI_AGAIN`) → empty expansions; CQL skipped.
- Hosted Inferno briefly unreachable.
- Report heredoc bug emptied `OVERNIGHT_MARATHON_REPORT_LATEST.md`.
- Empty `value_sets.json` overwrite of a good CMS165 cache (since guarded).

See also: `docs/OVERNIGHT_MARATHON_REPORT_20260723-220217.md` (failed-run artifact).

## VSAC expansions (after rebuild)

| Measure | Expanded |
|---------|----------|
| CMS165v14 | 37/37 |
| CMS122v14 | 30/30 |
| CMS138v14 | 36/36 |
| CMS2v15 | 21/21 |
| CMS130v14 | 35/35 |
| CMS125v14 | 36/36 |
| CMS131v14 | 33/33 |
| CMS68v15 | 10/10 |
| CMS22v14 | 24/24 |

(`value_sets.json` stays local / gitignored.)

## CQL selected-18 (cqm-execution)

| Measure | n | IPP | DENOM | NUMER | DENEX |
|---------|--:|----:|------:|------:|------:|
| CMS165v14 | 18 | 14 | 14 | 14 | 0 |
| CMS122v14 | 18 | 5 | 5 | 0 | 0 |
| CMS138v14 | 18 | 1 | 0 | 0 | 0 |
| CMS2v15 | 18 | 6 | 6 | 0 | 0 |
| CMS130v14 | 18 | 9 | 9 | 0 | 0 |
| CMS125v14 | 9 | 0 | 0 | 0 | 0 |
| CMS131v14 | 18 | 13 | 13 | 0 | 0 |
| CMS68v15 | 18 | 6 | 6 | 0 | 0 |
| CMS22v14 | 18 | 6 | 6 | 0 | 2 |

Summaries: `2026/cohorts/*/reports/cqm-execution-summary.json`.

## Quality dashboards (vehu10)

Published into `^C0FQUAL` (seed v3):

- **CMS165v14** — 14 / 14 / 14 (n=18), `official-cql`
- **CMS122v14** — 5 / 5 / 0 (n=18), `official-cql`

URLs: `http://127.0.0.1:9085/fhir-quality-dashboards`, gateway `http://localhost:5177/fhir-quality-dashboards`.

## Hosted Inferno (inferno.healthit.gov)

| Scorecard | pass | fail | skip | Session |
|-----------|-----:|-----:|-----:|---------|
| recover-altfhir-ien482 | 443 | 0 | 55 | [41TuYXN0w73](https://inferno.healthit.gov/suites/us_quality_core_v050/41TuYXN0w73) |
| recover-fhir-dfn101090 | 135 | 5 | 358 | [6mWW9A4q8I5](https://inferno.healthit.gov/suites/us_quality_core_v050/6mWW9A4q8I5) |
| recover-altfhir-cms165-selected18 | 89 | 111 | 298 | [lLtnzfUFZJ7](https://inferno.healthit.gov/suites/us_quality_core_v050/lLtnzfUFZJ7) |

## vendev15 Inferno (`http://vendev15.vistaplex.org:8088/`)

FHIR URL from Inferno: `http://host.docker.internal:5178/fhir`.

| Scorecard | pass | fail | skip | error | Session |
|-----------|-----:|-----:|-----:|------:|---------|
| vendev15-fhir-dfn101090 | 218 | 0 | 829 | 128 | [dsRvJ14T7qt](http://vendev15.vistaplex.org:8088/us_quality_core_v050/dsRvJ14T7qt) |
| vendev15-fhir-dfn101076 | 133 | 0 | 797 | 90 | [36MBUy4QqpK](http://vendev15.vistaplex.org:8088/us_quality_core_v050/36MBUy4QqpK) |
| CMS165 selected-18 | — | — | — | — | **Failed** mid-run: Inferno API HTTP 500 (likely validator/memory under concurrent load) |

## Script hardening (this recovery)

- `build-cqm-package.js` — refuse empty VSAC overwrite when expansions already exist
- `overnight-marathon.sh` — quoted report heredoc
- `evaluate-cqm.js` — pass value-set **array** to cqm-execution
- `inferno-run.py` — `--api` / `--ui-base` for vendev15 vs hosted

## Logs

- `logs/vsac-rebuild-20260724-233339.log`
- `logs/cqm-eval-all-20260724-234249.log`
- `logs/recover-cms165-122-20260724-233137.log`
- `logs/vendev15-inferno-101090.log`
- `logs/vendev15-inferno-101076.log`
- `logs/vendev15-inferno-cms165-selected18.log`

## Next

1. Retry vendev15 CMS165 selected-18 **alone**.
2. Fix enrich→load (HTTP 000s) so showcase DFNs land on graph/fhirdev.
3. Map selected-18 → DFNs + `SETPOP^C0FQUAL` for patient rows on dashboards.
4. Activate next shortlist measures when showcase + Inferno look good.
