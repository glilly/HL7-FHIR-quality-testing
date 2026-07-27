# CMS122 closed loop — DFN 101096 (2026-07-27)

## Goal

Select a CMS122 patient in **DENOM yes / NUMER no**, run Quality AI Consult,
accept **HbA1c > 9%** (poor-control numerator polarity), file to VistA, re-run
official CQL, and flip the dashboard **NUMER** to Yes.

## What we proved

| Step | Result |
|------|--------|
| Patient | **101096** BAUMBACH677,ALLINE927 — was `cql=1/1/0/0` |
| cds1 pick-list | Offers **`cms122-import-hba1c`** |
| Update Bundle | `POST /aiconsult/update-bundle` → Observation **4548-4** @ **9.2** |
| Writeback | `POST /updatepatient?dfn=101096&load=1` → Encounter + TIU + **Lab via LABADD** (`HEMOGLOBIN A1C=9.2`, HTTP 201) |
| `/fhir` read-back | Default bundle omits lab; **`/fhir?dfn=&domain=labs`** shows **9.2** |
| Heuristic SETPOP | `POST /fhir-quality-recompute` → **NUMER=1**, SUM rate **25.0%** |
| Official CQL | Synthea source + injected HbA1c 9.2 → **`ipp/denom/numer = 1/1/1`** |
| Dashboard | SETPOP `101096` → **Yes/Yes/Yes**; CMS122 SUM **5/4/1**, **rate 25.0%** |

Script: `scripts/cms122-closed-loop-101096.sh`  
Log: `logs/cms122-closed-loop-101096-20260727-005630.log`

## Polarity note

CMS122v14 is **poor glycemic control**: numerator is met when the most recent
HbA1c is **greater than 9%**. Filing a controlled value (e.g. 7.0) would keep
NUMER=No.

## UI path (rehmp)

After Send FHIR Update for a staged quality action, rehmp calls
`POST /fhir-quality-recompute` (proxied to the quality backend) so the
dashboard SETPOP/SUM refresh without a separate CQL job. Official CQL
verification still uses Synthea+inject (Codex `/fhir` alone remains too thin).

## Code changes

- Codex: `WSRECOMP^C0FQUAL` + `POST /fhir-quality-recompute` in `SYNWEBRG`
- rehmp: post-send hook in `finishNoteAndSendFhirUpdate`; gateway proxies recompute to `QUALITY_BACKEND`
