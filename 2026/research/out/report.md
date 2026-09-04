# Trial-matching MVP run — heuristic stage

Date: 2026-09-04T05:17:09Z · node: https://devfhir.vistaplex.org · criteria: `2026/research/trial-criteria.json`

Heuristic evidence checks via C0X population SPARQL + Patient demographics.
Value-threshold criteria (marked *CQL*) are presence-only here; the
confirmation stage owns thresholds — same two-stage pattern as the
quality measures. All patients are synthetic.

## NCT06862739 — Glycemic Control With Triple Pathway Approach Through Empagliflozin, Linagliptin and Metformin Combination

Registry status: RECRUITING · candidate pool 25 patients

- `t2d` Diagnosed with type II diabetes (SNOMED 44054006): **6** patients
- `metformin` Already on anti-diabetic agent incl. metformin (RxNorm 860975/106892): **8** patients
- `a1c` Has HbA1c result on record (LOINC 4548-4; >=8% threshold left to CQL stage): **24** patients
- `age` Aged 18-80 years: demographic check

**Eligible (all criteria): 3** — DFNs 101109, 101119, 101124
Near-miss (one criterion short): 101084 (missing t2d); 101095 (missing t2d); 101096 (missing metformin); 101098 (missing t2d); 101102 (missing metformin); 101122 (missing t2d)

## NCT06932874 — Metformin Hydrochloride Sustained-release Tablets (Ⅲ) in Patients With Type 2 Diabetes Mellitus Complicated With Coronary Heart Disease

Registry status: RECRUITING · candidate pool 8 patients

- `t2d` Type 2 diabetes (SNOMED 44054006): **6** patients
- `chd` Coronary heart disease (SNOMED 53741008): **3** patients
- `metformin` On metformin (RxNorm 860975): **3** patients
- `age` Aged 18-80 years: demographic check

**Eligible (all criteria): 0** — DFNs —
Near-miss (one criterion short): 101109 (missing chd); 101119 (missing chd); 101124 (missing chd)

## NCT06826872 — Efficacy and Safety of SPC1001 in Patients With Essential Hypertension

Registry status: RECRUITING · candidate pool 27 patients

- `htn` Essential hypertension (SNOMED 59621000): **27** patients
- `antihtn` On antihypertensive (lisinopril/amlodipine/HCTZ RxNorm 314076/308136/310798): **10** patients
- `age` Aged 18-75 years: demographic check

**Eligible (all criteria): 10** — DFNs 101077, 101084, 101088, 101094, 101095, 101096, 101097, 101098, 101099, 101100
Near-miss (one criterion short): 101101 (missing antihtn); 101102 (missing antihtn); 101103 (missing antihtn); 101104 (missing antihtn); 101105 (missing antihtn); 101106 (missing antihtn); 101107 (missing antihtn); 101108 (missing antihtn); 101109 (missing antihtn); 101111 (missing antihtn); 101115 (missing antihtn); 101122 (missing antihtn); 101123 (missing antihtn); 101126 (missing antihtn); 101127 (missing antihtn)

## NCT05413057 — An OS to Evaluate Effectiveness and Safety of Fixed-dose Combinations of FMS/AML or FMS/AML/HCTZ

Registry status: RECRUITING · candidate pool 27 patients

- `htn` Essential hypertension (SNOMED 59621000): **27** patients
- `amlodipine` On amlodipine (RxNorm 308136): **14** patients
- `age` Adult (18+): demographic check

**Eligible (all criteria): 14** — DFNs 101088, 101094, 101095, 101097, 101098, 101099, 101100, 101101, 101104, 101105, 101107, 101108, 101111, 101115
Near-miss (one criterion short): 101077 (missing amlodipine); 101084 (missing amlodipine); 101096 (missing amlodipine); 101102 (missing amlodipine); 101103 (missing amlodipine); 101106 (missing amlodipine); 101109 (missing amlodipine); 101110 (missing amlodipine); 101122 (missing amlodipine); 101123 (missing amlodipine); 101125 (missing amlodipine); 101126 (missing amlodipine); 101127 (missing amlodipine)

