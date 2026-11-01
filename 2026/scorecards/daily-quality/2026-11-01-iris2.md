# Daily quality rotate — 2026-11-01 — `iris2`

**Verdict:** **PASS**  
**Base:** `https://iris2.vistaplex.org`  
**Stamp (UTC):** `20261101T071635Z`  
**POPIDX:** populationIndexed=223, popidxDistinctCodes=1010  
**CQL reeval:** ran  

## Checks

| Status | Key | Detail |
|--------|-----|--------|
| PASS | `fhir-metadata` | HTTP 200 |
| PASS | `popidx` | populationIndexed=223 popidxDistinctCodes=1010 |
| PASS | `c0x-presets` | 6 active measure presets present |
| PASS | `ipp-CMS165v14` | ippCount=55 |
| PASS | `ipp-CMS122v14` | ippCount=31 |
| PASS | `ipp-CMS130v14` | ippCount=101 |
| PASS | `ipp-CMS125v14` | ippCount=76 |
| PASS | `ipp-CMS138v14` | ippCount=169 |
| PASS | `ipp-CMS2v15` | ippCount=169 |
| PASS | `sum-CMS165v14` | 58/3/2/1 |
| PASS | `sum-CMS122v14` | 32/1/1/0 |
| PASS | `sum-CMS130v14` | 103/2/2/0 |
| PASS | `sum-CMS125v14` | 77/1/1/0 |
| PASS | `sum-CMS138v14` | 172/3/3/0 |
| PASS | `sum-CMS2v15` | 173/4/4/0 |
| PASS | `reeval-CMS165v14` | 58/3/2/1 status=running |
| PASS | `reeval-CMS122v14` | 32/1/1/0 status=running |
| PASS | `reeval-CMS130v14` | 103/2/2/0 status=running |
| PASS | `reeval-CMS125v14` | 77/1/1/0 status=running |
| PASS | `reeval-CMS138v14` | 172/3/3/0 status=running |
| PASS | `reeval-CMS2v15` | 173/4/4/0 status=running |
| PASS | `json-222` | strict Bundle parse OK |
| PASS | `json-221` | strict Bundle parse OK |
| PASS | `json-215` | strict Bundle parse OK |

## Measure table

| Measure | SPARQL ippCount | SUM IPP/DENOM/NUMER/DENEX |
|---------|-----------------|---------------------------|
| CMS165v14 | ippCount=55 | — |
| CMS122v14 | ippCount=31 | — |
| CMS130v14 | ippCount=101 | — |
| CMS125v14 | ippCount=76 | — |
| CMS138v14 | ippCount=169 | — |
| CMS2v15 | ippCount=169 | — |

## Reproduce

```bash
cd HL7-FHIR-quality-testing && ./scripts/daily-quality-rotate.sh iris2
```

JSON twin: `2026-11-01-iris2.json`
