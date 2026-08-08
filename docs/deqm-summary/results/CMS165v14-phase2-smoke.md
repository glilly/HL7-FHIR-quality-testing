# Phase 2 smoke results — CMS165v14 DEQM Summary

- Date (UTC): 2026-08-08T01:39:31Z
- Validator: infernocommunity/fhir-validator-service (DISABLE_TX=true) + hl7.fhir.us.davinci-deqm#5.0.0
- Receiver: projecttacoma/deqm-test-server @ localhost:3000

## Receiver
- Transaction response: `transaction-response` with entries: 200 OK → 4_0_1/Organization/vistaplex-demo, 200 OK → 4_0_1/MeasureReport/CMS165v14-summary-deqm

## Validator OperationOutcome
- Severity counts: `{'error': 1, 'information': 4, 'warning': 3}`
- Actionable errors after known IG noise filter: **0**
- Known noise (also on IG golden `summ-measurereport02`): unable to resolve R5 `extension-MeasureReport.supplementalData` when evaluating extension slices on `extension-measureScoring`.

## Prototype fixes applied this pass
- `measure` now versioned (`…|14.0.000`) for DEQM invariant `deqm-0`
- Custom cohort provenance moved from `.extension` to `meta.tag`
- Group code system uses vistaplex CodeSystem (not example.org)
