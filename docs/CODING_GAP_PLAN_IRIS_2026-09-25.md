# Iris multi-measure coding-gap plan

**Date:** 2026-09-25  
**Host:** Iris lane `irisfhir` — https://irisfhir.vistaplex.org (VistA-on-IRIS)  
**Scan:** [CODING_GAP_SCAN_IRIS_2026-09-25.md](./CODING_GAP_SCAN_IRIS_2026-09-25.md) (+ `.json`)  
**Pointer:** [IRIS_CODING_GAP_PLAN_POINTER.md](./IRIS_CODING_GAP_PLAN_POINTER.md)  
**Siblings:** [FHIRDEV_CODING_GAP_PLAN_POINTER.md](./FHIRDEV_CODING_GAP_PLAN_POINTER.md), [RPMS_CODING_GAP_PLAN_POINTER.md](./RPMS_CODING_GAP_PLAN_POINTER.md), [WVEHR_CODING_GAP_PLAN_POINTER.md](./WVEHR_CODING_GAP_PLAN_POINTER.md)  
**NUMER bridge proven elsewhere:** `WVEHR-on-FHIR/docs/NUMER_BRIDGE_R69_PLAN_2026-09-24.md` (cds1 `fhir-to-qdm-patient.js`); RPMS GO pass 2026-09-24/25

## Snapshot (pre-work)

| Measure | IPP / DENOM / NUMER | Primary gap class on irisfhir |
|---------|---------------------|-------------------------------|
| CMS165v14 | 2 / 2 / 1 | BP control on DFN 10 — **not** missing HTN ICD |
| CMS122v14 | 1 / 1 / 1 | Hold — already met |
| CMS125v14 | 1 / 1 / 0 | Missing mammo Procedure on POP DFN 2 |
| CMS130v14 | 2 / 2 / 0 | DFN 10 coded but miss NUMER; DFN 2 narr/uncoded |
| CMS138v14 | 3 / 3 / 3 | Hold — fully met |
| CMS2v15 | 4 / 4 / **0** | Procedure PHQ only — need `73832-8` Assessment |

Do **not** loosen C0X/CQL value sets. Fix codes, timing, QDM bridges, then reeval. Cohort is intentionally tiny (n≈12); prefer surgical POP fixes over expanding the showcase set unless asked.

## Gap classes (same playbook)

1. **Wrong ICD (R69)** — heavy here: breast neoplasm (148) + normal pregnancy (52), concentrated on DFNs **3** and **11**.  
2. **Wrong FHIR shape for CMS2** — Procedure SCT depression screen without Observation Assessment LOINC `73832-8`. Heuristic `has_active_good` does **not** mean CQL NUMER.  
3. **Missing domain evidence** — mammo Procedure absent on CMS125 POP DFN 2.  
4. **NUMER ≠ coding** — CMS165 BP control (DFN 10); CMS130 timing/encounter/QDM (DFN 10).  
5. **cds1 QDM shape** — Assessment (CMS2), DiagnosticStudy/ProcedurePerformed (CMS125/130) — already fixed for WVEHR/fhirdev/rpmsfhir; confirm Iris reeval hits the same quality-eval build.

## Recommended sequence

### P0 — CMS2 NUMER (highest leverage; path proven)

1. Confirm Iris `POST /fhir-quality-reeval` / C0FQUAL→cds1 uses the Assessment bridge (`73832-8` + SNOMED result).  
2. For CMS2 POP DFNs **2, 8, 9, 10**: file Observation LOINC **`73832-8`** with a value-set result code within **14 days** of a 2026 qualifying encounter (`updatepatient` + fhir-intake retain). Do **not** rely on Procedure `171207006` / `715252007` alone.  
3. Prefer per-DFN cds1 evaluate + `SETPOP^C0FQUAL` if bulk reeval flakes (same ops note as rpmsfhir REFFIXEMIT hang — Iris may share Codex `C0FHIRLG`; keep `REFFIXEMIT` gated off).  
4. Success: CMS2 NUMER ≫ 0 (target ≥ 2 of 4 DENOM; stretch 4/4).

### P1 — CMS125 mammo on POP DFN 2

1. File screening mammography **Procedure** SCT `24623002` (or CPT `77067` **plus** SCT — CPT-only failed to bridge on RPMS) **with encounter visit pointer**.  
2. Reeval CMS125. Success: **1/1/1** without shrinking the 1-patient POP.

### P2 — CMS130 colo on POP miss list

1. DFN **10**: inventory existing colo Procedure vs MP window and encounter ref — file/fix timing or re-file SCT `73761001` with encounter if graph code is outside window / wrong QDM type.  
2. DFN **2**: replace narr/uncoded colo with coded Procedure + encounter ref.  
3. Reeval CMS130. Success: NUMER ≥ 1 (target **2/2/2**).

### P3 — CMS165 NUMER (coding already green)

