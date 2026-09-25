# Iris coding-gap scan — 2026-09-25

**Host:** Iris lane `irisfhir` — https://irisfhir.vistaplex.org (VistA-on-IRIS)  
**Cohort:** graph-linked DFNs **1–13** (dashboards report **n=12** patients); curated POP is a tiny showcase set  
**Method:** scrape quality-dashboard SETSUM + POP; `GET /fhir?dfn=N&refresh=1`; classify Conditions / Observations / Procedures against measure keywords + known good codes. Heuristic — not VSAC-complete.  
**Machine JSON:** [CODING_GAP_SCAN_IRIS_2026-09-25.json](./CODING_GAP_SCAN_IRIS_2026-09-25.json)  
**Plan:** [CODING_GAP_PLAN_IRIS_2026-09-25.md](./CODING_GAP_PLAN_IRIS_2026-09-25.md)

Refresh errors: **0** (all 13 DFNs returned).

## Live CQL / dashboard SETSUM

| Measure | IPP | DENOM | NUMER | DENEX | Note |
|---------|----:|------:|------:|------:|------|
| CMS165v14 | 2 | 2 | 1 | 0 | Coding green; DFN 10 miss NUMER (BP control) |
| CMS122v14 | 1 | 1 | 1 | 0 | Met; POP DFN 2 only |
| CMS125v14 | 1 | 1 | 0 | 0 | DFN 2 — no mammo concept |
| CMS130v14 | 2 | 2 | 0 | 0 | DFN 10 coded colo but NUMER 0; DFN 2 narr |
| CMS138v14 | 3 | 3 | 3 | 0 | Fully met — hold |
| CMS2v15 | 4 | 4 | **0** | 0 | Procedure PHQ present; need Assessment `73832-8` |

## R69 Condition rows

**235** R69 rows across the 13 DFNs (fhirdev-shaped pile on a tiny cohort).

Top narratives:

- 148× `Malignant neoplasm of breast (disorder)`
- 52× `Normal pregnancy`
- 17× `Viral sinusitis (disorder)`
- 3× `Laceration - injury (disorder)`
- 2× each: loss of taste, ankle sprain, concussion variants

Highest R69 DFNs: **11** (70), **3** (67), then 4 (24), 7 (23), 5 (17). Breast-neoplasm + pregnancy dominate — same Synthea R69 class as fhirdev, concentrated on two patients.

## Per-measure gaps (scanned DFNs 1–13)

Buckets: `has_active_good` = coded evidence matching keywords/codes; `r69_only_no_active_good` = concept on R69 without good ICD/SCT; `concept_narr_inactive_or_uncoded` = narrative / wrong shape; `no_concept_evidence` = no matching concept in graph.

### CMS165v14 — HTN / BP control
- gap mix: `{'has_active_good': 13}`
- Coding is **not** the bottleneck. Funnel 2/2/1 → DFN **10** DENOM miss NUMER (BP timing/control), DFN **2** NUMER.

### CMS122v14 — Diabetes / A1c
- gap mix: `{'has_active_good': 2, 'concept_narr_inactive_or_uncoded': 3, 'no_concept_evidence': 8}`
- Curated POP is only DFN **2** (NUMER true). Heuristic tags DFN 2 as `concept_narr_inactive_or_uncoded`, but CQL still counts — do **not** “fix” coding that already scores. Hold 1/1/1 unless expanding the showcase POP.

### CMS125v14 — Breast cancer screening
- gap mix: `{'has_active_good': 6, 'no_concept_evidence': 7}`
- Curated POP DFN **2**: `no_concept_evidence` and NUMER false. Other DFNs have mammo codes on the graph but are outside this 1-patient POP.

### CMS130v14 — Colorectal screening
- gap mix: `{'has_active_good': 6, 'concept_narr_inactive_or_uncoded': 1, 'no_concept_evidence': 6}`
- POP: DFN **10** `has_active_good` but NUMER false (timing / encounter / QDM shape); DFN **2** `concept_narr_inactive_or_uncoded`, NUMER false.

### CMS138v14 — Tobacco screening
- gap mix: `{'has_active_good': 13}`
- POP DFNs **2, 9, 10** all NUMER — **3/3/3**. No coding work.

### CMS2v15 — Depression screening
- gap mix: `{'has_active_good': 8, 'no_concept_evidence': 5}`
- Curated POP (DFNs **2, 8, 9, 10**): all DENOM, all NUMER false, all heuristic `has_active_good`.
- That “good” evidence is **Procedure**-shaped (Synthea PHQ / depression screen SCT `171207006` / `715252007`), **not** Observation LOINC **`73832-8`** Assessment with a result code — same class that blocked NUMER on fhirdev/WVEHR/rpmsfhir before the Assessment bridge + file step.
- Success path is already proven on other lanes: file `73832-8` (+ result) within encounter window, reeval via cds1.

## Contrast vs siblings (same week)

| | Iris (`irisfhir`) | rpmsfhir | fhirdev |
|--|-------------------|----------|---------|
| Cohort | DFNs 1–13, n≈12 | 81 curated POP | ~44 POP DFNs |
| R69 volume | **235** (breast neoplasm dominant) | 32 (DM proteinuria/transport) | 315 (breast neoplasm) |
| CMS2 | **4/4/0** Procedure≠Assessment | was 13/13/0 → 12/12/10 after GO | Assessment path proven |
| CMS125 | **1/1/0** no mammo on POP | 3/3/3 after GO | — |
| CMS130 | **2/2/0** coded+narr miss | 7/7/7 after GO | — |
| CMS138 | **3/3/3** hold | 14/14/11 after GO | — |
| CMS165 | **2/2/1** BP miss on DFN 10 | 36/36/19 | — |
| CMS122 | **1/1/1** hold | 42/42/10 | — |
