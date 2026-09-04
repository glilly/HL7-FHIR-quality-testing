# January 2027 Connectathon — linked-data demo script

Date: 2026-09-04 · Phase-4 prep for
`Vista-on-FHIR/docs/LINKED_DATA_STRATEGY.md` · Companion to
`Vista-on-FHIR/docs/CONNECTATHON_43_SHADOW_AND_JANUARY_PLAN.md` and the
ITS feedback draft `Vista-on-FHIR/docs/FHIR_RDF_IMPLEMENTATION_FINDINGS.md`

Target tracks: **FHIR-RDF / ITS** (host + findings), **Vulcan / research
matching** (trial finder), plus the existing quality lane.

## 15-minute demo (all live, all synthetic data)

**1. The node is a linked-data host (2 min).**
Open `https://devfhir.vistaplex.org/c0x/linkeddata` — machine-readable
service description. Show `/c0x/context.jsonld`, then a patient graph as
JSON-LD and as Turtle (`/c0x/jsonld?dfn=…`, `/c0x/turtle?dfn=…`), and a
population-level export. Point out: dereferenceable context, true
`@graph` array, five deployed nodes.

**2. SPARQL with terminology built in (2 min).**
In the C0X UI SPARQL panel, run a population query using
`VALUES ?code FROM oid "2.16.840.1.113883.3.464.1003.103.12.1001"` —
value-set expansion inside the query. Note candidates vs official CQL
IPP (round-2 results: within 0–2 patients on 6 of 7 CMS measures).

**3. Federation walk — local graph to the open knowledge web (3 min).**
UI Research panel → pick lisinopril from the medication dropdown → Run
walk: local orders/patients → RxNav ATC class → Wikidata entity +
indication → recruiting trials. Then the same thing as one gateway call:
`POST https://cds1.vistaplex.org/linked/enrich {"code":"314076"}`.

**4. Federated cohort counts, aggregate-only (2 min).**
`POST /linked/cohort-count {"code":"860975"}` — one query, three
sites (WorldVistA dev, WorldVistA prod-reference, RPMS), per-site counts
and timings, no patient identifiers. This is the privacy posture story.

**5. Trial matching (5 min).**
UI trial finder → search "type 2 diabetes" / "metformin" → hits annotate
with the published match run: NCT06862739 shows 3 eligible candidates
with DFNs; NCT06932874 shows the honest zero (no CHD in cohort) with
near-miss reasons. Open
`/filesystem/research/report.md` for the per-criterion met/missed table,
and a `ResearchStudy` / `ResearchSubject` pair as the FHIR artifacts a
sponsor system would consume. Close the loop: care-gap → order entered →
re-run → counts move (existing closed-loop demo).

**6. Findings for the ITS RDF subgroup (1 min).**
Six implementation findings from doing this on MUMPS/GT.M — the
`@graph` array trap, dereferenceable contexts, newline-sensitive Turtle,
"small SPARQL + terminology beats big SPARQL", vocabulary mapping to
`fhir.ttl` as the open ask, aggregate-only profiles.

## Prep checklist (day before)

- [ ] `linkeddata-host-smoke.sh` green on all five nodes
- [ ] `smoke-quality-host.sh` green on the three public nodes
- [ ] `POST /linked/enrich` + `/linked/cohort-count` warm (cache primed)
- [ ] Re-run `scripts/trial-matching.py` + `scripts/publish-research.sh`
      (registry statuses drift; trials may close)
- [ ] Verify the four NCT ids are still listed; swap criteria file if not
- [ ] PDF one-pagers current (strategy + findings)
