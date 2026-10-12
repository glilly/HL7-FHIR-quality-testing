# Daily quality rotate — 2026-10-12 — `fhirdev`

**Verdict:** **PASS**  
**Base:** `https://devfhir.vistaplex.org`  
**Stamp (UTC):** `20261012T175821Z`  
**POPIDX:** populationIndexed=682, popidxDistinctCodes=958  
**CQL reeval:** ran  

## Checks

| Status | Key | Detail |
|--------|-----|--------|
| PASS | `fhir-metadata` | HTTP 200 |
| PASS | `popidx` | populationIndexed=682 popidxDistinctCodes=958 |
| PASS | `c0x-presets` | 6 active measure presets present |
| PASS | `ipp-CMS165v14` | ippCount=49 |
| PASS | `ipp-CMS122v14` | ippCount=27 |
| PASS | `ipp-CMS130v14` | ippCount=46 |
| PASS | `ipp-CMS125v14` | ippCount=37 |
| PASS | `ipp-CMS138v14` | ippCount=67 |
| PASS | `ipp-CMS2v15` | ippCount=67 |
| PASS | `sum-CMS165v14` | 46/46/37/0 |
| PASS | `sum-CMS122v14` | 5/5/5/0 |
| PASS | `sum-CMS130v14` | 45/45/29/0 |
| PASS | `sum-CMS125v14` | 37/37/35/0 |
| PASS | `sum-CMS138v14` | 31/31/29/0 |
| PASS | `sum-CMS2v15` | 20/20/17/0 |
| PASS | `reeval-CMS165v14` | 47/47/37/0 status=done |
| PASS | `reeval-CMS122v14` | 5/5/5/0 status=done |
| PASS | `reeval-CMS130v14` | 45/45/29/0 status=done |
| PASS | `reeval-CMS125v14` | 37/37/35/0 status=done |
| PASS | `reeval-CMS138v14` | 31/31/29/0 status=done |
| PASS | `reeval-CMS2v15` | 21/21/18/0 status=done |
| PASS | `json-101152` | strict Bundle parse OK |
| PASS | `json-101151` | strict Bundle parse OK |
| PASS | `json-101149` | strict Bundle parse OK |

## Measure table

| Measure | SPARQL ippCount | SUM IPP/DENOM/NUMER/DENEX |
|---------|-----------------|---------------------------|
| CMS165v14 | ippCount=49 | — |
| CMS122v14 | ippCount=27 | — |
| CMS130v14 | ippCount=46 | — |
| CMS125v14 | ippCount=37 | — |
| CMS138v14 | ippCount=67 | — |
| CMS2v15 | ippCount=67 | — |

## Reproduce

```bash
cd HL7-FHIR-quality-testing && ./scripts/daily-quality-rotate.sh fhirdev
```

JSON twin: `2026-10-12-fhirdev.json`
