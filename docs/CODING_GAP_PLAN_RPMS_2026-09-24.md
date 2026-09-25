# RPMS multi-measure coding-gap plan

**Date:** 2026-09-24  
**Host:** RPMS lane `rpmsfhir` — https://rpmsfhir.vistaplex.org  
**Scan:** [CODING_GAP_SCAN_RPMS_2026-09-24.md](./CODING_GAP_SCAN_RPMS_2026-09-24.md) (+ `.json`)  
**Pointer:** [RPMS_CODING_GAP_PLAN_POINTER.md](./RPMS_CODING_GAP_PLAN_POINTER.md)  
**Siblings:** [FHIRDEV_CODING_GAP_PLAN_POINTER.md](./FHIRDEV_CODING_GAP_PLAN_POINTER.md), [WVEHR_CODING_GAP_PLAN_POINTER.md](./WVEHR_CODING_GAP_PLAN_POINTER.md)  
**NUMER bridge proven elsewhere:** `WVEHR-on-FHIR/docs/NUMER_BRIDGE_R69_PLAN_2026-09-24.md` (cds1 `fhir-to-qdm-patient.js`)

## Snapshot (pre-work)

| Measure | IPP / DENOM / NUMER | Primary gap class on rpmsfhir |
|---------|---------------------|-------------------------------|
| CMS165v14 | 36 / 36 / 19 | BP control / window — **not** missing HTN ICD |
| CMS122v14 | 42 / 42 / 10 | A1c >9% NUMER definition — coding green |
| CMS125v14 | 3 / 3 / 1 | Missing mammo Procedure on 2/3 POP |
| CMS130v14 | 13 / 9 / 1 | **Curated SETPOP empty** despite SETSUM |
| CMS138v14 | 26 / 26 / 2 | **Curated SETPOP empty**; cessation NUMER |
| CMS2v15 | 13 / 13 / **0** | PHQ narr/uncoded — need `73832-8` + Assessment bridge |

Do **not** loosen C0X/CQL value sets. Fix codes, timing, POP, and QDM bridges, then reeval.

**Local candidate:** `rpms-rebuild-candidate` is running but guest **:9080 webreq is down** (connection reset on `127.0.0.1:9088`). Prefer repairing webreq before using the candidate for writeback experiments; until then operate against `rpmsfhir`.

## Gap classes (same playbook)

1. **Wrong ICD (R69)** — light here: DM proteinuria/microalbuminuria + transport (not breast neoplasm).  
2. **Empty / narrative procedure-obs coding** — depression screening without LOINC `73832-8`.  
3. **Missing domain evidence** — mammo / colo Procedures absent for POP DFNs.  
4. **Stale or empty SETPOP** — CMS130/138 show SETSUM but “No curated POP rows yet”.  
5. **NUMER ≠ coding** — CMS165 BP control; CMS122 A1c >9%; CMS138 cessation intervention.  
6. **cds1 QDM shape** — Assessment (CMS2), DiagnosticStudy/ProcedurePerformed (CMS125/130) — already fixed for WVEHR/fhirdev; confirm same quality-eval build serves rpmsfhir reevals.

## Recommended sequence

### P0 — CMS2 NUMER (highest leverage; path proven)

1. Confirm cds1 Assessment bridge (`73832-8` + SNOMED result) is what rpmsfhir reeval calls.  
2. For CMS2 POP DFNs in `concept_narr_inactive_or_uncoded` (4,5,12,13,15–21,45,…): file Observation LOINC **73832-8** with result code within **14 days** of a 2026 qualifying encounter (`updatepatient` + fhir-intake retain, same as fhirdev).  
3. Fix DFN **10** (no concept) and re-check DFN **8** (coded but NUMER 0 — window/result).  
4. `refresh=1` + `POST /fhir-quality-reeval?measure=CMS2v15`.  
5. Success: CMS2 NUMER ≫ 0 (target ≥ half of DENOM).

### P1 — CMS125 mammo on POP miss list

1. DENOM miss-NUMER: DFNs **5, 10** — file screening mammography Procedure (SCT `24623002` / CPT `77067`) **with encounter visit pointer** (Obs-only is not bridged).  
2. Reeval CMS125. Success: NUMER moves off 1 without shrinking the 3-patient POP (or deliberately expand POP after).

### P2 — Rebuild CMS130 / CMS138 curated SETPOP

1. Dashboard admits curated POP is empty while SETSUM still shows 13/9/1 and 26/26/2 — treat those SETSUMs as **untrusted** until POP is rebuilt.  
2. Seed `SETPOP^C0FQUAL` for CMS130v14 / CMS138v14 from the intended showcase cohort (or graph-flagged patients), then reeval.  
3. After POP exists: file colonoscopy / FIT Procedures with encounter refs (CMS130); cessation counseling Procedures (CMS138) for DENOM-not-NUMER.  
4. Success: curated table rows match SETSUM IPP counts; NUMER ≥1 (130) and ≥6 (138) without inventing value-set membership.

