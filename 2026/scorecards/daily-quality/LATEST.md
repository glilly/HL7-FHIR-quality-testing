# Daily quality rotate — 2026-10-14 — `wvehr`

**Verdict:** **PASS**  
**Base:** `https://fhir.vistaplex.org`  
**Stamp (UTC):** `20261014T051948Z`  
**POPIDX:** populationIndexed=14, popidxDistinctCodes=521  
**CQL reeval:** skipped  

## Checks

| Status | Key | Detail |
|--------|-----|--------|
| PASS | `fhir-metadata` | HTTP 200 |
| PASS | `popidx` | populationIndexed=14 popidxDistinctCodes=521 |
| PASS | `c0x-presets` | 6 active measure presets present |
| PASS | `ipp-CMS165v14` | ippCount=10 |
| PASS | `ipp-CMS122v14` | ippCount=1 |
| PASS | `ipp-CMS130v14` | ippCount=7 |
| PASS | `ipp-CMS125v14` | ippCount=6 |
| PASS | `ipp-CMS138v14` | ippCount=9 |
| PASS | `ipp-CMS2v15` | ippCount=9 |
| PASS | `sum-CMS165v14` | 5/5/5/0 |
| PASS | `sum-CMS122v14` | 3/3/1/0 |
| PASS | `sum-CMS130v14` | 9/9/2/0 |
| PASS | `sum-CMS125v14` | 6/6/3/0 |
| PASS | `sum-CMS138v14` | 12/12/9/0 |
| PASS | `sum-CMS2v15` | 13/13/12/0 |
| PASS | `reeval-skipped` | QUALITY_REEVAL not requested for wvehr |
| PASS | `json-3` | strict Bundle parse OK |
| PASS | `json-5` | strict Bundle parse OK |
| PASS | `json-6` | strict Bundle parse OK |

## Measure table

| Measure | SPARQL ippCount | SUM IPP/DENOM/NUMER/DENEX |
|---------|-----------------|---------------------------|
| CMS165v14 | ippCount=10 | — |
| CMS122v14 | ippCount=1 | — |
| CMS130v14 | ippCount=7 | — |
| CMS125v14 | ippCount=6 | — |
| CMS138v14 | ippCount=9 | — |
| CMS2v15 | ippCount=9 | — |

## Reproduce

```bash
cd HL7-FHIR-quality-testing && ./scripts/daily-quality-rotate.sh wvehr
```

JSON twin: `2026-10-14-wvehr.json`
