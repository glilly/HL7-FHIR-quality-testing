# Daily quality rotate — 2026-10-06 — `rpms-candidate`

**Verdict:** **FAIL**  
**Base:** `http://127.0.0.1:9088`  
**Stamp (UTC):** `20261006T051841Z`  
**POPIDX:** populationIndexed=21, popidxDistinctCodes=0  
**CQL reeval:** skipped  

## Checks

| Status | Key | Detail |
|--------|-----|--------|
| PASS | `fhir-metadata` | HTTP 200 |
| FAIL | `popidx` | populationIndexed=21 popidxDistinctCodes=0 |
| PASS | `c0x-presets` | 6 active measure presets present |
| PASS | `ipp-CMS165v14` | ippCount=2 |
| PASS | `ipp-CMS122v14` | ippCount=3 |
| PASS | `ipp-CMS130v14` | ippCount=8 |
| PASS | `ipp-CMS125v14` | ippCount=5 |
| PASS | `ipp-CMS138v14` | ippCount=17 |
| PASS | `ipp-CMS2v15` | ippCount=17 |
| PASS | `sum-CMS165v14` | 19/16/15/0 |
| PASS | `sum-CMS122v14` | 2/2/2/0 |
| PASS | `sum-CMS130v14` | 13/9/1/0 |
| PASS | `sum-CMS125v14` | 3/3/1/0 |
| PASS | `sum-CMS138v14` | 26/26/2/0 |
| PASS | `sum-CMS2v15` | 13/13/0/0 |
| PASS | `reeval-skipped` | QUALITY_REEVAL not requested for rpms-candidate |
| PASS | `json-9` | strict Bundle parse OK |
| PASS | `json-12` | strict Bundle parse OK |
| PASS | `json-8` | strict Bundle parse OK |

## Measure table

| Measure | SPARQL ippCount | SUM IPP/DENOM/NUMER/DENEX |
|---------|-----------------|---------------------------|
| CMS165v14 | ippCount=2 | — |
| CMS122v14 | ippCount=3 | — |
| CMS130v14 | ippCount=8 | — |
| CMS125v14 | ippCount=5 | — |
| CMS138v14 | ippCount=17 | — |
| CMS2v15 | ippCount=17 | — |

## Reproduce

```bash
cd HL7-FHIR-quality-testing && ./scripts/daily-quality-rotate.sh rpms-candidate
```

JSON twin: `2026-10-06-rpms-candidate.json`
