# CMS165 cqm-execution package

Needed for `node scripts/evaluate-cms165-qdm.js`:

- `measure.json` (tracked; assembled from eCQI ELM)
- `value_sets.json` (**local only** — gitignored; expand via VSAC)

## Preferred

Bonnie / MADiE / Project Tacoma export of CMS165v14 (QDM).

## Local builder (VSAC)

```bash
eval "$(~/ops/scripts/load-vsac-api-key.sh)"
# Assembles measure.json from eCQI ELM under 2026/artifacts/.../CMS165-v14.0.000-QDM/
# Expands every ELM value-set OID via VSAC SVS into value_sets.json
node scripts/build-cms165-cqm-package.js
```

Expected when the key works: `Value sets: 37/37 expanded from VSAC` with non-zero concept counts.

Then:

```bash
node scripts/evaluate-cms165-qdm.js
```

See `docs/VSAC_CMS165_RUN_2026-07-23.md` for the first successful expand + execute run, engine fixes, and why `selected-18` still scores IPP=0.

## Notes

- The official eCQI 2026 QDM ZIP contains CQL/ELM libraries only, not expanded value sets.
- Builder emits value-set `oid` as `urn:oid:…` (required by `cql-execution` lookup against ELM).
- Do not commit expanded `value_sets.json` to a public remote (UMLS/VSAC terms).
