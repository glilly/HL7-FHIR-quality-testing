# Connectathon packet — DEQM Summary MeasureReport reporter

Status date: 2026-08-08 (attendance decision **2026-08-20**)  
Track target: prepare for **January 2027 virtual** CMS Quality Reporting
(QPP & HQR E2E); September Rockville = **shadow only** (not attending).
See `Vista-on-FHIR/docs/CONNECTATHON_43_SHADOW_AND_JANUARY_PLAN.md`.

## Role

VistaPlex acts as a **DEQM Summary MeasureReport reporter** (QRDA-III
replacement), not a Cypress/QRDA submitter for this track. The same
reporter codebase serves **both VistA-lineage (devfhir) and RPMS-lineage
(rpmsfhir) data** — see the RPMS lane below.

## Pinned stack

| Piece | Pin |
|---|---|
| DEQM IG | STU5 **5.0.0** |
| Profile | `…/StructureDefinition/summary-measurereport-deqm` |
| Evaluation path | QDM / `cqm-execution` → Summary MeasureReport builder |
| Local receiver proof | `projecttacoma/deqm-test-server` |
| Local profile gate | Inferno `fhir-validator-service` + DEQM package (`DISABLE_TX=true`) |

## Measures in this packet (official-cql selected-18)

Counts from `official-cql-selected18-counts.tsv` /
`RECOVER_CMS165_122_REPORT_LATEST.md` — do not invent NUMER depth.

| Measure | IPP | DENOM | NUMER | DENEX | Notes |
|---|---:|---:|---:|---:|---|
| CMS165v14 | 14 | 14 | 14 | 0 | Anchor; NUMER depth proven |
| CMS122v14 | 5 | 5 | 0 | 0 | Honest zero NUMER |
| CMS130v14 | 9 | 9 | 0 | 0 | Honest zero NUMER |
| CMS138v14 | 1 | 0 | 0 | 0 | DENOM empty |
| CMS2v15 | 6 | 6 | 0 | 0 | Honest zero NUMER |
| CMS125v14 | 0 | 0 | 0 | 0 | n=9 subset |
| CMS22v14 | 6 | 6 | 0 | 2 | DENEX=2 |

Artifacts:

- Per-measure: `prototypes/{CMS}-summary-deqm.json`
- Multi POST: `prototypes/Bundle-selected18-summary-transaction.json`
- Phase 2 CMS165 evidence: `results/CMS165v14-phase2-smoke.md`
- RPMS lane: `prototypes/rpms/CMS165v14-rpms-summary-deqm.json` +
  `results/CMS165v14-rpms-phase2-smoke.md`

## RPMS lane (in progress)

RPMS is IHS's VistA-derived EHR; its native aggregate quality report is
**CRS (Clinical Reporting System, `BQI`)** — annual GPRA
numerator/denominator reports transmitted facility → Area. DEQM Summary
MeasureReport is the same modernization story for CRS/GPRA that it is
for QRDA-III, so the Connectathon claim is: **one open-source reporter
emits DEQM Summary MeasureReports from both VistA and RPMS**.

Status:

| Step | State |
|---|---|
| `rpmsfhir.vistaplex.org` FHIR server + REST adapter (vendev15 `:5177`) | Up; ~1,000 Synthea patients loaded 2026-08-04 (`2026/patients/rpmsfhir-ingest-1000-20260804.tsv`) |
| Selected-18 cohort on rpmsfhir | **Loaded 19/19** 2026-08-08 (DFNs **1143–1161**); ledger `2026/patients/rpmsfhir-ingest-selected18-20260808.tsv`; spot-checked Patient `_id`/read + Observation search via tunnel |
| Official CQL runs (FHIR→QDM / cqm-execution) against rpmsfhir | **Done 2026-08-08** on round-trip exports (`GET /fhir?dfn=`), n=19, hierarchy-gated, seven measures: CMS165 **19/19/13/1**, CMS122 **10/10/4/0**, CMS130 **15/15/1/0**, CMS2 **19/19/0/0**, CMS22 **19/19/0/19**, CMS138 **19/19/19/0**, CMS125 **11/11/0/0**. Counts `rpms-roundtrip-counts.tsv`; per-patient `2026/cohorts/rpms/{CMS}/cql/` |
| RPMS-labeled Summary MeasureReports (distinct `reporter` Organization) | **Done ×5** — `prototypes/rpms/{CMS}-rpms-summary-deqm.json` (`Organization/vistaplex-rpms-demo`, `build-deqm-summary.py --reporter rpms`); validator 0 actionable errors each; receiver **201 Created** each. Evidence `results/CMS165v14-rpms-phase2-smoke.md` + `results/rpms-multi-measure-smoke.md` |
| Cross-platform equivalence demo (same patients, same CQL, two systems) | Partial: CMS165 — 13 of devfhir's 14 NUMER patients match; the 14th is DENEX on the RPMS round-trip. RPMS lane IPP/DENOM (and CMS122/130 NUMER) higher because the rpmsfhir collection Bundle round-trips more data; CMS22 DENEX=19 is coherent (hypertension cohort excluded from BP screening). Keep lanes separate; never merge counts |

