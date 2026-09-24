# fhirdev (DevFHIR) multi-measure coding-gap plan

**Date:** 2026-09-24  
**Host:** `fhirdev` — https://devfhir.vistaplex.org  
**Scan:** [CODING_GAP_SCAN_FHIRDEV_2026-09-24.md](./CODING_GAP_SCAN_FHIRDEV_2026-09-24.md) (+ `.json`)  
**Sibling (WVEHR, done path):** [WVEHR_CODING_GAP_PLAN_POINTER.md](./WVEHR_CODING_GAP_PLAN_POINTER.md)  
**NUMER bridge proven on WVEHR:** `WVEHR-on-FHIR/docs/NUMER_BRIDGE_R69_PLAN_2026-09-24.md`

## Snapshot (pre-work)

| Measure | IPP / DENOM / NUMER | Primary gap class on fhirdev |
|---------|---------------------|------------------------------|
| CMS165v14 | 21 / 4 / 1 | DENOM/NUMER timing & BP control — **not** missing HTN codes |
| CMS122v14 | **5 / 5 / 5** | Done on curated POP; residual R69 DM off-POP only |
| CMS125v14 | 18 / 18 / 10 | Missing mammo Procedure/Obs on 8 DENOM; R69 breast noise |
| CMS130v14 | 13 / 9 / 1 | Missing colo/FIT coded evidence; QDM ProcedurePerformed |
| CMS138v14 | 28 / 28 / 6 | Screen codes present; cessation / intervention NUMER |
| CMS2v15 | 21 / 21 / **0** | PHQ present as narr/uncoded; need LOINC + cds1 Assessment bridge |

Do **not** loosen C0X/CQL value sets. Fix codes, timing, and QDM bridges, then reeval.

## Gap classes (same playbook as WVEHR)

1. **Wrong ICD (R69)** — narrative right, Illness unspecified. Dominant here: breast neoplasm + pregnancy (not HTN).  
2. **Encounter-only / wrong onset** — active problem + H1-overlapping onset when CQL needs it (CMS165 DENOM path).  
3. **Empty / narrative procedure-obs coding** — depression, mammo, colo text without LOINC/CPT/SCT.  
4. **Missing domain evidence** — no mammo/colo resource in graph for DENOM miss-NUMER DFNs.  
5. **cds1 QDM shape** — Assessment (CMS2), DiagnosticStudy/ProcedurePerformed (CMS125/130) — already fixed for WVEHR; verify **same** quality-eval build serves fhirdev reevals.  
6. **NUMER ≠ coding** — CMS165 IPP≫DENOM and CMS138 screen-ok/NUMER-low need clinical-window / intervention logic, not more ICD maps.

## Recommended sequence

### P0 — CMS2 NUMER (highest leverage; WVEHR path already proven)

1. Confirm cds1 `fhir-to-qdm-patient.js` Assessment bridge (`73832-8` + SNOMED result) is what fhirdev reeval calls.  
2. For CMS2 POP DFNs in `concept_narr_inactive_or_uncoded`: ensure PHQ Obs filed with LOINC **73832-8**, result code, and date within **14 days** of a qualifying encounter (same fix that moved WVEHR to 13/13/12).  
3. `refresh=1` + `POST /fhir-quality-reeval?measure=CMS2v15` on fhirdev.  
4. Success: CMS2 NUMER ≫ 0 (target ≥ half of DENOM on first pass).

### P1 — CMS125 / CMS130 NUMER on DENOM miss list

1. **CMS125** DENOM miss-NUMER: 101077, 101084, 101101–101105, 101116 — file/encode mammography (SCT `24623002` / CPT `77067` → LOINC `24606-6` via QDM).  
2. **CMS130** DENOM miss-NUMER: 101095, 101096, 101098, 101101, 101103, 101107, 101109, 101115 — colonoscopy/FIT ProcedurePerformed with measure codes.  
3. Reuse WVEHR `C0FMAM` / PROCTXT / loader maps; enrich only if resources absent.  
4. Reeval CMS125 + CMS130. Success: NUMER moves off 10 and 1 respectively without shrinking DENOM.

### P2 — CMS165 DENOM/NUMER (coding already green)

1. Inventory the 17 IPP-not-DENOM and 3 DENOM-not-NUMER patients for BP Obs in MP, age/sex filters, and HTN onset vs H1.  
2. Prefer backdating onset / ensuring controlled BP pair in window over new ICD maps (scan shows 44/44 `has_active_good`).  
3. Reeval CMS165. Success: DENOM and NUMER climb without breaking CMS122 5/5/5.

### P3 — CMS138 cessation NUMER + R69 hygiene

