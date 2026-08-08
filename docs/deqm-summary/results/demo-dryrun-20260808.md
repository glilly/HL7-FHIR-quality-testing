# Live demo dry-run — timings and findings

Date: 2026-08-08 (checklist item 8)

Full loop per `CONNECTATHON_PACKET.md` demo script, both lanes, from
clean `/tmp` outputs, public endpoints, local validator + receiver.

## Timings

| Step | VistA (devfhir, 20 DFNs) | RPMS (rpmsfhir, 19 DFNs) |
|---|---:|---:|
| 1. Fetch collection Bundles | 23.7 s | 39.7 s |
| 2. CQL evaluation (CMS165v14) | 5.0 s | 5.1 s |
| 3. Build Summary MeasureReport | < 0.1 s | < 0.1 s |
| 4. Validate + POST receiver | 0.4 s | 0.4 s |
| **Loop total** | **~30 s** | **~45 s** |

Both loops complete in under a minute each — comfortable inside a
10-minute live slot with narration. Validator: 0 actionable errors both
lanes; receiver: 200/201 both lanes.

## Findings

1. **Counting bug found and fixed.** The evaluator's cohort counting
   used raw CQL statement results, so patients outside the denominator
   (or excluded) could still count in NUMER. `evaluate-cqm-manifest.js`
   now enforces population hierarchy (DENOM ⊆ IPP, DENEX ⊆ DENOM,
   NUMER ⊆ DENOM−DENEX). Published RPMS counts corrected:
   CMS165 19/19/**13**/1 (was 14), CMS122 10/10/**4**/0 (was 9);
   CMS130/CMS2/CMS22 unchanged. devfhir raw selected-18 (14/14/14/0)
   re-verified unchanged under gating.
2. **Live RPMS re-fetch reproduces the packet counts exactly**
   (19/19/13/1) — the demo is reproducible from the network, not only
   from cached bundles.
3. **Demo caveat for the VistA lane:** the frozen packet counts
   (14/14/14/0) come from evaluating the raw Synthea bundles; the
   *live* devfhir round-trip surface yields **8/8/8/0** on 20 DFNs —
   the devfhir collection-Bundle export round-trips less data than
   rpmsfhir's. State this up front in the demo: frozen counts = raw
   evaluation; live loop = round-trip evaluation. (It is also the
   round-trip-fidelity finding of the dual-lane comparison.)

## Fallbacks rehearsed

- Local `deqm-test-server` (`:3000`) accepts both lanes' transaction
  Bundles; use when no peer/track receiver is available.
- Pre-built reports under `prototypes/` and `prototypes/rpms/` if live
  evaluation is not possible (network loss): validate + POST directly.
