# September Connectathon Recommendations

Status: working document, updated as cohorts and scorecards are produced.

## Selection Rule

A measure/patient cohort becomes a September candidate when it has evidence in all three layers:

1. CQL/DEQM MeasureReport confirms denominator and numerator membership.
2. Hosted Inferno validates the source bundle through `http://devfhir.vistaplex.org:9080/altfhir`.
3. After `load=1`, hosted Inferno validates the VistA-generated bundle through `https://devfhir.vistaplex.org/fhir` or the direct devfhir listener if needed.

## Current Runtime Finding

`/altfhir` is publicly reachable through the HTTPS devfhir front door at `https://devfhir.vistaplex.org/altfhir`. Caddy now proxies `/altfhir*` to the M listener on `fhirdev22`, matching the planned hosted-Inferno base URL.

## Initial Round-Trip Evidence

| Endpoint | Patient | Hosted Inferno session | Pass | Fail | Skip | Notes |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `/altfhir` | graph IEN 10 | https://inferno.healthit.gov/suites/us_quality_core_v050/jTPqGQ5WrGz | 25 | 175 | 298 | Source-bundle smoke against direct devfhir listener. |
| `/fhir` | DFN 101091 | https://inferno.healthit.gov/suites/us_quality_core_v050/fi9VnEq3MQX | 30 | 126 | 342 | VistA round-trip smoke after `addpatient?load=1`; generated bundle is smaller than source bundle. |
| `/fhir` | DFN 101091 + generated Provenance | https://inferno.healthit.gov/suites/us_quality_core_v050/iPLS5HMzUnE | 45 | 128 | 325 | Prototype generated one US Core Provenance resource per VistA bundle and enabled `_revinclude=Provenance:target`; 13 Provenance revinclude tests passed after warming the cached Patient search. |
| `/altfhir` | CMS165 selected 18 graph IENs | https://inferno.healthit.gov/suites/us_quality_core_v050/2AG6LOnFf4B | 32 | 194 | 272 | Source-bundle run for the first CMS165 numerator cohort. |
| `/fhir` | CMS165 selected 18 DFNs | https://inferno.healthit.gov/suites/us_quality_core_v050/4OuMYu6AMCF | 31 | 129 | 338 | Round-trip run after loading all 18 CMS165 patients into VistA. |

Loaded smoke patients:

- IEN 1352 / DFN 101091
- IEN 1353 / DFN 101092
- IEN 1354 / DFN 101093

CMS165 selected cohort:

- Source graph IENs: `492,505,524,529,530,558,567,566,574,576,577,582,607,608,624,644,680,686`
- Loaded DFNs: `101094,101095,101096,101097,101098,101099,101100,101101,101102,101103,101104,101105,101106,101107,101108,101109,101110,101111`
- Preclassifier result: 193 denominator candidates and 76 numerator candidates among the first 1000 generated Synthea bundles; first 18 numerator candidates selected for hosted Inferno and round-trip load.

Provenance prototype result:

- Direct smokes confirm `Patient?_id=101091&_revinclude=Provenance:target` returns Patient plus Provenance, and `Observation?patient=101091&_count=5&_revinclude=Provenance:target` returns 5 Observations plus Provenance.
- Hosted Inferno improved from 30 pass / 126 fail / 342 skip to 45 pass / 128 fail / 325 skip after cache warming.
- Provenance-specific tests improved from 0 pass / 17 fail / 34 skip to 13 pass / 17 fail / 21 skip. The remaining Provenance failures are for resource types whose searches still return `OperationOutcome` or whose resources are absent from this patient.
- Next fix: make newly deployed Provenance generation invalidate or refresh stale cached search bundles automatically so hosted Inferno does not depend on a manual warm-up request.

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
