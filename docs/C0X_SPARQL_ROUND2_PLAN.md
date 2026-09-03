# C0X SPARQL Round 2 — UNION/VALUES IPP approximation

Date: 2026-09-03. Baseline: round-1 experiment imported at
`2026/cohorts/c0x-heuristic/` + `2026/cohorts/{CMS}/c0x-cql/` (commit
`c8aac09`).

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