1. DFN **10**: most-recent BP in MP, panel LOINC `85354-9`, encounter-day pairing (same pattern that lifted fhirdev).  
2. Prefer filing a controlled BP panel on encounter day over new ICD maps.  
3. Reeval CMS165. Success: **2/2/2**.

### P4 — Hold CMS122 / CMS138

1. CMS122 **1/1/1** and CMS138 **3/3/3** — no coding work.  
2. Smoke after other reevals so those SETSUMs hold.  
3. Optional later: expand showcase POP only if demos need more than one DM patient.

### P5 — R69 hygiene (low priority on tiny lane)

1. Extend / run `C0FR69X` MAP for breast neoplasm → appropriate ICD-10-CM and pregnancy → `Z34.*` (or defer and accept Synthea narrative pile on DFNs 3/11).  
2. Success: R69 rows on DFNs 1–13 drop from 235 toward fhirdev-after-repair levels; **do not** treat R69 as in-value-set for CQL.

## Success criteria

| # | Criterion | Verify |
|---|-----------|--------|
| 1 | CMS2 NUMER ≥ 2 after Assessment evidence + reeval | dashboard CMS2v15 |
| 2 | CMS125 **1/1/1** | dashboard |
| 3 | CMS130 NUMER ≥ 1 (target 2/2/2) | dashboard |
| 4 | CMS165 **2/2/2** | dashboard |
| 5 | CMS122 1/1/1 and CMS138 3/3/3 hold | smoke |
| 6 | Scan + plan under HL7-FHIR-quality-testing; pointer discoverable | this doc + pointer |

## Non-goals

- Treating R69 or Procedure-only depression screen as CMS2 NUMER.  
- Expanding Iris POP beyond the curated showcase unless a human asks.  
- Unattended Docker Hub pushes; experimental work on fhirprod.  
- Loosening VSAC / C0X value sets to chase NUMER.

## Implementation log

| When | What |
|------|------|
| 2026-09-25 | Scan DFNs 1–13 on irisfhir (`refresh=1`); 0 errors; artifacts `CODING_GAP_SCAN_IRIS_2026-09-25.{md,json}`. |
| 2026-09-25 | Plan written from live SETSUM + gap mix; CMS2 Assessment path treated as transferable from fhirdev/WVEHR/rpmsfhir GO. |
| 2026-09-25 GO | **GRAPHLABS:** Iris (VistA-on-IRIS) defaults graph-lab emit OFF; set `^C0FHIR("EXPERIMENT","GRAPHLABS")=1` so fhir-intake Observations (PHQ/Assessment) appear in `/fhir` export. |
| 2026-09-25 GO | **P0 CMS2:** filed LOINC `73832-8` (adult DFNs 2/9/10) and `73831-0` (adolescent DFN 8) + SNOMED `428171000124102`; cds1 per-DFN + `SETPOP`/`SETSUM` → **4/4/0 → 4/4/4**. |
| 2026-09-25 GO | **P1 CMS125:** SCT `24623002` + CPT `77067` Procedure w/ encounter on DFN 2 → **1/1/0 → 1/1/1**. |
| 2026-09-25 GO | **P2 CMS130:** SCT `73761001` + CPT `45378` on DFNs 2/10 → **2/2/0 → 2/2/2**. |
| 2026-09-25 GO | **P3 CMS165:** controlled BP panel `85354-9` 128/78 on DFN 10 → **2/2/1 → 2/2/2**. |
| 2026-09-25 GO | **Hold CMS138:** stayed **3/3/3**. |
| 2026-09-25 GO | **Hold CMS122:** re-score briefly dropped to 1/1/0; filed A1c `4548-4`=9.5 on DFN 2 and restored SETSUM → **1/1/1**. |
| 2026-09-25 GO | Driver artifacts: `/tmp/iris-gap-go/` (`go_iris_gaps.py`, per-measure JSON, `go.log`). |

## Results (GO pass)

| Measure | Before | After GO | Criterion |
|---------|--------|----------|-----------|
| CMS2v15 | 4/4/0 | **4/4/4** | Met (≥2; stretch 4/4) |
| CMS125v14 | 1/1/0 | **1/1/1** | Met |
| CMS130v14 | 2/2/0 | **2/2/2** | Met |
| CMS165v14 | 2/2/1 | **2/2/2** | Met |
| CMS122v14 | 1/1/1 | **1/1/1** | Met (hold; restored after A1c) |
| CMS138v14 | 3/3/3 | **3/3/3** | Met (hold) |

**Ops notes:** (1) Keep `GRAPHLABS=1` on Iris or Assessment filings stay invisible to cds1. (2) Adolescent POP members need LOINC `73831-0`, not adult `73832-8`. (3) Prefer cds1 per-DFN + `SETPOP^C0FQUAL` over TaskMan reeval (TaskMan site params still broken on IRIS). (4) Droplet `ufw limit 22/tcp` — multiplex SSH / cool down between bursts.
