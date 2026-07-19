# CMS165 cqm-execution package

Needed for `node scripts/evaluate-cms165-qdm.js`:

- `measure.json`
- `value_sets.json`

## Preferred

Bonnie / MADiE / Project Tacoma export of CMS165v14 (QDM).

## Local builder (best-effort)

```bash
# Assembles measure.json from eCQI ELM under 2026/artifacts/.../CMS165-v14.0.000-QDM/
node scripts/build-cms165-cqm-package.js

# Optional: expand value sets via UMLS/VSAC API key
VSAC_API_KEY=... node scripts/build-cms165-cqm-package.js
```

Without VSAC expansions (or a Bonnie `value_sets.json`), `cqm-execution` is not meaningful — codes never match.

The official eCQI 2026 QDM ZIP contains CQL/ELM libraries only, not expanded value sets.
