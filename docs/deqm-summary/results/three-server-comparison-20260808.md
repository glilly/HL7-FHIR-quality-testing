# Three-server upgrade + cohort comparison — fhir / devfhir / rpmsfhir

Date: 2026-08-08

Goal: bring `fhir.vistaplex.org` (production reference, WorldVistA) up to
the current quality stack, load the shared selected-18 + showcase cohort
onto it, and compare official CQL results across all three documented
endpoints.

## What was wrong on fhir.vistaplex.org

The deploy-quality-all smoke *passed* before any work (dashboards, C0X
presets, index all green), but the ingest/export pipeline was badly
behind. Root causes found, in order:

1. **Root-owned GT.M object files.** `/home/osehra/p/V6.3-002_x86_64/*.o`
   were owned by root, so every `zlink` from deploy scripts (running as
   `osehra`) silently failed and the listener kept executing years-old
   compiled code even after source syncs. Fixed with `chown -R osehra`,
   plus `touch *.m` (docker cp preserves old mtimes, which also
   suppresses recompilation) and a full recompile.
2. **Stale SYN loader routines.** The container had 75 old SYN* routines
   vs devfhir's current 50; the old `SYNDHP61` mishandled
   `$$MAP^SYNDHPMP` results (treated `1^I10` status prefix as the code),
   so problem filing fell back to ICD-10 `R69.` placeholders. Synced all
   50 from the devfhir container (backup:
   `fhir:/home/osehra/syn-backup-20260808.tar`).
3. **Missing SYN mapping tables.** Only 3 of 10 `^SYN("2002.030",*)`
   maps existed; `sct2cpt`, vitals, health-factor, mental-health maps
   were absent and `sct2os5` had 90 entries vs devfhir's 1,041. Loaded
   2,339 nodes from devfhir; all 10 maps now match.
4. **Stale Lexicon SNOMED→ICD-10 mapping content.** The decisive bug:
   `GETASSN^LEXTRAN1(59621000,5217693)` returned **R69.** on fhir but
   **I10.** on devfhir — file 757.33 had 745,287 nodes vs devfhir's
   836,663 (older Lexicon patch level). Replaced `^LEX(757.33)` with
   devfhir's copy (836,663 nodes; backup
   `fhir:/tmp/lex33-backup.pairs.gz`).
5. **Listener restart trap.** `d go^%webreq` JOBs fail with
   `%GTM-E-JOBFAIL / ENO13` unless run from a writable cwd; earlier
   deploys' restart step had silently never restarted the listener.
   Restarting from `/tmp` works.

## Cohort load

The same 19 Synthea patients as the rpmsfhir lane (selected-18 +
showcase; manifest `2026/patients/rpmsfhir-selected18-manifest.tsv`)
were loaded via `/addpatient` → **DFNs 1643–1661** (Audrea = 1652; her
28.9 MB bundle needs the SSH tunnel to port 9080, same as rpmsfhir).
After the fixes above, all 19 were re-filed in place via
`/updatepatient?dfn=` (16 min total). Residual R69 problem rows from the
first, broken filing remain on the problem lists; they match no measure
value set and do not affect CQL.

## Three-server official CQL counts (IPP/DENOM/NUMER/DENEX, hierarchy-gated)

Same measures, same CQL, same evaluator; each lane evaluated on that
server's own round-trip `GET /fhir?dfn=` exports.

| Measure | fhir (n=19) | rpmsfhir (n=19, same cohort) | devfhir (n=20 official-cql DFNs, incl. showcase) |
|---|---|---|---|
| CMS165v14 | 16/16/15/1 | 19/19/13/1 | 8/8/8/0 |
| CMS122v14 | 9/9/9/0 | 10/10/4/0 | 6/6/6/0 |
| CMS130v14 | 15/15/0/0 | 15/15/1/0 | 16/16/0/0 |
| CMS2v15 | 19/19/0/0 | 19/19/0/0 | 20/20/0/0 |
| CMS22v14 | 19/19/2/16 | 19/19/0/19 | 20/20/5/8 |
| CMS138v14 | 19/19/19/0 | 19/19/19/0 | 20/20/1/0 |
| CMS125v14 | 11/11/0/0 | 11/11/0/0 | 11/11/3/0 |

Caveat: the devfhir column is the 20-DFN official-cql SETPOP cohort
(selected-18 lineage + showcase), not the identical 19-bundle load, so
compare shapes rather than exact patients.

Counts: `fhirprod-roundtrip-counts.tsv`, `rpms-roundtrip-counts.tsv`;
per-patient results under `2026/cohorts/{fhirprod,rpms}/{CMS}/cql/`.

## Findings

- **After the upgrade, fhir has the best VistA-lineage round-trip
  fidelity.** Freshly re-filed data with current routines beats
  devfhir's own round-trip on CMS165 (16/16/15 vs 8/8/8) and CMS138
  (NUMER 19 vs 1). devfhir's older filed data predates several loader
  fixes — the same class of drift just fixed on fhir, at a smaller
  scale.
- rpmsfhir still leads on CMS165 IPP (19 vs 16): three fhir patients
  lack a qualifying encounter+diagnosis pair on the round-trip surface.
- CMS125 NUMER=0 on both fhir and rpmsfhir vs 3 on devfhir: mammography
  evidence still does not survive the fhir/rpmsfhir ingest→export path
  (procedure filing gaps; `PRCADD failed: -1` on fhir is a remaining
  known issue).
- Honest zeros persist for CMS2 (depression screening) on all three.

## deploy-quality-all status

`fhir.vistaplex.org` is the `fhirprod` target and **is already in the
default target list** of
`VistA-FHIR-Server-Codex/scripts/deploy-quality-all.sh`
(`fhirdev vehu10 rpms-candidate rpmsfhir fhirprod`). The deploy +
`smoke-quality-host.sh` gate ran green after the upgrade
(`SMOKE OK: fhirprod`, index pop=1633). The root-owned-object and
listener-cwd traps above are the reason past deploys appeared to
succeed without taking effect.

## Remaining known gaps on fhir

- Procedure filing errors (`PRCADD failed: -1`) — CPT/OS5 filing path
  needs its own session; affects CMS130 colonoscopy NUMER.
- Lab DiagnosticReport panels partially filed (12 loaded / 52 error per
  patient typical); A1c depth was still sufficient for CMS122 NUMER=9.
- Many Synthea SNOMED codes remain unmappable via Lexicon on all
  WorldVistA lanes (same error class as devfhir; expected).
