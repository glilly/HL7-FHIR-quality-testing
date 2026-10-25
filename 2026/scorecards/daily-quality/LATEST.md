# Daily quality rotate — 2026-10-25 — `showfhir`

**Verdict:** **FAIL**  
**Base:** `https://showfhir.vistaplex.org`  
**Stamp (UTC):** `20261025T030721Z`  
**POPIDX:** populationIndexed=217, popidxDistinctCodes=1143  
**CQL reeval:** ran  

## Checks

| Status | Key | Detail |
|--------|-----|--------|
| PASS | `fhir-metadata` | HTTP 200 |
| PASS | `popidx` | populationIndexed=217 popidxDistinctCodes=1143 |
| PASS | `c0x-presets` | 6 active measure presets present |
| PASS | `ipp-CMS165v14` | ippCount=62 |
| PASS | `ipp-CMS122v14` | ippCount=33 |
| PASS | `ipp-CMS130v14` | ippCount=110 |
| PASS | `ipp-CMS125v14` | ippCount=82 |
| PASS | `ipp-CMS138v14` | ippCount=194 |
| PASS | `ipp-CMS2v15` | ippCount=194 |
| PASS | `sum-CMS165v14` | 19/16/15/0 |
| PASS | `sum-CMS122v14` | 5/4/0/0 |
| PASS | `sum-CMS130v14` | 13/9/1/0 |
| PASS | `sum-CMS125v14` | 0/0/0/0 |
| PASS | `sum-CMS138v14` | 26/26/2/0 |
| PASS | `sum-CMS2v15` | 6/6/0/0 |
| FAIL | `reeval-CMS165v14` | accept HTTP 400 |
| FAIL | `reeval-CMS122v14` | accept HTTP 400 |
| FAIL | `reeval-CMS130v14` | accept HTTP 400 |
| FAIL | `reeval-CMS125v14` | accept HTTP 400 |
| FAIL | `reeval-CMS138v14` | accept HTTP 400 |
| FAIL | `reeval-CMS2v15` | accept HTTP 400 |
| PASS | `json-101284` | strict Bundle parse OK |
| PASS | `json-101283` | strict Bundle parse OK |
| PASS | `json-101282` | strict Bundle parse OK |

## Measure table

| Measure | SPARQL ippCount | SUM IPP/DENOM/NUMER/DENEX |
|---------|-----------------|---------------------------|
| CMS165v14 | ippCount=62 | — |
| CMS122v14 | ippCount=33 | — |
| CMS130v14 | ippCount=110 | — |
| CMS125v14 | ippCount=82 | — |
| CMS138v14 | ippCount=194 | — |
| CMS2v15 | ippCount=194 | — |

## Reproduce

```bash
cd HL7-FHIR-quality-testing && ./scripts/daily-quality-rotate.sh showfhir
```

JSON twin: `2026-10-25-showfhir.json`
