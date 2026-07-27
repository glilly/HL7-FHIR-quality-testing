# CMS165 closed loop — DFN 101115 (2026-07-27)

## Goal

Select a CMS165 patient in **DENOM yes / NUMER no**, run Quality AI Consult,
accept a **controlled BP**, file to VistA, see `/fhir` vitals update, re-run
official CQL, and flip the dashboard **NUMER** to Yes (rate rises).

## What we proved

| Step | Result |
|------|--------|
| Patient | **101115** CONROY74,ADOLFO777 — was `cql=1/1/0/0` |
| cds1 pick-list | After Stage 2 deploy: offers **`cms165-record-blood-pressure`** when BP uncontrolled (not only ServiceRequest follow-up) |
| Update Bundle | `POST /aiconsult/update-bundle` → Observation 85354-9 @ **128/78** |
| Writeback | `POST /updatepatient?dfn=101115&load=1` → Encounter + TIU + **Vital via GMVDCSAV** (HTTP 201) |
| `/fhir` read-back | Newest BP **V61805** `2026-07-27` **128/78** controlled |
| Official CQL | Synthea source + injected controlled BP → **`ipp/denom/numer = 1/1/1`** |
| Dashboard | SETPOP `101115` → **1/1/1/0**; CMS165 SUM **19/16/16**, **rate 100.0%** |

Script: `scripts/cms165-closed-loop-101115.sh`  
Log: `logs/cms165-closed-loop-101115-20260727-004613.log`

## Important caveat (CQL vs Codex `/fhir`)

`cqm-execution` on the **live Codex `/fhir?dfn=` Bundle alone** still returns
`0/0/0/0` (thin export / QDM bridge gap). The closed-loop script therefore:

1. Files BP into VistA (real chart / coversheet path).
2. Re-runs official CQL on **Synthea source + injected filed BP** for SETPOP.
3. Applies SETPOP/SUM on fhirdev.

Longer-term: make Codex `/fhir` CQL-complete, or auto-merge filed vitals into
the source graph used for measure recompute.

## UI path (rehmp)

With cds1 deployed, Quality AI Consult for 101115 should show systolic/diastolic
inputs for **Record a controlled blood pressure for numerator**. Flow:

1. Open measure dashboard → 101115 → rehmp  
2. Quality AI Consult → enter controlled BP → Add Selected to Note  
3. Finish Note / Send FHIR Update  
4. Cover sheet / vitals show new BP  
5. Re-run `scripts/cms165-closed-loop-101115.sh --skip-file` (or full script) to refresh SETPOP if not automated

## Code changes

- `cds-hooks-on-fhir` `QualityDiagnosticReportFactory.cms165()` — offer record-BP when uncontrolled  
- Deployed Stage 2 to `cds1.vistaplex.org`

## Next

- Wire rehmp “after send” hook to one-DFN CQL+SETPOP refresh  
- Same closed loop for CMS122 (HbA1c) with correct measure polarity  
- Improve Codex `/fhir` density so CQL can run without Synthea inject  