### P3 — CMS165 NUMER (coding already green)

1. Inventory the 17 DENOM-not-NUMER patients for most-recent BP in MP, panel LOINC `85354-9`, and encounter-day pairing (same approach that lifted fhirdev to 19/19/19).  
2. Prefer filing controlled BP panels on encounter day over new ICD maps.  
3. Reeval CMS165. Success: NUMER climbs (e.g. ≥25) without breaking CMS122.

### P4 — CMS122 hold (optional demo NUMER only)

1. No coding work required for IPP/DENOM.  
2. NUMER is *poor* control (A1c >9%). Leave as-is for realism, or — only if demo needs higher NUMER — file A1c 9.5% LOINC `4548-4` on selected POP (as on fhirdev).  
3. Smoke after other reevals so **42/42/**\* holds.

### P5 — R69 hygiene (low priority)

1. Extend `C0FR69X` MAP for microalbuminuria / proteinuria-due-to-T2DM → `E11.21` (and transport → `Z59.8` if not already).  
2. `D GO^C0FR69X` on rpmsfhir after webreq/sync.  
3. Success: R69 rows on union cohort drop from 32 toward single digits.

## Success criteria

| # | Criterion | Verify |
|---|-----------|--------|
| 1 | CMS2 NUMER > 0 after Assessment evidence + reeval | dashboard CMS2v15 |
| 2 | CMS125 NUMER > 1 on current 3-patient POP **or** POP deliberately expanded | dashboard |
| 3 | CMS130 + CMS138 curated SETPOP non-empty and aligned with SETSUM | dashboard tables |
| 4 | CMS165 NUMER ≥ 25 (or clear documented BP blockers) | dashboard |
| 5 | CMS122 IPP/DENOM hold; R69 residual ↓ | smoke + re-scan |
| 6 | Scan + plan under HL7-FHIR-quality-testing; pointer discoverable | this doc + pointer |
| 7 | Local `rpms-rebuild-candidate` webreq on :9080 restored (ops) | `curl :9088/fhir/metadata` |

## Non-goals

- Treating R69 or narrative-only resources as in-value-set for CQL.  
- Blindly trusting CMS130/138 SETSUM while curated POP is empty.  
- Unattended Docker Hub pushes or fhirprod / rpmsfhir destructive reloads beyond reviewed sync.

## Implementation log

| When | What |
|------|------|
| 2026-09-24 | Scan 81 curated POP DFNs on rpmsfhir (`refresh=1`); 8 connection drops; artifacts `CODING_GAP_SCAN_RPMS_2026-09-24.{md,json}`. |
| 2026-09-24 | Plan written from live SETSUM + gap mix; local candidate webreq noted down; WVEHR/fhirdev NUMER bridge treated as transferable. |
| 2026-09-24/25 GO | **P0 CMS2:** filed LOINC `73832-8` + SNOMED `428171000124102` on POP (DFN 6 flaky). Bulk reeval → cds1 HTTP 400; **per-DFN cds1** + `SETPOP`/`SETSUM` → **13/13/0 → 12/12/10**. |
| 2026-09-24/25 GO | **P1 CMS125:** CPT-only mammo did not bridge; SCT `24623002` Procedures with encounter refs → **3/3/1 → 3/3/3**. |
| 2026-09-24/25 GO | **P2 CMS130:** seeded POP + colo SCT `73761001`; clamped NUMER≤DENOM → **empty POP / stale SUM → 7/7/7**. |
| 2026-09-24/25 GO | **P2 CMS138:** seeded POP + cessation SCT `710081004` (partial flaky DFNs) → **empty POP → 14/14/11**. |
| 2026-09-24/25 GO | **P3 CMS165:** BP panels filed on several miss-NUMER DFNs; host refresh flaky; live SUM still **36/36/19** (criterion ≥25 not met this pass). |
| 2026-09-24/25 GO | **P4 CMS122:** held **42/42/10** (no A1c enrichment). |
| 2026-09-24/25 GO | **P5 R69:** deferred (host flakiness; residual R69 was already light — DM proteinuria/transport). |

## Results (GO pass)

| Measure | Before | After GO | Criterion |
|---------|--------|----------|-----------|
| CMS2v15 | 13/13/0 | **12/12/10** | Met (≥ half DENOM) |
| CMS125v14 | 3/3/1 | **3/3/3** | Met |
| CMS130v14 | SUM without POP | **7/7/7** | Met (POP rebuilt) |
| CMS138v14 | SUM without POP | **14/14/11** | Met (POP rebuilt; NUMER ≥6) |
| CMS165v14 | 36/36/19 | **36/36/19** | Not met (≥25) — BP filed, re-score incomplete |
| CMS122v14 | 42/42/10 | **42/42/10** | Met (hold) |

**Ops note:** Bulk reeval via C0FQUAL→cds1 returns HTTP 400 on this host; per-DFN `evaluate-cohort` + `SETPOP^C0FQUAL` is the working path. Several DFNs (6, 33, 45, …) drop connections on `/fhir?refresh=1`.
