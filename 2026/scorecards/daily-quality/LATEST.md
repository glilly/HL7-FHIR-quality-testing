# Daily quality rotate — 2026-10-28 — `fhirdev`

**Verdict:** **PASS**  
**Base:** `https://devfhir.vistaplex.org`  
**Stamp (UTC):** `20261028T051553Z`  
**POPIDX:** populationIndexed=692, popidxDistinctCodes=962  
**CQL reeval:** skipped  

## Checks

| Status | Key | Detail |
|--------|-----|--------|
| PASS | `fhir-metadata` | HTTP 200 |
| PASS | `popidx` | populationIndexed=692 popidxDistinctCodes=962 |
| PASS | `c0x-presets` | 6 active measure presets present |
| PASS | `ipp-CMS165v14` | ippCount=52 |
| PASS | `ipp-CMS122v14` | ippCount=29 |
| PASS | `ipp-CMS130v14` | ippCount=56 |
| PASS | `ipp-CMS125v14` | ippCount=47 |
| PASS | `ipp-CMS138v14` | ippCount=77 |
| PASS | `ipp-CMS2v15` | ippCount=77 |
| PASS | `sum-CMS165v14` | 50/50/37/0 |
| PASS | `sum-CMS122v14` | 7/7/5/0 |
| PASS | `sum-CMS130v14` | 55/55/39/0 |
| PASS | `sum-CMS125v14` | 47/47/35/0 |
| PASS | `sum-CMS138v14` | 41/41/31/0 |
| PASS | `sum-CMS2v15` | 31/31/18/0 |
| PASS | `reeval-skipped` | QUALITY_REEVAL not requested for fhirdev |
| PASS | `json-101156` | strict Bundle parse OK |
| PASS | `json-101155` | strict Bundle parse OK |
| PASS | `json-101154` | strict Bundle parse OK |

## Measure table

| Measure | SPARQL ippCount | SUM IPP/DENOM/NUMER/DENEX |
|---------|-----------------|---------------------------|
| CMS165v14 | ippCount=52 | — |
| CMS122v14 | ippCount=29 | — |
| CMS130v14 | ippCount=56 | — |
| CMS125v14 | ippCount=47 | — |
| CMS138v14 | ippCount=77 | — |
| CMS2v15 | ippCount=77 | — |

## Reproduce

```bash
cd HL7-FHIR-quality-testing && ./scripts/daily-quality-rotate.sh fhirdev
```

JSON twin: `2026-10-28-fhirdev.json`
