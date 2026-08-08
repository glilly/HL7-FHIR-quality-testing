#!/usr/bin/env python3
"""Build one DEQM Individual MeasureReport (QRDA-I analogue) from SETPOP flags."""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEQM_INDV_PROFILE = (
    "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/indv-measurereport-deqm"
)
MEASURE_SCORING_EXT = (
    "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/extension-measureScoring"
)
POP_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-population"
SCORING_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-scoring"
IMPROVE_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-improvement-notation"
ORG_REF = "Organization/vistaplex-demo"


def measure_canonical(cms: str) -> str:
    version = "0.0.1"
    if "v" in cms:
        tail = cms.rsplit("v", 1)[-1]
        if tail.isdigit():
            version = f"{int(tail)}.0.000"
    return f"https://ecqi.healthit.gov/ecqm/ec/{cms}|{version}"


def pop(code: str, display: str, count: int) -> dict[str, Any]:
    return {
        "code": {
            "coding": [{"system": POP_SYSTEM, "code": code, "display": display}],
            "text": display,
        },
        "count": int(count),
    }


def find_row(manifest: pathlib.Path, cms: str, dfn: str) -> dict[str, Any]:
    for line in manifest.read_text().splitlines()[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 8:
            continue
        if parts[0] == cms and parts[1] == str(dfn):
            return {
                "ipp": int(parts[2]),
                "denom": int(parts[3]),
                "numer": int(parts[4]),
                "denex": int(parts[5]),
                "evidence": parts[6],
                "mode": parts[7],
            }
    raise SystemExit(f"No SETPOP row for {cms} DFN {dfn} in {manifest}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cms", default="CMS165v14")
    ap.add_argument("--dfn", default="101115")
    ap.add_argument(
        "--manifest",
        default=str(ROOT / "2026/cohorts/SETPOP_MANIFEST.tsv"),
    )
    ap.add_argument("--period-start", default="2026-01-01")
    ap.add_argument("--period-end", default="2026-12-31")
    args = ap.parse_args()

    row = find_row(pathlib.Path(args.manifest), args.cms, args.dfn)
    as_of = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rid = f"{args.cms}-Patient-{args.dfn}-deqm"
    rep: dict[str, Any] = {
        "resourceType": "MeasureReport",
        "id": rid,
        "meta": {
            "profile": [DEQM_INDV_PROFILE],
            "source": "urn:vista:deqm-individual-builder",
            "tag": [
                {
                    "system": "https://vistaplex.org/fhir/CodeSystem/quality-calc-mode",
                    "code": row["mode"] or "official-cql",
                }
            ],
        },
        "extension": [
            {
                "url": MEASURE_SCORING_EXT,
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": SCORING_SYSTEM,
                            "code": "proportion",
                            "display": "Proportion",
                        }
                    ]
                },
            }
        ],
        "status": "complete",
        "type": "individual",
        "measure": measure_canonical(args.cms),
        "subject": {"reference": f"Patient/{args.dfn}"},
        "date": as_of,
        "reporter": {
            "reference": ORG_REF,
            "display": "VistaPlex FHIR Quality Demo",
        },
        "period": {"start": args.period_start, "end": args.period_end},
        "improvementNotation": {
            "coding": [
                {
                    "system": IMPROVE_SYSTEM,
                    "code": "increase",
                    "display": "Increased score indicates improvement",
                }
            ]
        },
        "group": [
            {
                "population": [
                    pop("initial-population", "Initial Population", row["ipp"]),
                    pop("denominator", "Denominator", row["denom"]),
                    pop("numerator", "Numerator", row["numer"]),
                    pop("denominator-exclusion", "Denominator Exclusion", row["denex"]),
                ]
            }
        ],
    }
    if row["evidence"]:
        # Keep evidence off .extension to avoid DEQM supplementalData slice noise.
        rep["meta"]["tag"].append(
            {
                "system": "https://vistaplex.org/fhir/CodeSystem/quality-evidence",
                "code": "evidence",
                "display": row["evidence"][:200],
            }
        )

    out = (
        ROOT
        / "docs/deqm-summary/prototypes"
        / f"{args.cms}-Patient-{args.dfn}-individual-deqm.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=2) + "\n")
    cohort = ROOT / "2026/cohorts/deqm-summary" / args.cms
    cohort.mkdir(parents=True, exist_ok=True)
    (cohort / f"Patient-{args.dfn}-individual-deqm.json").write_text(
        json.dumps(rep, indent=2) + "\n"
    )
    print(
        f"{args.cms} DFN {args.dfn}: IPP={row['ipp']} DENOM={row['denom']} "
        f"NUMER={row['numer']} DENEX={row['denex']} OUT={out}",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