## Third lane: fhir.vistaplex.org (production reference)

2026-08-08: `fhir.vistaplex.org` (the third documented endpoint,
WorldVistA production reference) was upgraded to the current quality
stack and loaded with the **same 19-patient cohort** (DFNs
**1643–1661**). Official CQL on its round-trip exports, seven measures,
hierarchy-gated: CMS165 **16/16/15/1**, CMS122 **9/9/9/0**, CMS130
**15/15/0/0**, CMS2 **19/19/0/0**, CMS22 **19/19/2/16**, CMS138
**19/19/19/0**, CMS125 **11/11/0/0** — after the upgrade this is the
best VistA-lineage round-trip surface. Counts
`fhirprod-roundtrip-counts.tsv`; full upgrade story + three-server
comparison table `results/three-server-comparison-20260808.md`.

Summary MeasureReports ×7 built with a third reporter Organization
(`Organization/vistaplex-prod-demo`, `build-deqm-summary.py --reporter
fhirprod`) under `prototypes/fhirprod/`; validator 0 actionable errors
each, receiver **201 Created** each; published alongside the VistA and
RPMS lanes at
`https://devfhir.vistaplex.org/filesystem/quality/measurereports/fhirprod/index.json`.
Demo claim upgrade: **one open-source reporter, three reporting
organizations, three FHIR servers, one CQL pipeline.**

## Known limitations (state at Connectathon)

1. Measure canonicals are **placeholders**
   (`https://ecqi.healthit.gov/ecqm/ec/{CMS}|{ver}`) until CMS FHIR dQM
   Measure packages are pinned for EC.
2. Production path remains **FHIR→QDM / cqm-execution**; FHIR-native
   `$evaluate-measure` is stretch.
3. Stratifiers not emitted until CQL evidence supports them.
4. Inferno validator may emit known DEQM IG noise for R5
   `extension-MeasureReport.supplementalData` slicing on
   `extension-measureScoring` (also present on IG golden examples).
5. RPMS lane uses **Synthea synthetic data** loaded into an RPMS-shaped
   FHIR server — no real IHS clinical data, and no CRS/`BQI` extraction;
   RPMS enters the pipeline at the FHIR layer, same as VistA.
6. RPMS counts will be whatever the CQL run produces (honest zero-NUMER
   stays zero), reported under a distinct RPMS `reporter` Organization.

## How peers can pull / POST

```bash
# Build
python3 scripts/build-deqm-summary-batch.py --check

# Validate + POST CMS165 (or swap path)
./scripts/deqm-summary-receiver-smoke.sh \
  docs/deqm-summary/prototypes/CMS165v14-summary-deqm.json \
  --validate --docker

# Multi-measure POST
curl -fsS -X POST http://127.0.0.1:3000/4_0_1 \
  -H 'Content-Type: application/fhir+json' \
  --data-binary @docs/deqm-summary/prototypes/Bundle-selected18-summary-transaction.json
```

Public host (when published):

- `https://devfhir.vistaplex.org/filesystem/quality/measurereports/{CMS}/summary-deqm.json`
- Dashboard: `https://devfhir.vistaplex.org/fhir-quality-dashboards/{CMS}`
- Auth: none for filesystem JSON; dashboard HTML is open on fhirdev

Local `deqm-test-server` also accepts anonymous POSTs on `:3000`.

## Live demo script (10-minute loop, then run it twice)

The demo walks the DEQM exchange pattern end to end — clinical data
source → measure evaluation → Summary MeasureReport → validation →
receiver — live, from public endpoints. Then it repeats from RPMS.

1. **Data, not slides.** Pull one patient's collection Bundle live from
   the in-M FHIR server:

   ```bash
   curl -s 'https://devfhir.vistaplex.org/fhir?dfn=101115' \
     -H 'Accept: application/fhir+json' | jq '.entry | length'
   ```

2. **Evaluate live** (official CMS CQL, VSAC-expanded value sets;
   per-patient IPP/DENOM/NUMER/DENEX prints as it runs). Manifest is
   `bundle_path<TAB>dfn` rows over the bundles fetched in step 1
   (RPMS-lane example: `2026/cohorts/rpms/CMS165v14/eval-manifest.tsv`):

   ```bash
   node scripts/evaluate-cqm-manifest.js CMS165v14 \
     --manifest /tmp/demo-bundles/eval-manifest.tsv \
     --out-dir /tmp/demo-cql
   ```

3. **Build the Summary MeasureReport** (QRDA-III replacement artifact)
   from the counts just produced:

   ```bash
   python3 scripts/build-deqm-summary.py --cms CMS165v14 \
     --ipp <IPP> --denom <DENOM> --numer <NUMER> --denex <DENEX> \
     --cohort-size <N> --mode official-cql --source "live demo" \
     --out-dir /tmp/demo-reports
   ```

