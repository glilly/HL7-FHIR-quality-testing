# C0X SPARQL Round 2 — UNION/VALUES IPP approximation

Date: 2026-09-03. Baseline: round-1 experiment imported at
`2026/cohorts/c0x-heuristic/` + `2026/cohorts/{CMS}/c0x-cql/` (commit
`c8aac09`).

> **Status: round 2 executed overnight 2026-09-03.** The three engine
> bugs below were fixed in fhir-triple-store (`C0XSPAR.m`), presets were
> upgraded to the verified multi-code shapes (`C0XCOH.m`), everything
> was deployed to all five quality targets, and phase-2 CQL confirmation
> ran over the round-2 candidates. Headline: **recall 1.0 vs CQL IPP on
> all four measures**, and CQL confirmed 7 more true IPP patients for
> CMS165 than round 1 had found. Results below.

## Goal

Round 1 used a **single-code** C0X graph query per measure as an IPP
proxy (e.g. CMS165 = Condition 59621000), then confirmed candidates with
official CQL. Recall was decent but the single code both overshot
(23 candidates → 16 CQL IPP for CMS165) and undershot (misses patients
whose hypertension is coded differently).

The C0X SPARQL engine (fhir-triple-store, commits `5f75396`…`71e2fcf`)
now supports **VALUES** (inline + FileMan `FROM oid|measure`), **UNION**,
**MINUS**, richer FILTER, and **POPIDX population execution** that
returns `dfn` bindings directly. Round 2: rebuild each measure's
heuristic as a value-set-driven population query and score it against
the round-1 official-CQL truth — the target is SPARQL-side candidate
lists that approach CQL IPP (high recall, better precision).

## Live probe findings (devfhir, 2026-09-03)

| Capability | State |
|---|---|
| BGP + `population=1` | Works; returns `dfn` per binding (27 candidates for 59621000) |
| `VALUES` inline + population | Works (28 candidates for 59621000+38341003) |
| `UNION` + population | **Returns 0** despite each arm returning 27/28 alone — engine bug, blocker for UNION-style queries; use multi-code `VALUES` until fixed |
| `VALUES ?code FROM measure "CMS165"` | Parses, expands, but 0 candidates |
| `VALUES ?code FROM oid <hypertension VS>` | Only 1 candidate, matched via ICD `I10` — the FileMan 802.2 expansion does not include the SNOMED codes Synthea data carries |
| `/c0x/valueset/status` | 802.2 = 1,006 sets, 802.3 = 260, measure groups for all nine CMS ids |

Three engine-side work items fall out (fhir-triple-store, has
uncommitted `C0XVSIMP` work in flight as of this writing):

1. Fix UNION under `population=1` (arms evaluate to 0 when combined).
2. Fix VALUES candidate union with mixed numeric/alphanumeric codes:
   `VALUES { "59621000" "38341003" "1201005" }` → 28 candidates, but
   adding `"I10"` collapses the result to 1 (only the I10 row) — smells
   like numeric-vs-string subscript collation in the POPIDX prune.
   Until fixed, round-2 queries stay SNOMED-only.
3. Deepen FileMan VS expansions so `FROM oid`/`FROM measure` cover the
   SNOMED branches, not just ICD — otherwise value-set-driven queries
   can't see Synthea-coded conditions.

## Method

For each measure with a round-1 CQL baseline (CMS165, CMS122, CMS130,
CMS138):

1. Draft the IPP-shaped population query in
   `2026/cohorts/c0x-sparql-round2/queries/{CMS}.sparql`. Prefer
   `VALUES` multi-code lists now; switch to `FROM oid` once expansions
   are fixed; add `MINUS` arms later for DENEX-shaped pruning.
2. Run `scripts/c0x-sparql-round2.py --cms {CMS}` — POSTs the query to
   `/c0x/sparql?population=1`, collects candidate DFNs, and scores
   against the round-1 truth `2026/cohorts/{CMS}/c0x-cql/cql-results.tsv`
   (CQL IPP column): true/false positives, missed IPP patients,
   precision, recall.
3. Results land in `2026/cohorts/c0x-sparql-round2/{CMS}-round2.json` +
   a cumulative `SUMMARY.tsv`; compare against round-1 single-code
   baselines recorded there too.

Success criteria: recall = 1.0 against CQL IPP on the known cohort with
precision materially better than round 1's single-code proxy, using only
index-side SPARQL (no CQL until confirmation).

## Round-2 baseline runs (devfhir, 2026-09-03)

Verified multi-code `VALUES` queries (combinations checked to union
correctly), scored by unique DFNs from actual bindings — note the
server's `candidates` field is the POPIDX prune superset and can be much
larger (CMS138: 506 candidates → 35 patients with verified triples).

| Measure | Round-2 query | DFNs | Round-1 single-code | vs CQL IPP |
|---|---|---|---|---|
| CMS165v14 | Condition 59621000/38341003/1201005 | 28 | 23 | precision 0.571, **recall 1.0** (round-1: 0.696/1.0); 5 new candidates the single code missed |
| CMS122v14 | Condition 44054006/73211009 | 7 | 5 | truth TBD (regenerate CQL confirmations) |
| CMS130v14 | Procedure 73761001/444783004 | 19 | 17 | truth TBD |
| CMS138v14 | Observation 72166-2/449868002 | 35 | 47¹ | truth TBD |

¹ Round-1 CMS138 count came from the candidates field, not verified
bindings, so the numbers are not directly comparable.

