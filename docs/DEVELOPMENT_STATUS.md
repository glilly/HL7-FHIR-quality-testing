# Development Status and Gap Analysis — HL7-FHIR-quality-testing

Status date: 2026-10-27 (previous: 2026-08-07, with an inline 2026-10-14
update)
Branch at time of writing: `master` (clean, in sync with origin; the nightly
lane commits `chore(nightly): quality evidence` here every night, so
`git pull --ff-only` before committing)

Part of the VistA-on-FHIR workspace. Ecosystem-level context lives in
`Vista-on-FHIR/docs/PROJECT_OVERVIEW.md`; the cross-repo roadmap is
`Vista-on-FHIR/docs/PATH_FORWARD.md`. Strategy sources:
`docs/STRATEGY.md`, `docs/CQL_DEQM_STATUS.md`,
`docs/RECOVER_CMS165_122_REPORT_LATEST.md`, Connectathon docs under
`docs/connectathon/`.

## Role of this repository

Evidence factory for the January 2027 Connectathon / US Quality Core claims:

1. Generate and curate Synthea CMS eCQM-focused cohorts
2. Classify membership with official QDM/`cqm-execution` (VSAC expansions)
3. Validate graph-source (`/altfhir`) and VistA-generated (`/fhir`) surfaces
   through hosted Inferno US Quality Core v0.5.0
4. Drive Codex loader/server hardening from scorecard failures
5. Bridge FHIR→QDM for measures that need screening/order semantics
   (e.g. CMS138)

Authoritative demo host: **`devfhir.vistaplex.org`** (`fhirdev22`).
Inferno showcase host: **`showfhir.vistaplex.org`** (container `Show`).

## Since 2026-08-07

