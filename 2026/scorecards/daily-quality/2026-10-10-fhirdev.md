# Daily quality rotate — 2026-10-10 — `fhirdev`

**Verdict:** **FAIL**  
**Base:** `https://devfhir.vistaplex.org`  
**Stamp (UTC):** `20261010T053127Z`  
**POPIDX:** populationIndexed=0, popidxDistinctCodes=0  
**CQL reeval:** skipped  

## Checks

| Status | Key | Detail |
|--------|-----|--------|
| FAIL | `fhir-metadata` | HTTP 000000 |
| FAIL | `popidx` | HTTP 000000 |
| FAIL | `c0x-presets` | HTTP 000000 or missing presets |
| FAIL | `ipp-CMS165v14` | HTTP 000000 |
| FAIL | `ipp-CMS122v14` | HTTP 000000 |
| FAIL | `ipp-CMS130v14` | HTTP 000000 |
| FAIL | `ipp-CMS125v14` | HTTP 000000 |
| FAIL | `ipp-CMS138v14` | HTTP 000000 |
| FAIL | `ipp-CMS2v15` | HTTP 000000 |
| FAIL | `sum-CMS165v14` | dashboard HTTP 000000 |
| FAIL | `sum-CMS122v14` | dashboard HTTP 000000 |
| FAIL | `sum-CMS130v14` | dashboard HTTP 000000 |
| FAIL | `sum-CMS125v14` | dashboard HTTP 000000 |
| FAIL | `sum-CMS138v14` | dashboard HTTP 000000 |
| FAIL | `sum-CMS2v15` | dashboard HTTP 000000 |
| PASS | `reeval-skipped` | QUALITY_REEVAL not requested for fhirdev |
| FAIL | `json-parse` | no sample DFNs |

## Measure table

| Measure | SPARQL ippCount | SUM IPP/DENOM/NUMER/DENEX |
|---------|-----------------|---------------------------|
| CMS165v14 | HTTP 000000 | — |
| CMS122v14 | HTTP 000000 | — |
| CMS130v14 | HTTP 000000 | — |
| CMS125v14 | HTTP 000000 | — |
| CMS138v14 | HTTP 000000 | — |
| CMS2v15 | HTTP 000000 | — |

## Reproduce

```bash
cd HL7-FHIR-quality-testing && ./scripts/daily-quality-rotate.sh fhirdev
```

JSON twin: `2026-10-10-fhirdev.json`
