# Phase-1 host readiness — every node ready for external searchers

Date: 2026-09-04 (overnight) · Strategy:
`Vista-on-FHIR/docs/LINKED_DATA_STRATEGY.md` Phase 1 (target-role
hardening) · Code: `fhir-triple-store` commit `60ac330`

## What a visiting searcher now gets

1. **`GET /c0x/linkeddata`** — machine-readable service description:
   endpoints, SPARQL dialect and its limits (no `SERVICE` federation),
   vocabulary, privacy tier (`synthetic-full`), worked examples. This is
   the door sign; hand this URL to a Connectathon partner.
2. **`GET /c0x/context.jsonld`** — dereferenceable JSON-LD 1.1 context for
   the `c0x:` vocabulary; any jsonld export can reference it by URL with
   `&ctx=url`.
3. **Population-level graph exports** — `GET /c0x/jsonld?population=1&
   measure=CMS165v14&max=25` (and the Turtle twin) return the measure
   cohort as `Patient/<dfn>` nodes with heuristic match metadata.
4. **Standards-compliant JSON-LD** — `@graph` is now a true JSON array
   (the old `"0": count` node forced object mode and broke JSON-LD
   processors; count moved to a `nodes` field). Exports expand cleanly
   under pyld (JSON-LD 1.1) and Turtle parses under rdflib.
5. **CORS** was already open (`Access-Control-Allow-Origin: *` on GET)
   via Caddy on all public hosts — verified rather than built.

## Verification — linkeddata-host-smoke.sh, all five nodes

The new `fhir-triple-store/scripts/linkeddata-host-smoke.sh` asserts the
whole contract: description JSON, context, JSON-LD 1.1 expansion (pyld),
Turtle parse (rdflib), population exports, CORS header.

| Node | DFN probed | Result |
|---|---|---|
| devfhir.vistaplex.org | 101076 | HOST SMOKE OK |
| fhir.vistaplex.org | 1643 | HOST SMOKE OK |
| rpmsfhir.vistaplex.org | 8 | HOST SMOKE OK |
| vehu10 (local :9085) | 101076 | HOST SMOKE OK |
| rpms-candidate (local :9088) | 4 | HOST SMOKE OK |

## Honest limits carried into Phase 2+

- Graphs speak the `urn:c0x:` index vocabulary, not FHIR-RDF `fhir:`
  ontology terms; FHIR-RDF alignment (and ShEx validation against the
  R6-ballot schemas) is the natural next standards step.
- References export as string literals, not IRIs.
- Population exports are heuristic cohort surfaces; official CQL counts
  remain on the quality dashboards.
- The searcher-facing guide lives at
  `fhir-triple-store/docs/LINKED_DATA_HOST.md`.