4. **Gate it** — validator (DEQM 5.0.0 profile; expect 0 actionable
   errors, explain the known IG supplementalData slice noise) then
   **POST to the receiver** and show the `201 Created`:

   ```bash
   ./scripts/deqm-summary-receiver-smoke.sh \
     /tmp/demo-reports/CMS165v14-summary-deqm.json --validate --docker
   ```

   At the event, swap the local receiver for the track's reference
   receiver or a peer system — that POST is the Connectathon objective;
   local `deqm-test-server` is the rehearsed fallback.

5. **The dual-platform moment.** Repeat 1–4 from
   `https://rpmsfhir.vistaplex.org/fhir?dfn=1143` with
   `--reporter rpms`. Same reporter codebase, two systems, two reporter
   Organizations; 13 of devfhir's 14 CMS165 NUMER patients match (the
   14th is a denominator exclusion on the RPMS round-trip). Present the
   IPP/DENOM differences as a finding (round-trip fidelity differs by
   server), not a discrepancy to hide.

Talking points along the way: honest-counts discipline (zero NUMER stays
zero), CRS/GPRA modernization framing for IHS, and the known-limitations
list below stated up front.

## Coordination

- Strategy home: `Vista-on-FHIR/docs/DEQM_SUMMARY_MEASUREREPORT_QRDA3_REPLACEMENT_STRATEGY.md`

### `#cql` Zulip draft (ready to paste)

```
Hi #cql — VistaPlex (open-source VistA-on-FHIR) is preparing for the
Sep 19–25 2026 Rockville Connectathon as a **DEQM Summary MeasureReport
reporter** (QRDA-III replacement path).

Pinned: DEQM STU5 5.0.0 summary-measurereport-deqm. First measure CMS165v14
(official-cql selected-18 14/14/14/0); shortlist also has CMS122/130/138/2/125/22
with honest zero-NUMER where CQL has no depth yet. Evaluation today is
FHIR→QDM + cqm-execution; FHIR-native $evaluate is stretch.

We also run an RPMS-lineage FHIR server (IHS's VistA derivative), aiming to
demo the same reporter emitting Summary MeasureReports from both VistA and
RPMS data — the DEQM path as a CRS/GPRA modernization story for IHS/tribal
sites (synthetic data only).

Looking for the Quality Reporting / DEQM track contact and any preferred
receiver CapabilityStatement for Summary MeasureReport POST. Packet:
github.com/glilly/HL7-FHIR-quality-testing (docs/deqm-summary/).
```

### Registration / shadow checklist (updated 2026-08-20)

1. [x] ~~Register for Rockville Sep 2026~~ **Not attending** (in-person only)
2. [ ] Register for **January 12–15, 2027** virtual Connectathon when open
3. [ ] Join the **CMS Quality Reporting: QPP & HQR End-to-End Submission**
      track for January (same track family as Sep) —
      <https://confluence.hl7.org/spaces/FHIR/pages/477660436/2026+-+09+CMS+Quality+Reporting+QPP+HQR+End-to-End+Submission+Track>
4. [ ] Email CMS track lead (shadow interest + January intent); post `#cql`
      intro if Zulip allows non-attendees (draft above). Draft:
      `Vista-on-FHIR/docs/emails/2026-08-bridget-calvert-cms-quality-track.md`.
      Weekly upstream keep-up:
      `Vista-on-FHIR/docs/CONNECTATHON_UPSTREAM_WATCHLIST.md`.
5. [x] Published `summary-deqm.json` set to fhirdev 2026-08-08 via
      `scripts/fhirdev-publish-measurereports.sh --build`, now including the
      RPMS lane: <https://devfhir.vistaplex.org/filesystem/quality/measurereports/rpms/index.json>
6. [x] Individual MeasureReport spike demo-ready
      (`CMS165v14-Patient-101115-individual-deqm.json`, QRDA-I analogue):
      validated 2026-08-08 against `indv-measurereport-deqm` (0 actionable
      errors, known IG slice noise only); receiver POST **201 Created**
7. [x] RPMS lane CMS165: cohort loaded, official CQL run, RPMS-labeled
      Summary MeasureReport validated + accepted (see RPMS lane section)
8. [x] RPMS lane extended to CMS122/130/2/22 and CMS138/125: round-trip
      CQL counts, reports validated + accepted
      (`results/rpms-multi-measure-smoke.md`) — full seven-measure set
9. [x] Timed dry-run of the live demo script (both lanes) —
      `results/demo-dryrun-20260808.md` (~30 s VistA loop, ~45 s RPMS
      loop; found + fixed population-hierarchy counting bug)
10. [ ] Optional stretch: host `deqm-test-server` publicly so VistaPlex
      can also act as receiver for peers (doubles scorecard surface)
11. [ ] Shadow: freeze dated Inferno US Quality Core scorecards for the
      packet cohort; short gap note vs `cqframework/dqm-content-cms-2026`