**The US Quality Core suite is green.** On 2026-10-25, hosted Inferno ran
US Quality Core v0.5.0 against `https://showfhir.vistaplex.org/fhir` with
the 34 ZZ charts (DFNs 101258–101291) and passed **438 of 438 tests, 0
skipped, 498 of 498 rows** (session
[2yWbChvQkWt](https://inferno.healthit.gov/suites/us_quality_core_v050/2yWbChvQkWt);
scorecard `2026/scorecards/inferno/2026-10-25-showfhir-rebuild.md`). The
34 served Bundles are published at
`2026/patients/show-quality-core-2026-10-25/` with a README, a browser link
per patient (GitHub Pages tjson FHIR browser), and one zip. Every given
name begins with ZZ; that prefix is part of the record and marks the chart
as synthetic.

The ladder that got there, all with zero failures from pass 2 on
(`docs/USQC_INFERNO_SKIP_PLAN.md`):

| Date | Host | Patients | Pass / fail / skip of 498 | Session |
|---|---|---|---|---|
| 10-12 | fhirdev `/fhir` | ZZ 101130–101153 | 173 / 0 / 325 (baseline after step 0) | `ii7aiQNhNnY` |
| 10-12 | fhirdev | same | 246 / 0 / 252 (pass 2) | `fe4WObX47az` |
| 10-13 | fhirdev | same | 352 / 0 / 146 (pass 3) | `ecpMXM0JLJo` |
| 10-14 | fhirdev | 101130–101163 (+10 gap charts) | **446 / 0 / 52 (89.6%)** (pass 4) | `88Gj3JAQF4o` |
| 10-14 | iris2 | 16–49 | 442 / 0 / 56 (pass 3) | `lXvArJeWycf` |
| 10-18 | iris2 (first weekly) | 16–49 | 443 / 5 / 50 | `lsTYIZeIw3E` |
| 10-24 | showfhir (rebuilt) | 101258–101291 | 471 / 15 / 12 | `e95iOBSHNCA` |
| 10-25 | showfhir (rebuilt again) | 101258–101291 | **498 / 0 / 0** | `2yWbChvQkWt` |

Each step paired a chart change (`WVEHR-on-FHIR/scripts/make-zz-patients.py`,
the ten gap charts, Inferno example-carriers folded into the ZZ-Vera-Ellis /
ZZ-Will-Ford / ZZ-Ivy-Ford bundles) with a Codex read-path change (CVX/LOINC
displays, Observation `date` by effective time, graph-carried Coverage /
CareTeam / RelatedPerson / Goal / CarePlan / ServiceRequest / Provenance,
`_include` Medication, pediatric / pregnancy / occupation / not-done groups,
`IMMSTATUSREASON`, MedicationAdministration code indexing) and, where a
display was wrong, a cds-hooks fix (CMS130 FIT LOINC, 10-12).

Other changes in the period:

- **Weekly iris2 Inferno lane** (`scripts/weekly-iris2-inferno.sh`,
  Sundays; evidence `2026/scorecards/inferno/weekly/`). Fails on any
  failure or on n < 498; skips are allowed.
- **Daily quality rotation** (`scripts/daily-quality-rotate.sh`) rotates
  showfhir, fhirdev, vehu10, rpms-candidate, rpmsfhir, wvehr by day of
  year; evidence `2026/scorecards/daily-quality/`; since 10-24 it skips a
  local host whose port is not listening instead of failing the night.
- **Official CQL on the rebuilt Show** (10-25, after cohort store + reeval):
  CMS2 126/126/40/0, CMS165 34/34/21/1, CMS122 31/31/8/0, CMS130
  83/83/56/1, CMS125 68/68/16/0, CMS138 106/106/83/1 (IPP/DENOM/NUMER/EXCL).
- Coding-gap scans and plans for fhirdev, RPMS, Iris, and WVEHR
  (`docs/*CODING_GAP_PLAN*`, 09-24/25); the fhirdev Quality Core suite at
  89.6% (10-14) and the ZZ scorecards for US Core 7.0 on `/altfhir` (10-11).

## What is working today

**Update 2026-10-14.** US Quality Core v0.5.0 on fhirdev `/fhir`, ZZ patients `101130`–`101163`: **446 pass, 0 fail, 52 skip (89.6% of 498)**. Session [88Gj3JAQF4o](https://inferno.healthit.gov/suites/us_quality_core_v050/88Gj3JAQF4o). Step log: `docs/USQC_INFERNO_SKIP_PLAN.md`. Scorecard: `2026/scorecards/inferno/usquality-v050-fhirdev-fhir-zz-20261014-pass4.json`. The same night the six dashboards were reevaluated; denominator-not-numerator is about a quarter on CMS122, CMS125, CMS130, CMS138, and CMS165, and 13 of 31 on CMS2. Superseded on Show by the 2026-10-25 green run above.

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
- **DEQM Summary MeasureReport path (QRDA-III replacement) Phase 2 gated:**
  `docs/deqm-summary/` checklist + IG examples; CMS165v14 prototype
  (official-cql selected-18 **14/14/14/0**, measure `|14.0.000`) from
  `scripts/build-deqm-summary.py`; structural gate
  `scripts/check-deqm-summary.py`; Inferno validator + DEQM 5.0.0 and
  `deqm-test-server` POST via
  `scripts/deqm-summary-receiver-smoke.sh --validate --docker`
  (evidence `docs/deqm-summary/results/CMS165v14-phase2-smoke.md`).
  Phase 3: batch builder for selected-18 official-cql shortlist
  (7 Summary MeasureReports + multi Bundle); SETPOP publisher now emits
  DEQM-profiled `summary.json` + copies official freeze to
  `summary-deqm.json`; Individual DEQM spike for CMS165 DFN 101115;
  Connectathon packet includes `#cql` Zulip draft + Rockville checklist
  (`docs/deqm-summary/CONNECTATHON_PACKET.md`).

## Gap analysis

1. **Cohort-scale CQL is still uneven.** Heuristic FHIR preclassifiers are
   not official MeasureReports; several selected-18 measures still show
   low/zero NUMER until clinical enrichment + bridge work lands.
2. **Inferno “green” is cohort- and host-specific.** The 2026-10-25 run is
   the full US Quality Core v0.5.0 server suite with no skips, but it is
   green on Show with those 34 charts. fhirdev (89.6%) and iris2 (weekly,
   5 fails on 10-18) are not yet at the same point, and a new host or
   cohort will skip again until it carries the example resources. State
   the host and session when citing it.
3. ~~**Working tree is very dirty.**~~ Closed: the tree is clean and the
   nightly lane commits evidence daily. `CQL_DEQM_STATUS.md` is still stale
   relative to the DEQM Phase 3 and October gains.
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
