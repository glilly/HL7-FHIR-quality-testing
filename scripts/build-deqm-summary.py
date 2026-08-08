#!/usr/bin/env python3
"""Build a DEQM STU5 Summary MeasureReport (QRDA-III FHIR replacement).

Emits:
  docs/deqm-summary/prototypes/{CMS}-summary-deqm.json
  docs/deqm-summary/prototypes/Organization-vistaplex-demo.json
  docs/deqm-summary/prototypes/Bundle-{CMS}-summary-transaction.json

Counts may be passed explicitly (preferred for official-cql freeze) or
aggregated from SETPOP_MANIFEST.tsv.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs/deqm-summary/prototypes"

DEQM_SUMMARY_PROFILE = (
    "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/summary-measurereport-deqm"
)
MEASURE_SCORING_EXT = (
    "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/extension-measureScoring"
)
POP_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-population"
SCORING_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-scoring"
IMPROVE_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-improvement-notation"
ORG_ID = "vistaplex-demo"
ORG_REF = f"Organization/{ORG_ID}"


def measure_canonical(cms: str) -> str:
    # Placeholder until CMS FHIR dQM Measure packages are pinned for EC.
    return f"https://ecqi.healthit.gov/ecqm/ec/{cms}"


def pop(code: str, display: str, count: int) -> dict[str, Any]:
    return {
        "code": {
            "coding": [{"system": POP_SYSTEM, "code": code, "display": display}],
            "text": display,
        },
        "count": int(count),
    }


def organization() -> dict[str, Any]:
    return {
        "resourceType": "Organization",
        "id": ORG_ID,
        "meta": {
            "profile": [
                "http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-organization"
            ]
        },
        "identifier": [
            {
                "system": "https://vistaplex.org/fhir/sid/organization",
                "value": "vistaplex-demo",
            }
        ],
        "active": True,
        "name": "VistaPlex FHIR Quality Demo (fhirdev)",
        "telecom": [
            {"system": "url", "value": "https://devfhir.vistaplex.org/fhir-quality-dashboards"}
        ],
    }


def summary_report(
    *,
    cms: str,
    ipp: int,
    denom: int,
    numer: int,
    denex: int,
    cohort_size: int,
    mode: str,
    source: str,
    period_start: str,
    period_end: str,
    as_of: str,
) -> dict[str, Any]:
    score = (float(numer) / float(denom)) if denom else 0.0
    rid = f"{cms}-summary-deqm"
    return {
        "resourceType": "MeasureReport",
        "id": rid,
        "meta": {
            "profile": [DEQM_SUMMARY_PROFILE],
            "source": "urn:vista:deqm-summary-builder",
            "tag": [
                {
                    "system": "https://vistaplex.org/fhir/CodeSystem/quality-calc-mode",
                    "code": mode,
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
            },
            {
                "url": "https://vistaplex.org/fhir/StructureDefinition/vista-quality-cohort-size",
                "valueInteger": int(cohort_size),
            },
            {
                "url": "https://vistaplex.org/fhir/StructureDefinition/vista-quality-source",
                "valueString": source,
            },
        ],
        "status": "complete",
        "type": "summary",
        "measure": measure_canonical(cms),
        "date": as_of,
        "reporter": {"reference": ORG_REF, "display": "VistaPlex FHIR Quality Demo"},
        "period": {"start": period_start, "end": period_end},
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
                "code": {
                    "coding": [
                        {
                            "system": "https://vistaplex.org/fhir/CodeSystem/measure-group",
                            "code": "group-1",
                            "display": "group-1",
                        }
                    ],
                    "text": "group-1",
                },
                "population": [
                    pop("initial-population", "Initial Population", ipp),
                    pop("denominator", "Denominator", denom),
                    pop("numerator", "Numerator", numer),
                    pop("denominator-exclusion", "Denominator Exclusion", denex),
                ],
                "measureScore": {"value": round(score, 6)},
            }
        ],
    }


def transaction_bundle(report: dict[str, Any], org: dict[str, Any], ts: str) -> dict[str, Any]:
    return {
        "resourceType": "Bundle",
        "id": f"{report['id']}-transaction",
        "type": "transaction",
        "timestamp": ts,
        "entry": [
            {
                "fullUrl": f"urn:uuid:{ORG_ID}",
                "resource": org,
                "request": {"method": "PUT", "url": ORG_REF},
            },
            {
                "fullUrl": f"urn:uuid:{report['id']}",
                "resource": report,
                "request": {
                    "method": "PUT",
                    "url": f"MeasureReport/{report['id']}",
                },
            },
        ],
    }


def write_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def counts_from_manifest(manifest: pathlib.Path, cms: str) -> tuple[int, int, int, int, int]:
    ipp = denom = numer = denex = n = 0
    for line in manifest.read_text().splitlines()[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 6 or parts[0] != cms:
            continue
        n += 1
        ipp += int(parts[2])
        denom += int(parts[3])
        numer += int(parts[4])
        denex += int(parts[5])
    if n == 0:
        raise SystemExit(f"No SETPOP rows for {cms} in {manifest}")
    return ipp, denom, numer, denex, n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cms", default="CMS165v14")
    ap.add_argument("--ipp", type=int)
    ap.add_argument("--denom", type=int)
    ap.add_argument("--numer", type=int)
    ap.add_argument("--denex", type=int, default=0)
    ap.add_argument("--cohort-size", type=int)
    ap.add_argument("--mode", default="official-cql")
    ap.add_argument(
        "--source",
        default="manual counts (see docs/deqm-summary/README.md)",
    )
    ap.add_argument("--from-setpop", action="store_true")
    ap.add_argument(
        "--manifest",
        default=str(ROOT / "2026/cohorts/SETPOP_MANIFEST.tsv"),
    )
    ap.add_argument("--period-start", default="2026-01-01")
    ap.add_argument("--period-end", default="2026-12-31")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    if args.from_setpop:
        ipp, denom, numer, denex, n = counts_from_manifest(
            pathlib.Path(args.manifest), args.cms
        )
        source = f"SETPOP_MANIFEST.tsv aggregate for {args.cms}"
        mode = "setpop-aggregate"
        cohort_size = n
    else:
        missing = [k for k in ("ipp", "denom", "numer") if getattr(args, k) is None]
        if missing:
            raise SystemExit(f"Pass {missing} or --from-setpop")
        ipp, denom, numer, denex = args.ipp, args.denom, args.numer, args.denex
        cohort_size = args.cohort_size if args.cohort_size is not None else denom
        source = args.source
        mode = args.mode

    now = datetime.now(timezone.utc)
    as_of = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    out = pathlib.Path(args.out_dir)
    org = organization()
    report = summary_report(
        cms=args.cms,
        ipp=ipp,
        denom=denom,
        numer=numer,
        denex=denex,
        cohort_size=cohort_size,
        mode=mode,
        source=source,
        period_start=args.period_start,
        period_end=args.period_end,
        as_of=as_of,
    )
    bundle = transaction_bundle(report, org, as_of)

    write_json(out / "Organization-vistaplex-demo.json", org)
    write_json(out / f"{args.cms}-summary-deqm.json", report)
    write_json(out / f"Bundle-{args.cms}-summary-transaction.json", bundle)

    # Also mirror under cohorts for dashboard adjacency
    cohort_out = ROOT / "2026/cohorts/deqm-summary" / args.cms
    write_json(cohort_out / "summary-deqm.json", report)
    write_json(cohort_out / "Organization-vistaplex-demo.json", org)
    write_json(cohort_out / "Bundle-summary-transaction.json", bundle)

    score = report["group"][0]["measureScore"]["value"]
    print(
        f"{args.cms}: IPP={ipp} DENOM={denom} NUMER={numer} DENEX={denex} "
        f"score={score} cohort={cohort_size} mode={mode}",
        flush=True,
    )
    print(f"OUT={out / (args.cms + '-summary-deqm.json')}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
