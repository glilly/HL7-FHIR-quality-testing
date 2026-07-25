# Overnight Marathon Report (20260723-220217) — failed run

Generated: 2026-07-23T22:05:09 (broken report body; heredoc bug)

## Status

**Failed / incomplete.** Preclassifier wrote cohorts, but VSAC expansions were empty, CQL and Inferno did not complete, and this report was corrupted by an unquoted bash heredoc.

**Authoritative recovery report:** [`RECOVER_CMS165_122_REPORT_LATEST.md`](./RECOVER_CMS165_122_REPORT_LATEST.md) (2026-07-25).

## What still useful from this night

- Multi-measure preclassifier outputs under `2026/cohorts/`
- `2026/cohorts/OVERNIGHT_PRECLASSIFIER_SUMMARY.json`
- Log: `logs/overnight-marathon-20260723-220217.log`

## Morning checklist (carried forward)

1. Review preclassifier numer counts — pick final showcase DFN/IEN per measure.
2. Inspect CQL batch JSON for measures with expanded value sets. *(done in recovery)*
3. Compare Inferno multi-showcase skip families vs CMS165-only baseline.
4. Activate winning measures in C0FQUAL / Quality AI Consult. *(CMS165/122 aggregates published)*
5. Commit scorecards + reports (`value_sets.json` stays gitignored).
