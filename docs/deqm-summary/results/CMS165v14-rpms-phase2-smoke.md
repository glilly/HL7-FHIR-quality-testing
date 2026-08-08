# CMS165v14 RPMS lane — Phase 2 smoke evidence

Date: 2026-08-08

## Pipeline (round-trip, honest counts)

1. Selected-18 + showcase Synthea bundles loaded into
   `rpmsfhir.vistaplex.org` (`/addpatient?load=1`) → DFNs **1143–1161**
   (`2026/patients/rpmsfhir-ingest-selected18-20260808.tsv`).
2. Patient collection Bundles exported back **from rpmsfhir**
   (`GET https://rpmsfhir.vistaplex.org/fhir?dfn={dfn}`, 228–1,486 entries
   each) → `2026/cohorts/rpms/CMS165v14/bundles/`.
3. FHIR→QDM + `cqm-execution` CMS165v14 (37/37 VSAC-expanded value sets):
   `node scripts/evaluate-cqm-manifest.js CMS165v14
   --manifest 2026/cohorts/rpms/CMS165v14/eval-manifest.tsv
   --out-dir 2026/cohorts/rpms/CMS165v14/cql`
   (log `logs/rpms-cms165-cql-20260808.log`).

## Counts (n=19)

| IPP | DENOM | NUMER | DENEX | score |
|---:|---:|---:|---:|---:|
| 19 | 19 | 14 | 1 | 0.736842 |

Per-patient: `2026/cohorts/rpms/CMS165v14/cql/cql-results.tsv`.

Comparison vs devfhir lane (selected-18, 14/14/14/0): **NUMER=14 matches**;
IPP/DENOM are higher on the RPMS lane because the rpmsfhir collection
Bundle round-trips more of the source data (more qualifying
encounters/elements survive), and the cohort includes the showcase
patient (n=19 vs 18). DENEX=1 is DFN 1145. Do not average or merge the
two lanes; report each under its own reporter Organization.

## Phase 2 gates

- Report: `prototypes/rpms/CMS165v14-rpms-summary-deqm.json`
  (reporter `Organization/vistaplex-rpms-demo`), built by
  `scripts/build-deqm-summary.py --reporter rpms`.
- Structural check: OK (`scripts/check-deqm-summary.py`).
- Inferno FHIR Validator + DEQM 5.0.0 (`DISABLE_TX=true`): severity
  `{error: 1, warning: 3, information: 4}`; the single error is the known
  IG `supplementalData` slice noise (also on IG golden examples) →
  **0 actionable errors**.
- `deqm-test-server` POST: transaction-response **201 Created** for
  `Organization/vistaplex-rpms-demo` and
  `MeasureReport/CMS165v14-rpms-summary-deqm`.
