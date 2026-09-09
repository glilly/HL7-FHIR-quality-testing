# DEQM Individual + Subject-List scenarios — 2026-09-09

Sprint Day 3 (FOUR_DAY_TOKEN_SPRINT). Completes the CMS-track reporting
triangle: Summary (done earlier), **Individual**, and **Subject-List**
MeasureReports, all validated and accepted by the reference receiver.

## What ran

- Builder: `scripts/build-deqm-subject-list.py` (new) — reads
  `2026/cohorts/SETPOP_MANIFEST.tsv`, emits per measure:
  - `{CMS}-subjectlist-deqm.json` — DEQM STU5
    `subjectlist-measurereport-deqm` (type `subject-list`); one contained
    `List` (profile `indv-measurereport-list`) per population whose
    entries reference the per-patient individual MeasureReports; empty
    populations carry an `emptyReason` List (profile requires
    `subjectResults` 1..1, and `entry: []` is invalid FHIR).
  - `Bundle-{CMS}-subjectlist-transaction.json` — subject-list +
    reporter Organization + every individual MeasureReport
    (`indv-measurereport-deqm`, same shapes as
    `build-deqm-individual.py`).
- Receiver: `projecttacoma/deqm-test-server` at `127.0.0.1:3000`
  (mongo + redis + node via its docker-compose).
- Validator: Inferno `fhir-validator-service` at `:4567` with
  `hl7.fhir.us.davinci-deqm#5.0.0` loaded, `DISABLE_TX=true`.

## Results

| Measure | Subjects | IPP / DENOM / NUMER / DENEX | Validator (subject-list profile) | Receiver |
|---|---|---|---|---|
| CMS165v14 | 23 | 19 / 16 / 16 / 0 | 0 actionable errors (1 known `supplementalData` slice noise, also on IG golden examples) | transaction accepted, 25/25 entries 201/200 |
| CMS122v14 | 9 | 5 / 4 / 1 / 0 | 0 actionable errors (same single known-noise item) | transaction accepted, 11/11 entries 201/200 |

Individual-scenario read-back proof: `GET
/4_0_1/MeasureReport/CMS165v14-Patient-101095-deqm` returns type
`individual`, subject `Patient/101095`, populations 1/1/1/0 — matching
the SETPOP manifest row (official-cql evidence). Subject-list read-back
returns the report with all four contained population Lists intact.

## Fixes made along the way

1. `entry: []` on the empty denominator-exclusion List — invalid empty
   array per validator; replaced with an entry-less List carrying
   `emptyReason` (profile still gets its required `subjectResults`).
2. Upstream `deqm-test-server` Dockerfile fails to build on its
   `dhi.io/node:24-dev` base (`npm install --global npm@'<11.12.0'`
   hits EEXIST). Local patch: add `--force` — worth a PR upstream.

## Rerun crib

    python3 scripts/build-deqm-subject-list.py --cms CMS165v14
    # validate (profile=subjectlist-measurereport-deqm) against :4567
    # POST docs/deqm-summary/prototypes/Bundle-{CMS}-subjectlist-transaction.json to :3000/4_0_1
