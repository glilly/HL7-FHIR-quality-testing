# RPMS coding-gap scan — 2026-09-24

**Host:** RPMS lane `rpmsfhir` via https://rpmsfhir.vistaplex.org  
**Local note:** `rpms-rebuild-candidate` container is up (`127.0.0.1:9088→9080`) but **webreq is not listening on 9080** inside the guest — scan used the remote public lane.  
**Cohort:** union of curated SETPOP DFNs for CMS165 / CMS122 / CMS125 / CMS2 (**81** unique; 8 refresh timeouts)  
**Method:** `GET /fhir?dfn=N&refresh=1`, classify Conditions / Observations / Procedures against measure keywords + known good codes. Heuristic — not VSAC-complete.  
**Machine JSON:** [CODING_GAP_SCAN_RPMS_2026-09-24.json](./CODING_GAP_SCAN_RPMS_2026-09-24.json)

## Live CQL / dashboard SETSUM (same day)

| Measure | IPP | DENOM | NUMER | DENEX | Note |
|---------|----:|------:|------:|------:|------|
| CMS165v14 | 36 | 36 | 19 | 0 | Coding green; NUMER = BP control |
| CMS122v14 | 42 | 42 | 10 | 0 | Coding green; NUMER = A1c >9% |
| CMS125v14 | 3 | 3 | 1 | 0 | Tiny curated POP; mammo thin |
| CMS130v14 | 13 | 9 | 1 | 0 | **SETSUM present; curated POP table empty** |
| CMS138v14 | 26 | 26 | 2 | 0 | **SETSUM present; curated POP table empty** |
| CMS2v15 | 13 | 13 | 0 | 0 | 0% NUMER — Assessment / LOINC gap |

R69 Condition rows (any narrative, scanned cohort): **32** across **21**/73 successful DFNs (52 clean). Far lighter than fhirdev’s breast-neoplasm pile.

Refresh failures (excluded from gap counts): DFNs **6, 55, 62, 93, 153, 477, 734, 1073**.

## Top R69 narratives

- 12× `Microalbuminuria due to type 2 diabetes mellitus (disorder)`
- 9× `Transport problem (finding)`
- 8× `Proteinuria due to type 2 diabetes mellitus (disorder)`
- 2× `Fracture subluxation of wrist (disorder)`
- 1× `Acute pulmonary embolism (disorder)`

Highest R69 DFNs (count=2 each): 33, 104, 147, 168, 175, 210, 251, 311, 542, 574.

## Per-measure gaps (scanned DFNs)

Buckets: `has_active_good` = coded evidence matching keywords/codes; `r69_only_no_active_good` = concept on R69 without good ICD/SCT; `concept_narr_inactive_or_uncoded` = narrative / wrong shape; `no_concept_evidence` = no matching concept in graph.

### CMS165v14 — HTN / BP control
- gap mix: `{'has_active_good': 73}`
- Coding is **not** the bottleneck — every successful scan DFN already has active good HTN/BP codes.
- Funnel: 36/36/19 → **17 DENOM miss NUMER**, all with `has_active_good` when scanned (BP timing/control, not ICD).

### CMS122v14 — Diabetes / A1c
- gap mix: `{'has_active_good': 73}`
- Same shape: codes present; NUMER is *poor* glycemic control (A1c >9%). Dashboard 42/42/10 is expected if most A1c ≤9.

### CMS125v14 — Breast cancer screening
- gap mix: `{'has_active_good': 1, 'no_concept_evidence': 72}`
- Curated POP only 3 patients: DFN **4** NUMER (good mammo); **5** and **10** DENOM miss NUMER with **no** mammo concept in graph.

### CMS130v14 — Colorectal screening
- gap mix: `{'has_active_good': 35, 'no_concept_evidence': 38}`
- Dashboard SETSUM 13/9/1 but **curated SETPOP HTML is empty** (“No curated POP rows yet”). Cannot attribute miss-NUMER DFNs without rebuilding POP.
- Union-cohort graph still shows colo evidence on ~half of scanned patients.

### CMS138v14 — Tobacco screening
- gap mix: `{'has_active_good': 72, 'no_concept_evidence': 1}` (DFN 10)
- Screen codes largely present. SETSUM 26/26/2 with **empty curated POP** — NUMER gap is cessation / POP hygiene, not missing tobacco Obs codes on the union graph.

### CMS2v15 — Depression screening
- gap mix: `{'has_active_good': 60, 'concept_narr_inactive_or_uncoded': 12, 'no_concept_evidence': 1}`
- Curated POP (13): almost all DENOM with NUMER false; **11**/13 sit in `concept_narr_inactive_or_uncoded` or failed refresh — need LOINC `73832-8` Assessment (+ cds1 bridge already proven on fhirdev/WVEHR).
- DFN **8** already `has_active_good` but still NUMER false → timing / encounter window / result code.
- DFN **10** `no_concept_evidence`.

## Contrast vs fhirdev (same day)

| | fhirdev | rpmsfhir |
|--|---------|----------|
| Cohort | 44 POP DFNs (~101065+) | 81 curated POP DFNs (low DFNs + Synthea) |
| R69 volume | 315 (breast neoplasm dominant) | **32** (DM proteinuria / transport) |
| CMS165 | 21/4/1 → coding then DENOM | **36/36/19** coding green; NUMER=BP |
| CMS122 | 5/5/5 curated | **42/42/10** coding green; NUMER=A1c>9 |
| CMS2 | was 21/21/0 before bridge | **13/13/0** — same Assessment class |
| CMS130/138 POP | curated present | **SETSUM without curated POP rows** |
