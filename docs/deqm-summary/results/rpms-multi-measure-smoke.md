# RPMS lane multi-measure — Phase 2/3 smoke evidence

Date: 2026-08-08

Same round-trip cohort and pipeline as
`CMS165v14-rpms-phase2-smoke.md` (rpmsfhir exports, DFNs 1143–1161,
n=19): FHIR→QDM + `cqm-execution` per measure via
`evaluate-cqm-manifest.js --out-dir 2026/cohorts/rpms/{CMS}/cql`,
reports from `build-deqm-summary.py --reporter rpms`.

## Counts (n=19, hierarchy-gated) vs devfhir selected-18 lane

Counts corrected 2026-08-08 (later same day): `evaluate-cqm-manifest.js`
now enforces population hierarchy (DENOM ⊆ IPP, DENEX ⊆ DENOM,
NUMER ⊆ DENOM−DENEX) instead of counting raw CQL statement results.
The devfhir selected-18 raw-bundle counts (14/14/14/0) were re-verified
under gating and are unchanged.

| Measure | RPMS IPP/DENOM/NUMER/DENEX | devfhir (n=18) | Note |
|---|---|---|---|
| CMS165v14 | 19/19/13/1 | 14/14/14/0 | 13 of devfhir's 14 NUMER patients match; the 14th (DFN 1145) is DENEX on the RPMS round-trip |
| CMS122v14 | 10/10/4/0 | 5/5/0/0 | Round-trip A1c depth reaches NUMER |
| CMS130v14 | 15/15/1/0 | 9/9/0/0 | One colonoscopy/FIT path survives |
| CMS2v15 | 19/19/0/0 | 6/6/0/0 | Honest zero NUMER both lanes |
| CMS22v14 | 19/19/0/19 | 6/6/0/2 | DENEX=19 coherent: cohort selected for CMS165 (hypertension) is excluded from BP screening |
| CMS138v14 | 19/19/19/0 | n/a (setpop cohort differs) | Tobacco screening universal in Synthea data; bridge slice carries it through the round-trip |
| CMS125v14 | 11/11/0/0 | n/a (setpop cohort differs) | Honest zero: mammography evidence does not survive the round-trip |

Interpretation: the rpmsfhir patient collection Bundle round-trips more
source data than the devfhir lane, so IPP/DENOM (and some NUMER) are
higher. These are honest per-lane counts; lanes are never merged and
each reports under its own reporter Organization.

Counts TSV: `docs/deqm-summary/rpms-roundtrip-counts.tsv`
Eval log: `logs/rpms-multi-cql-20260808.log`

## Phase 2 gates (all four measures, 2026-08-08)

- Inferno FHIR Validator + DEQM 5.0.0 (`DISABLE_TX=true`): each report
  `{error: 1, warning: 3, information: 4}` where the single error is the
  known IG `supplementalData` slice noise → **0 actionable errors**.
- `deqm-test-server` POST: **201 Created** for
  `MeasureReport/{CMS}-rpms-summary-deqm` (CMS122v14, CMS130v14,
  CMS2v15, CMS22v14) under `Organization/vistaplex-rpms-demo`.
- Smoke log: `logs/rpms-multi-smoke-20260808.log`
