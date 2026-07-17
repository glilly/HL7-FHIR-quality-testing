# September Connectathon Recommendations

Status: working document, updated as cohorts and scorecards are produced.

## Selection Rule

A measure/patient cohort becomes a September candidate when it has evidence in all three layers:

1. CQL/DEQM MeasureReport confirms denominator and numerator membership.
2. Hosted Inferno validates the source bundle through `http://devfhir.vistaplex.org:9080/altfhir`.
3. After `load=1`, hosted Inferno validates the VistA-generated bundle through `https://devfhir.vistaplex.org/fhir` or the direct devfhir listener if needed.

## Current Runtime Finding

`/altfhir` is publicly reachable on the direct devfhir listener at `http://devfhir.vistaplex.org:9080/altfhir`. The HTTPS front door currently falls through to the CPRS demo for `/altfhir/*`, so hosted Inferno scorecards should use the direct listener until the HTTPS proxy is expanded.

## Initial Round-Trip Evidence

| Endpoint | Patient | Hosted Inferno session | Pass | Fail | Skip | Notes |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `/altfhir` | graph IEN 10 | https://inferno.healthit.gov/suites/us_quality_core_v050/jTPqGQ5WrGz | 25 | 175 | 298 | Source-bundle smoke against direct devfhir listener. |
| `/fhir` | DFN 101091 | https://inferno.healthit.gov/suites/us_quality_core_v050/fi9VnEq3MQX | 30 | 126 | 342 | VistA round-trip smoke after `addpatient?load=1`; generated bundle is smaller than source bundle. |

Loaded smoke patients:

- IEN 1352 / DFN 101091
- IEN 1353 / DFN 101092
- IEN 1354 / DFN 101093

## Candidate Measures

| CMS ID | Candidate Status | Notes |
| --- | --- | --- |
| CMS122v14 | pending cohort classification | Diabetes/HbA1c should be high yield. |
| CMS165v14 | pending cohort classification | Blood pressure overlaps strong USQC vital-sign groups. |
| CMS130v14 | pending cohort classification | Screening numerator support may expose Procedure/DiagnosticReport gaps. |
| CMS125v14 | pending cohort classification | Mammography evidence likely needs source enrichment. |
| CMS147v14 | verify against 2026 ZIP | Strong Immunization validation overlap if still present. |
| CMS2v15 | pending cohort classification | May expose screening/follow-up domains not fully loaded into VistA. |
| CMS68v15 | pending cohort classification | Medication documentation evidence needs exact mapping. |
| CMS138v14 | pending cohort classification | Social-history tobacco data may be thin in current server. |
| CMS134v14 | verify exact 2026 title/logical successor | Needs ZIP extraction before enrichment. |
| CMS131v14 | pending cohort classification | Eye exam evidence likely source-enrichment first. |

## Gap Log Template

For each candidate cohort, record:

- MeasureReport result: denominator, numerator, exclusions.
- `/altfhir` Inferno summary: pass/fail/error/skip and failure buckets.
- VistA load status: graph IEN, DFN, domains loaded, loader errors.
- `/fhir` Inferno summary: pass/fail/error/skip and delta from `/altfhir`.
- Recommendation: demo, backup, or backlog.
