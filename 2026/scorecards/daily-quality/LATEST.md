# Daily quality rotate — 2026-10-29 — `rpmsfhir`

**Verdict:** **PASS**  
**Base:** `https://rpmsfhir.vistaplex.org`  
**Stamp (UTC):** `20261029T051632Z`  
**POPIDX:** populationIndexed=1159, popidxDistinctCodes=1205  
**CQL reeval:** skipped  

## Checks

| Status | Key | Detail |
|--------|-----|--------|
| PASS | `fhir-metadata` | HTTP 200 |
| PASS | `popidx` | populationIndexed=1159 popidxDistinctCodes=1205 |
| PASS | `c0x-presets` | 6 active measure presets present |
| PASS | `ipp-CMS165v14` | ippCount=97 |
| PASS | `ipp-CMS122v14` | ippCount=24 |
| PASS | `ipp-CMS130v14` | ippCount=172 |
| PASS | `ipp-CMS125v14` | ippCount=89 |
| PASS | `ipp-CMS138v14` | ippCount=200 |
| PASS | `ipp-CMS2v15` | ippCount=200 |
| PASS | `sum-CMS165v14` | 36/36/22/5 |
| PASS | `sum-CMS122v14` | 42/42/10/0 |
| PASS | `sum-CMS130v14` | 7/7/7/0 |
| PASS | `sum-CMS125v14` | 3/3/3/0 |
| PASS | `sum-CMS138v14` | 16/16/13/0 |
| PASS | `sum-CMS2v15` | 12/12/10/0 |
| PASS | `reeval-skipped` | QUALITY_REEVAL not requested for rpmsfhir |
| PASS | `json-498` | strict Bundle parse OK |
| PASS | `json-497` | strict Bundle parse OK |
| PASS | `json-489` | strict Bundle parse OK |

## Measure table

| Measure | SPARQL ippCount | SUM IPP/DENOM/NUMER/DENEX |
|---------|-----------------|---------------------------|
| CMS165v14 | ippCount=97 | — |
| CMS122v14 | ippCount=24 | — |
| CMS130v14 | ippCount=172 | — |
| CMS125v14 | ippCount=89 | — |
| CMS138v14 | ippCount=200 | — |
| CMS2v15 | ippCount=200 | — |

## Reproduce

```bash
cd HL7-FHIR-quality-testing && ./scripts/daily-quality-rotate.sh rpmsfhir
```

JSON twin: `2026-10-29-rpmsfhir.json`
