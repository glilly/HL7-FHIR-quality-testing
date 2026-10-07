# Agent working agreement — HL7-FHIR-quality-testing

1. Don't assume. Don't hide confusion. Surface tradeoffs.
2. Minimum code that solves the problem. Nothing speculative.
3. Touch only what you must. Clean up only your own mess.
4. Define success criteria. Loop until verified.

This repo holds **quality-measure evidence**: CMS eCQM cohorts and value
sets under `2026/measures/`, DEQM builders/validators, Inferno scorecards,
the daily quality rotation, and the trial-matching research lane. Server
code is in `VistA-FHIR-Server-Codex` (`C0FQUAL`, `C0FHIR*`); population
queries are in `fhir-triple-store` (C0X). Read those repos' `AGENTS.md`
before changing anything they own.

## Rules that have bitten us

- **Scorecards come from hosted Inferno against `https://devfhir.vistaplex.org`**,
  never from a local container. Inferno cannot reach localhost.
- **Value sets are vendored artifacts.** Never hand-edit
  `2026/measures/*/cqm/value_sets.json`; `VistA-FHIR-Server-Codex/scripts/check-artifacts.sh`
  must stay green and is run every night. Refresh only with the documented
  fetch script and a daytime `--update`.
- **IPP vs NUMER labels are a contract.** When a dashboard or preset label
  is wrong, add a machine check to Codex `scripts/smoke-quality-host.sh`
  alongside the fix (the "deploy-quality-all" phrase in Codex `AGENTS.md`).
- **Evidence is committed whether green or red.** Daily quality rotation
  writes `2026/scorecards/daily-quality/YYYY-MM-DD-<host>.md`; the nightly
  lane commits it from a detached worktree, so `git pull --ff-only` before
  committing here.
- All patients are synthetic (Synthea). No PHI, ever, including in
  scorecards and research outputs.

## Standing verification commands

| Claim | Command |
|---|---|
| DEQM subject-list rebuildable | `scripts/build-deqm-subject-list.py` then `scripts/check-deqm-summary.py <prototype>` |
| Trial confirmation reproducible | `scripts/trial-confirmation.py --scan-pool` |
| One host's quality stack healthy | `scripts/daily-quality-rotate.sh` (host rotates daily; `QUALITY_REEVAL=0` at night) |
| Curated SETPOP on fhirdev | `scripts/fhirdev-apply-setpop.sh` |
| Inferno run | `scripts/inferno-run.py` (hosted Inferno, devfhir base) |

cds1 (`cds-hooks-on-fhir`, CQL/quality-eval sidecar) may be called at any
time, including unattended. Shared fleet servers may not be redeployed or
restarted at night — a failure gets a dated report.