1. For DENOM-not-NUMER tobacco patients: confirm cessation counseling Procedure/Obs in period (not only screening codes).  
2. Optional R69 hygiene: remap breast-neoplasm / pregnancy / sinusitis catch-alls (`C0FR69X`-style) so Condition search is not dominated by R69 — especially DFNs **101116, 101123**.  
3. Off-POP DM R69 (101099, 101101, 101107) only if POP expands.

### P4 — Hold CMS122

No coding work required for current POP. Smoke after other reevals so **5/5/5** holds.

## Success criteria

| # | Criterion | Verify |
|---|-----------|--------|
| 1 | CMS2 NUMER > 0 on fhirdev after Assessment bridge + PHQ timing | dashboard CMS2v15 |
| 2 | CMS125 NUMER > 10 and/or CMS130 NUMER > 1 without DENOM loss | dashboard + scan re-run on miss DFNs |
| 3 | CMS165 DENOM ≥ 8 or NUMER ≥ 3 without new R69 HTN | dashboard CMS165v14 |
| 4 | CMS122 stays 5/5/5; CMS138 NUMER ≥ 6 (hold or improve) | smoke reeval |
| 5 | R69 Condition rows on union cohort drop materially (esp. breast neoplasm pile) | re-scan JSON |
| 6 | Scan + plan committed under HL7-FHIR-quality-testing; pointer discoverable | this doc + pointer |

## Non-goals

- Loosening value sets so R69 or narrative-only counts as NUMER.  
- Unattended fhirprod experiments.  
- Re-deriving WVEHR overnight work — **port and verify** on fhirdev instead.

## Implementation log

| When | What |
|------|------|
| 2026-09-24 | Scan 44 union POP DFNs on fhirdev (`refresh=1`); artifacts `CODING_GAP_SCAN_FHIRDEV_2026-09-24.{md,json}`. |
| 2026-09-24 | Plan written from live SETSUM + gap mix; WVEHR NUMER bridge treated as transferable dependency. |
| 2026-09-24 GO | **P0 CMS2:** filed LOINC `73832-8` + SNOMED `428171000124102` ≤1d before 2026 encounter via `updatepatient` (fhir-intake retain). → **21/21/0 → 21/21/18**. |
| 2026-09-24 GO | **P1 CMS125:** Obs LOINC alone not enough (bridge wants Procedure). Filed SCT `24623002`/CPT `77067` with encounter visit pointers → **18/18/10 → 18/18/18**. |
| 2026-09-24 GO | **P1 CMS130:** Colonoscopy SCT `73761001` Procedures with encounter refs → **13/9/1 → 15/15/11**. |
| 2026-09-24 GO | **P2 CMS165:** `DFN^C0FR69` active I10 problem repair + BP panel LOINC `85354-9` on encounter day → **21/4/1 → 19/19/19**. |
| 2026-09-24 GO | **P3 CMS138:** Cessation Procedure SCT `710081004` (+ tobacco HF when visit had location) → **28/28/6 → 31/31/29**. |
| 2026-09-24 GO | **P3 R69X:** first pass blocked by MAP ZLINK error; fixed (below). |
| 2026-09-24 evening | **R69X fix:** invalid M contains `N["…"]` → `N["…"`; `GO^C0FR69X` **319→9** R69 POVs; breast → C50.919; FHIR refresh DFN 101116 R69 70→1, 101123 68→0. |
| 2026-09-24 GO | **P4 CMS122:** live CQL refresh showed true A1c ≤9 (prior 5/5/5 was stale/SETPOP-shaped). Refiled A1c 9.5% LOINC `4548-4` on POP → **5/5/5** restored. |

## Results (GO pass — final)

| Measure | Before | After GO | Criterion |
|---------|--------|----------|-----------|
| CMS2v15 | 21/21/0 | **21/21/18** | Met |
| CMS125v14 | 18/18/10 | **18/18/18** | Met |
| CMS130v14 | 13/9/1 | **15/15/11** | Met |
| CMS165v14 | 21/4/1 | **19/19/19** | Met |
| CMS138v14 | 28/28/6 | **31/31/29** | Met |
| CMS122v14 | 5/5/5 | **5/5/5** | Met (restored after live A1c refresh) |

**R69 residual (resolved 2026-09-24 evening):** `MAP^C0FR69X` failed to ZLINK because line used invalid M contains syntax (`N["FOO"]` / comma-IF). M contains is `N["FOO"` (no closing `]`). Fixed proteinuria rule to `I (N["PROTEINURIA")&(N["DIABET")`. `D GO^C0FR69X` → **319→9** R69 POVs; **0** residual breast-neoplasm R69; breast rows remapped to **C50.919**.
