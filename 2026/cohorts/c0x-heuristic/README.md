# C0X → CQL cohort expansion (2026-07-26)

Population SPARQL IPP presets on fhirdev (`/c0x`) discovered candidate DFNs; those with name-matched Synthea source bundles were re-evaluated with official `cqm-execution` CQL and merged into `SETPOP_MANIFEST.tsv`.

## Pipeline

1. `/c0x/cohort?measure=…` heuristic IPP lists → `IPP_SUMMARY.tsv`
2. Name-match DFN → Synthea FHIR bundle (Codex `/fhir?dfn=` exports do **not** yet CQL-pass; use raw Synthea)
3. `scripts/evaluate-cqm-manifest.js` + `scripts/c0x-ipp-to-setpop.py`
4. `scripts/fhirdev-apply-setpop.sh`

## CQL results (mapped Synthea)

| Measure | Evaluated | IPP | DENOM | NUMER |
|---------|-----------|-----|-------|-------|
| CMS165v14 | 20 | 16 | 16 | 15 |
| CMS122v14 | 4 | 2 | 2 | 0 |
| CMS130v14 | 13 | 9 | 9 | 1 |

Unmapped C0X-only DFNs (no Synthea file) kept as `heuristic-c0x` IPP=1 in SETPOP for discovery.

## UI

- C0X: https://devfhir.vistaplex.org/c0x
- Dashboards: https://devfhir.vistaplex.org/fhir-quality-dashboards
