# fhirdev (DevFHIR) coding-gap scan — 2026-09-24

**Host:** `fhirdev` via https://devfhir.vistaplex.org  
**Cohort:** union of active-measure dashboard POP DFNs (**44** unique)  
**Method:** `GET /fhir?dfn=N&refresh=1`, classify Conditions/Observations/Procedures against measure concept keywords + known good codes. Heuristic — not VSAC-complete.  
**Machine JSON:** [CODING_GAP_SCAN_FHIRDEV_2026-09-24.json](./CODING_GAP_SCAN_FHIRDEV_2026-09-24.json)

## Live CQL / dashboard SETSUM (same day)

| Measure | IPP | DENOM | NUMER | DENEX | Rate note |
|---------|----:|------:|------:|------:|-----------|
| CMS165v14 | 21 | 4 | 1 | 0 | 25% of DENOM; IPP≫DENOM |
| CMS122v14 | 5 | 5 | 5 | 0 | Fully met on curated POP |
| CMS125v14 | 18 | 18 | 10 | 0 | 55.6%; 8 DENOM miss NUMER |
| CMS130v14 | 13 | 9 | 1 | 0 | 11.1%; colo NUMER thin |
| CMS138v14 | 28 | 28 | 6 | 0 | 21.4%; screen ok, cessation thin |
| CMS2v15 | 21 | 21 | 0 | 0 | 0% — Assessment/QDM bridge gap |

R69 Condition rows (any narrative, union cohort): **315** across **36**/44 DFNs (8 DFNs clean).

## Top R69 narratives

- 148× `Malignant neoplasm of breast (disorder)` — concentrated (esp. DFNs 101116, 101123)
- 52× `Normal pregnancy`
- 39× `Viral sinusitis (disorder)`
- 10× `Normal pregnancy (finding)`
- 5× `Proteinuria due to type 2 diabetes mellitus (disorder)`
- 5× `Laceration - injury (disorder)`
- 4× `Acute infective cystitis (disorder)`
- 4× `Concussion injury of brain (disorder)`
- 4× `Allergic disposition (finding)`
- 3× `Viral sinusitis (disorder) (ICD-10-CM R69.)`
- 3× `Complete miscarriage (disorder)`
- 3× `Fracture of bone (disorder)`
- 2× `Diabetes mellitus`
- 2× `Injury of neck (disorder)` / burn / transport / fetus complication / concussion variants

Highest R69 DFNs: **101116** (70), **101123** (68), **101124** (24), **101127** (24), **101125** (17).

## Per-measure gaps (union of 44 DFNs)

Buckets: `has_active_good` = coded evidence that matches measure keywords/codes; `r69_only_no_active_good` = concept text on R69 Condition without active good ICD/SCT; `concept_narr_inactive_or_uncoded` = narrative/proc/obs without usable coding (or inactive); `no_concept_evidence` = no matching concept in FHIR graph.

### CMS165v14 — HTN / BP control
- gap mix: `{'has_active_good': 44}`
- Coding is **not** the bottleneck on this cohort — every scanned DFN already has active good HTN/BP codes.
- Funnel gap is **DENOM/NUMER** (21 IPP → 4 DENOM → 1 NUMER): BP timing/control and DENOM filters, not R69.

### CMS122v14 — Diabetes / A1c
- gap mix: `{'has_active_good': 39, 'r69_only_no_active_good': 3, 'concept_narr_inactive_or_uncoded': 1, 'no_concept_evidence': 1}`
- Dashboard POP already **5/5/5**. Residual R69 DM narratives are on **non-POP** DFNs: **101099, 101101, 101107** (R69-only); **101111** (narr/uncoded); **101065** (no concept).
- Hygiene only unless POP expands.

### CMS125v14 — Breast cancer screening
- gap mix: `{'has_active_good': 11, 'no_concept_evidence': 33}`
- DENOM miss-NUMER (no mammo codes in graph): **101077, 101084, 101101, 101102, 101103, 101104, 101105, 101116**
- Massive R69 breast-neoplasm pile (148) may affect exclusions / Condition noise; mammo Procedure/Obs coding still missing for half of DENOM.

### CMS130v14 — Colorectal screening
- gap mix: `{'has_active_good': 5, 'no_concept_evidence': 39}`
- DENOM miss-NUMER: **101095, 101096, 101098, 101101, 101103, 101107, 101109, 101115** (plus IPP-only without colo evidence)
- Same shape as pre-bridge WVEHR: little coded ProcedurePerformed/Obs for colo/FIT in graph.

### CMS138v14 — Tobacco screening
- gap mix: `{'has_active_good': 42, 'no_concept_evidence': 2}`
- Almost all DFNs already show tobacco Obs/Proc codes. NUMER 6/28 is **cessation intervention / timing**, not missing screen codes.
- No concept: **101065** (in POP, DENOM, not NUMER), **101119** (not IPP).

### CMS2v15 — Depression screening
- gap mix: `{'concept_narr_inactive_or_uncoded': 32, 'no_concept_evidence': 9, 'has_active_good': 3}`
- Dashboard **21/21/0** — every POP patient is DENOM with NUMER false.
- Nearly all CMS2 POP DFNs sit in `concept_narr_inactive_or_uncoded` (PHQ/depression text or Procedure without LOINC `73832-8` + QDM Assessment shape / encounter window).
- Same class as WVEHR pre-NUMER-bridge: cds1 `fhir-to-qdm-patient` Assessment mapping + encounter-day PHQ Obs.

## Contrast vs WVEHR (same day)

| | WVEHR (`fhir.vistaplex.org`) | fhirdev (`devfhir.vistaplex.org`) |
|--|------------------------------|-----------------------------------|
| Cohort | DFNs 1–14 | 44 POP DFNs (101065–101128 range) |
| CMS165 | 5/5/5 after R69 repair | 21/4/1 — codes present; DENOM/NUMER thin |
| CMS122 | 3/3/0 after DM repair | **5/5/5** already |
| CMS2 NUMER | 13/13/12 after bridge | **21/21/0** — bridge not applied / evidence uncoded |
| R69 volume | cleaned toward 0 POV | **315** FHIR Condition rows still visible |
| Dominant R69 | was gingivitis/stress (pre-clean) | breast neoplasm + pregnancy |
