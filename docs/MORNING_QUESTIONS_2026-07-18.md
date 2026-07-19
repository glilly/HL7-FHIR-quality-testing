# Morning review questions — 2026-07-18

Overnight work continued the recommended path: implement C0FW lab filing via the proven SYN/ISI `LABADD^SYNDHP63` path, keep CMS122 Quality AI Consult as the consumer, and leave questions here instead of blocking.

## Decisions (answered 2026-07-19)

1. **Lab engine ownership** — keep C0FWLAB SYN/ISI under native ownership.  
2. **Demo HbA1c value** — require clinician data entry of result specifics (implemented in cds-hooks + CPRS demo).  
3. **DiagnosticReport panels** — not needed for these lab tests.  
4. **CQL honesty** — prioritize FHIR→QDM bridge before more cohorts (bridge scripts added; Bonnie measure package still required).  
5. **Smoke** — both updatepatient and Quality AI Consult.  
6. **SYNQLDM map reload** — yes.  
7. **Commit / push** — yes, then deploy.  

## Status at handoff

### Done in code

- `VistA-FHIR-Server-Codex/src/C0FWLAB.m` — files laboratory `Observation` via SYN/ISI; maps `4548-4` etc. to `HEMOGLOBIN A1C`; sets Kernel context; treats ISI duplicates as loaded; leaves `DiagnosticReport` as explicit NI.
- `C0FWDOM.m` — `engine.Lab=syn|isi` routes to `C0FWLAB`; `auto` can retry Lab through same adapter.
- `C0FWPOL.m` — capability probe for Lab syn/isi via `LABADD^SYNDHP63`.
- `VistA-FHIR-Data-Loader/src/SYNQLDM.m` — added `4548-4` and `4549-2` lab map rows.
- Quality-testing docs: CMS165 heuristic proxy note + this questions file.
- Codex note: `docs/C0FWLAB_SYN_ISI_NOTES.md`.

### Verified on fhirdev

- `SYNDHP63`, `ISIIMP12`, `SYNFLAB` present.
- `#60` `HEMOGLOBIN A1C` = IEN `97`.
- DFN `101090` `CHALMERS,PETER` has SSN and `AFICN=8800000482V948500`.
- Direct `LABADD` spike: `RETSTA=1`, created `LR=809` (value `7.2`). Lab package printed rollover warnings but accession completed.
- HTTP `POST /updatepatient?dfn=101090&load=1` with one LOINC `4548-4` Observation: **HTTP 201**, `domains.Lab.status=loaded`, message `HEMOGLOBIN A1C=7.4`.
- Readback `GET /fhir/Observation?patient=101090&category=laboratory` returns both `7.2` and `7.4` A1C Observations with US Quality Core lab profile.

### Still for morning

- CPRS Notes → Quality AI Consult → accept `cms122-import-hba1c` end-to-end (HTTP path already proves filing; UI path not smoked overnight).
- Official CQL MeasureReports.
- Lab `DiagnosticReport` panel path.
- Meds / procedures (deferred).
- Commits/pushes (not created overnight).
- Formal `XINDEX` pass on changed routines (ZLINK OK; interactive XINDEX not completed).

## Suggested morning checklist

1. Answer questions 1–5 above.
2. In CPRS demo for DFN `101090`, run Quality AI Consult and accept only HbA1c; confirm Cover Sheet Labs shows the new result.
3. Optional: run `XINDEX` on `C0FWLAB`, `C0FWDOM`, `C0FWPOL`.
4. Decide commit/push scope across Codex / Data-Loader / quality-testing.
