# CMS165 HTN / R69 Condition coding plan — pointer

Canonical plan (root cause, Lexicon vs SYN invent vs C0FW, repair steps):

**[WVEHR-on-FHIR/docs/CMS165_HTN_CONDITION_R69_PLAN_2026-09-24.md](../../WVEHR-on-FHIR/docs/CMS165_HTN_CONDITION_R69_PLAN_2026-09-24.md)**

Short version: cohort HTN Conditions show text “Essential hypertension” with ICD
**R69** because stale Lexicon associations and/or `SYNDHP61`’s empty-map
fallback filed *Illness, unspecified*. Do not loosen C0X presets. Fix mapping
(reject R69 catch-all; prefer I10 / Bundle ICD) and repair stored problem-list
rows. JOHN-SALT dual I10+59621000 active is the reference shape.

**Status 2026-09-24:** after repair + H1 onset backdate + official reeval on
`fhir.vistaplex.org`, CMS165v14 CQL is **IPP/DENOM/NUMER = 5/5/5**. Broader
coding gaps: [WVEHR_CODING_GAP_PLAN_POINTER.md](./WVEHR_CODING_GAP_PLAN_POINTER.md).