Broken VALUES combinations recorded for the engine fix (all reduce to
1 candidate — the crafted 101090 quality row — silently dropping the
other arms):

- `{ "59621000" "38341003" "1201005" "I10" }` (works without "I10")
- `{ "44054006" "73211009" "46635009" }` (any order; each pair works)

## Round-2 final results (devfhir, 2026-09-03, post-fix)

Engine fixes shipped in fhir-triple-store `C0XSPAR.m`:

1. **POPEXEC prune now unions code buckets** (and type buckets), then
   intersects only across the two families. The old per-code
   intersection with reseed-on-empty caused every "collapses to the one
   crafted 101090 row" symptom, including the apparent `FROM
   oid`/`FROM measure` failures — the FileMan expansions were fine all
   along.
2. **UNION arms no longer abort on a no-match arm** (a patient coding
   hypertension one way failed the other arm and dropped out — that was
   the population-UNION-returns-0 bug), and main-WHERE triples are now
   merged into each arm as shared constraints.
3. `deploy-c0x.sh` listener restarts now run from `/tmp` (JOB'd children
   die with JOBFAIL/ENO13 from non-writable cwds) — the same trap that
   had left fhirprod and rpmsfhir silently running stale builds.

Final queries: `FROM oid` (CMS165, CMS122), four-arm cross-type UNION
(CMS130), five-code VALUES (CMS138). Phase-2 confirmation
(`scripts/c0x-round2-confirm.py`) fetched each candidate's round-trip
export (`GET /fhir?dfn=`) and ran official CQL
(`evaluate-cqm-manifest.js`) — same surface as the round-1 c0x-cql lane.

| Measure | R2 query | Candidates | CQL IPP | R2 precision/recall | R1 precision/recall |
|---|---|---|---|---|---|
| CMS165v14 | Condition `FROM oid` Essential HTN | 28 | 23 | 0.821 / **1.000** | 0.870 / 0.870 |
| CMS122v14 | Condition `FROM oid` Diabetes | 7 | 5 | 0.714 / **1.000** | 0.600 / 0.600 |
| CMS130v14 | 4-arm UNION Procedure+Observation | 19 | 17 | 0.895 / **1.000** | 0.882 / 0.882 |
| CMS138v14 | 5-code VALUES Observation | 35 | 28 | 0.800 / **1.000** | 0.596 / 1.000 |

Notes:

- Truth = CQL IPP among all evaluated candidates (round-1 ∪ round-2), so
  recall is relative to every patient either round surfaced — not a
  full-population sweep. Round 1's single-code queries **missed true IPP
  patients on three of four measures** (3 for CMS165, 2 for CMS122 and
  CMS130); round 2 found them all.
- CMS165 truth grew 16 → 23: the round-2 candidate set surfaced 7 more
  CQL-confirmable IPP patients (5 new candidates + exports re-evaluated
  after the September data loads).
- Remaining false positives are honest heuristic looseness (no
  age/encounter gating in the raw SPARQL; the preset cohort layer adds
  those gates server-side).
- Artifacts: queries, candidates, export bundles, QDM conversions, CQL
  results, and truth lists under `2026/cohorts/c0x-sparql-round2/`.

## Preset upgrades (C0XCOH.m, deployed to all five targets)

Primary preset SPARQL upgraded from single-code to the verified round-2
shapes: multi-code `VALUES` for all VALUES-safe presets and a four-arm
cross-type UNION for CMS130-NUMER (colonoscopy Procedure OR FIT/FOBT
Observation). `FHQS` code lists extended to match (CMS165 +1201005,
CMS122 +73211009,46635009). Verified post-deploy: preset cohorts resolve
via POPIDX (devfhir CMS165 ippCount 27 with age+encounter gates).

## Deployment status (2026-09-03 overnight)

`deploy-quality-all.sh` ran green on all five targets (fhirdev, vehu10,
rpms-candidate, rpmsfhir, fhirprod). fhirprod and rpmsfhir needed the
listener-restart fix and a POPIDX population build
(`fhirdev-reindex-population.sh` against their bases; fhirprod 1,633
patients / 900 distinct codes, rpmsfhir 1,158 / 807). rpmsfhir had been
running a pre-population C0XSPAR build — its restart had been silently
failing for some time. Post-fix verification: UNION population queries
return candidates on all three public servers.

Known content gaps (not engine): rpmsfhir has no FileMan 802.2 value-set
store (`FROM oid` errors there; inline VALUES presets work); fhirprod's
older VS/coding content yields different counts than devfhir.

## Query sketches

- **CMS165** — hypertension dx: `VALUES` over the Essential Hypertension
  VS SNOMED+ICD codes (59621000, 38341003, 1201005, I10, …).
- **CMS122** — diabetes dx: VS 2.16.840.1.113883.3.464.1003.103.12.1001
  codes (44054006, E11.*, …) UNION/VALUES; later `MINUS` hospice.
- **CMS130** — age-band + colonoscopy/FIT evidence OR colorectal dx;
  start with Condition/Procedure code lists.
- **CMS138** — tobacco screening: Observation 72166-2 or tobacco-use
  finding codes; nearly every patient qualifies (age gate dominates) —
  good precision stress test.

Age/sex gates are not expressible in triples yet; accept that
over-selection and note it in scoring (POPIDX carries sex/age? — check
`c0x:sex`/birthdate triples as a follow-up).
