# Development Status and Gap Analysis — HL7-FHIR-quality-testing

Status date: 2026-08-07
Branch at time of writing: `master` @ `de8109f` (committed tip 2026-07-29;
large untracked Aug scorecard/cohort/ingest artifacts also present locally)

Part of the VistA-on-FHIR workspace. Ecosystem-level context lives in
`Vista-on-FHIR/docs/PROJECT_OVERVIEW.md`; the cross-repo roadmap is
`Vista-on-FHIR/docs/PATH_FORWARD.md`. Strategy sources:
`docs/STRATEGY.md`, `docs/CQL_DEQM_STATUS.md`,
`docs/RECOVER_CMS165_122_REPORT_LATEST.md`, Connectathon docs under
`docs/connectathon/`.

## Role of this repository

Evidence factory for September Connectathon / US Quality Core claims:

1. Generate and curate Synthea CMS eCQM-focused cohorts
2. Classify membership with official QDM/`cqm-execution` (VSAC expansions)
3. Validate graph-source (`/altfhir`) and VistA-generated (`/fhir`) surfaces
   through hosted Inferno US Quality Core v0.5.0
4. Drive Codex loader/server hardening from scorecard failures
5. Bridge FHIR→QDM for measures that need screening/order semantics
   (e.g. CMS138)

Authoritative demo host: **`devfhir.vistaplex.org`** (`fhirdev22`).

## What is working today

- Full pipeline docs and scripts for 1000-patient Synthea ingest
  (`load=0` graph → enrich → `load=1` VistA) on fhirdev.
- Official 2026 EC eCQM package fetch; first-wave QDM measures available
  (CMS165/122/130/131/138/2/22/68/125).
- VSAC expansions restored after the 2026-07-23 overnight failure
  (CMS165 37/37 and peers documented in recovery report).
- FHIR→QDM patient converter + per-measure CQM package builders;
  selected-18 CQL summaries for the shortlist.
- Hosted Inferno scorecards under `2026/scorecards/inferno/`, including
  recorded **zero-fail** `/fhir` leaf/showcase runs after Codex Condition /
  Encounter / Procedure / CVX / smoking-export / CarePlan / OS5 POV
  `reasonCode` fixes (e.g. committed 2026-07-29 session
  **189 pass / 0 fail / 309 skip**; local untracked 2026-08-03 rerun
  **191 / 0 / 307**).
- Recovery-era selected-18 official CQL: CMS165 **14/14/14** NUMER depth;
  CMS122 **5/5/0**; several peers still NUMER-thin
  (`docs/RECOVER_CMS165_122_REPORT_LATEST.md`).
- Closed-loop scripts/docs for CMS165 (DFN 101115) and CMS122 (DFN 101096).
- Quality AI Consult plan linking this evidence lane to
  `cds-hooks-on-fhir` + rehmp.
- CMS138 FHIR→QDM screening bridge fix with live SETPOP refresh
  (2026-07-29).
- Local untracked Aug artifacts also include rpmsfhir ~1000-patient ingest
  ledgers aligning with `rpms-fhir` bulk-load docs.
- **DEQM Summary MeasureReport path (QRDA-III replacement) started:**
  `docs/deqm-summary/` checklist + IG examples; CMS165v14 prototype
  (official-cql selected-18 **14/14/14/0**) from
  `scripts/build-deqm-summary.py`; structural gate
  `scripts/check-deqm-summary.py`. Full FHIR Validator / receiver POST is
  next (`scripts/deqm-summary-receiver-smoke.sh`).

## Gap analysis

1. **Cohort-scale CQL is still uneven.** Heuristic FHIR preclassifiers are
   not official MeasureReports; several selected-18 measures still show
   low/zero NUMER until clinical enrichment + bridge work lands.
2. **Inferno “green” is leaf/session specific.** Zero-fail runs prove the
   active VistA surface can validate cleanly for chosen DFNs/families;
   skipped resource families and multi-patient selected-18 sessions still
   need deliberate coverage choices — do not imply full US Quality Core
   coverage.
3. **Working tree is very dirty** (dozens of untracked scorecards/artifacts).
   Treat committed docs + dated scorecard paths as the report evidence;
   artifact hygiene remains an open ops task. `CQL_DEQM_STATUS.md` is also
   stale relative to late-July gains.
4. **`us-quality-core-test-kit` is upstream.** Local presets/wrappers live
   primarily under `Vista-on-FHIR/scripts/usqc-*.sh` and
   `Vista-on-FHIR/docs/US_QUALITY_CORE_INFERNO.md` (supporting asset);
   authoritative Connectathon cites are hosted Inferno sessions.
5. **DEQM FHIR-native `$evaluate-measure` path** is secondary; QDM/
   `cqm-execution` is the working official path today.
6. **Live Codex `/fhir` is not yet CQL-complete** for all measures; some
   closed loops still inject filed facts into Synthea-source evaluation.

## Integration points

| Repo / service | Relationship |
|---|---|
| VistA-FHIR-Server-Codex | `/fhir`, `/altfhir`, quality dashboards, Must Support export fixes |
| fhir-triple-store | Heuristic population IPP discovery before CQL |
| cds-hooks-on-fhir | Quality AI Consult + evaluate-cohort VSAC packages |
| rehmp | Clinician quality update UI |
| Synthea / SYN | Cohort generation and intake |
| Inferno hosted / local US Quality Core kit | Conformance scorecards |
