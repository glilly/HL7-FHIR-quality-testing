# Connectathon packet — DEQM Summary MeasureReport reporter

Status date: 2026-08-07  
Track target: HL7 FHIR Connectathon **Sep 19–25, 2026 Rockville**
(“FHIR Quality Reporting with DEQM” / related quality tracks).

## Role

VistaPlex acts as a **DEQM Summary MeasureReport reporter** (QRDA-III
replacement), not a Cypress/QRDA submitter for this track.

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

Looking for the Quality Reporting / DEQM track contact and any preferred
receiver CapabilityStatement for Summary MeasureReport POST. Packet:
github.com/glilly/HL7-FHIR-quality-testing (docs/deqm-summary/).
```

### Rockville registration checklist

1. [ ] Register for HL7 FHIR Connectathon **Sep 19–25, 2026 Rockville**
2. [ ] Confirm / join **FHIR Quality Reporting with DEQM** (or successor) track
3. [ ] Post `#cql` intro (draft above)
4. [ ] Publish `summary-deqm.json` set to fhirdev via
      `scripts/fhirdev-publish-measurereports.sh --build`
5. [ ] Optional: bring Individual MeasureReport spike
      (`CMS165v14-Patient-101115-individual-deqm.json`) for QRDA-I analogue demo
