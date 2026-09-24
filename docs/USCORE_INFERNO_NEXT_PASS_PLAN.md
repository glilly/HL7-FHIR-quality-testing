# US Core Inferno — next pass plan (fhirdev)

Status: **done** (2026-09-24) — results in [USCORE_INFERNO_RESCORE_2026-09-24.md](./USCORE_INFERNO_RESCORE_2026-09-24.md).  
Baseline: [USCORE_INFERNO_RESCORE_2026-09-23.md](./USCORE_INFERNO_RESCORE_2026-09-23.md)  
Baseline sessions: [6.1.0 `79Xp8I6E6MH`](https://inferno.healthit.gov/suites/us_core_v610/79Xp8I6E6MH) · [7.0.0 `5HDVWXegFQw`](https://inferno.healthit.gov/suites/us_core_v700/5HDVWXegFQw)  
**This-pass Inferno:** [6.1.0 `9xwqWOCxP7x`](https://inferno.healthit.gov/suites/us_core_v610/9xwqWOCxP7x) · [7.0.0 `DQpAJA49qc`](https://inferno.healthit.gov/suites/us_core_v700/DQpAJA49qc)  
FHIR base: `https://devfhir.vistaplex.org/fhir`  
Cohort (unchanged): `101090,101114,101115,101116,101120,101121,101119,101065,101077`

Results after this pass land in:

- Narrative: `docs/USCORE_INFERNO_RESCORE_YYYY-MM-DD.md` (new dated file; link both ways from this plan and the 09-23 baseline)
- Scorecards: `2026/scorecards/inferno/uscore-v{610,700}-fhirdev-YYYYMMDD.{md,json}`
- Server commit: `VistA-FHIR-Server-Codex` (message references the rescore doc)

---

## Goal

Clear the remaining **code-side fails** without expanding the cohort. Leave large skip families (CareTeam, Coverage, pregnancy, BMI LOINC, etc.) for a later **export** slice unless a one-line builder fix falls out of CapStmt/Observation work.

Target (leaf-oriented, approximate):

| Suite | Now | Aim |
| --- | ---: | ---: |
| 6.1.0 fail | 14 | ≤ 5 (DAR + harness noise OK) |
| 7.0.0 fail | 23 | ≤ 8 (Location should flip if post-score fix holds) |
| Skips | 225 / 296 | unchanged unless we intentionally ship one export |

---

## Phase A — CapabilityStatement (multi-fail, quick)

Live `/fhir/metadata` today:

- `date` is a **FileMan number** (`3260924.012059`) → Inferno: *primitive value must be a string*
- No `instantiates` / US Core IG URI
- Thin `rest.resource` list; **0** `supportedProfile` entries

**Do:**

1. Emit `date` via `$$FM2FHIR^C0FHIRBU($$NOW^XLFDT)` (or `$$NOWISO^C0FQRPT`) in `ALTCAP^C0FHIR`.
2. Set `instantiates` (or `implementationGuide`) to US Core 6.1.0 and/or 7.0.0 package URIs Inferno expects.
3. Add a minimal `supportedProfile` list for resources we already pass (Patient, Condition, Encounter, Observation smoking/lab/vitals, Immunization, DiagnosticReport lab, DocumentReference, MedicationRequest, Location, Organization, Practitioner).

**Verify:** `curl -sS https://devfhir.vistaplex.org/fhir/metadata | jq '.date,.instantiates,.rest[0].resource|length'`

---

## Phase B — Observation tagging (biggest fail cluster)

Known live shapes that fail Inferno:

| Resource | Problem |
| --- | --- |
| `Observation/101090-quality-cms138-smoking-status` | `category=laboratory` + `us-quality-core-observation-lab`; needs **social-history** + `us-core-smokingstatus` |
| `Observation/101090-quality-cms122-hba1c` (and kin) | `meta.profile` points at `http://fhir.org/guides/onc/us-quality-core/...` — Inferno cannot resolve → emit **US Core** lab / clinical-result / simple-observation URLs (dual-profile OK) |
| Graph path `EMIT^C0FHIRLG` | Forces **laboratory** on LOINC `72166-2` for CQL — breaks smokingstatus profile |

**Do:**

1. In `EMIT^C0FHIRLG` (and any quality overlay that stamps smoking): if code is `72166-2`, set category `social-history` and profile `us-core-smokingstatus` (do not force laboratory).
2. Map/replace unknown `us-quality-core-observation-*` profile URLs with the matching `hl7.org/fhir/us/core` StructureDefinitions on read/cache emit for Inferno-facing bundles.
3. Keep quality measure CQL working: if lab retrieve needs tobacco as lab, use a **separate** synthetic or keep both categories only where US Core allows — prefer correct US Core smoking shape for `/fhir` export.

**Verify:** fetch the two Observation ids above; category/profile match US Core; smokingstatus + lab validation groups improve on rescore.

---

## Phase C — Location (7.0 only)

Address/name search OO was fixed **after** the 09-23 scored run.

**Do:** re-run Location group (or full 7.0). No new design unless still red.

---

## Phase D — Out of scope this pass

| Item | Why |
| --- | --- |
| Add DFNs `101122` / `101076` | Live scan: no CareTeam/Coverage/BMI/pregnancy/ped LOINCs on fhirdev; cohort already has CarePlan/Imm/smoking |
| CareTeam / Coverage / Goal / Device / MedDispense export | Skip track — needs builders + VistA source, not CapStmt |
| BMI / pregnancy / occupation / ped vitals | Same; use HL7 US Core `examples.json.zip` + Azure USCore6/7 test bundles as **golden shapes** when that export slice starts |
| DiagnosticReport `synthetichealth` errors | Inferno harness constant |
| DAR | Needs DAR data or deliberate absent-reason support |

**Reference samples (for a later export pass, not this one):**

- HL7: [STU6.1 examples](https://hl7.org/fhir/us/core/STU6.1/examples.html) · [examples.json.zip](https://hl7.org/fhir/us/core/STU6.1/examples.json.zip)
- Azure loadable packs: [USCore6-test-data](https://github.com/Azure-Samples/azure-health-data-and-ai-samples/tree/main/samples/USCore6-test-data), [USCore7-test-data](https://github.com/Azure-Samples/azure-health-data-and-ai-samples/tree/main/samples/USCore7-test-data)
- Already loaded Quality Core pack → `CHALMERS,PETER` / `101090` — proves intake ≠ Inferno-visible export for hard types

---

## Execution checklist

1. [x] Implement Phase A + B in `VistA-FHIR-Server-Codex` (+ newest-cache search in `C0FWCAC`)
2. [x] `./scripts/fhirdev-codex-sync.sh` → container `fhirdev22`
3. [x] `refresh=1` on the nine DFNs
4. [x] Smoke CapStmt date string + smoking Observation shape
5. [x] Hosted Inferno US Core 6.1.0 + 7.0.0 FHIR API — `9xwqWOCxP7x` / `DQpAJA49qc`
6. [x] Write scorecards under `2026/scorecards/inferno/`
7. [x] Write `docs/USCORE_INFERNO_RESCORE_2026-09-24.md`; mark this plan **done**
8. [ ] Commit quality-testing docs/scorecards; Codex commit for M changes

Commands (evidence gate):

```bash
# after sync
curl -sS https://devfhir.vistaplex.org/fhir/metadata | jq -r '.date,.fhirVersion'
curl -sS 'https://devfhir.vistaplex.org/fhir/Observation/101090-quality-cms138-smoking-status' \
  | jq '{category, profile: .meta.profile, code}'

# rescore via existing harness
python3 scripts/inferno-run.py   # (US Core 6.1 / 7.0 FHIR API, nine DFNs)
python3 scripts/summarize-inferno.py
```

---

## Related

- Kit fit: [INFERNO_QA_TEST_KIT_FIT_2026-09-18.md](./INFERNO_QA_TEST_KIT_FIT_2026-09-18.md)
- Prior CMS165 plan pattern: [INFERNO_FHIRDEV_CMS165_REMAINING_ERRORS_AND_PLAN.md](./INFERNO_FHIRDEV_CMS165_REMAINING_ERRORS_AND_PLAN.md)
- Codex CapStmt builder: `ALTCAP^C0FHIR` in `VistA-FHIR-Server-Codex`
