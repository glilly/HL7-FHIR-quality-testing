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

REPORTERS = {
    "vistaplex": {
        "org_id": "vistaplex-demo",
        "org_name": "VistaPlex FHIR Quality Demo (fhirdev)",
        "display": "VistaPlex FHIR Quality Demo",
        "url": "https://devfhir.vistaplex.org/fhir-quality-dashboards",
        "file_tag": "",
    },
    "rpms": {
        "org_id": "vistaplex-rpms-demo",
        "org_name": "VistaPlex RPMS FHIR Quality Demo (rpmsfhir)",
        "display": "VistaPlex RPMS FHIR Quality Demo",
        "url": "https://rpmsfhir.vistaplex.org/fhir",
        "file_tag": "rpms-",
    },
    "fhirprod": {
        "org_id": "vistaplex-prod-demo",
        "org_name": "VistaPlex FHIR Production Reference (fhir)",
        "display": "VistaPlex FHIR Production Reference",
        "url": "https://fhir.vistaplex.org/fhir",
        "file_tag": "fhirprod-",
    },
}


def measure_canonical(cms: str) -> str:
    # Placeholder until CMS FHIR dQM Measure packages are pinned for EC.
    # DEQM invariant deqm-0 requires a version segment after '|'.
    # CMS165v14 → version 14.0.000 (placeholder, not a published FHIR Measure).
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


def organization(rep: dict[str, str]) -> dict[str, Any]:
    return {
        "resourceType": "Organization",
        "id": rep["org_id"],
        "meta": {
            "profile": [
                "http://hl7.org/fhir/us/qicore/StructureDefinition/qicore-organization"
            ]
        },
        "identifier": [
            {
                "system": "https://vistaplex.org/fhir/sid/organization",
                "value": rep["org_id"],
            }
        ],
        "active": True,
        "name": rep["org_name"],
        "telecom": [{"system": "url", "value": rep["url"]}],
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
    rep: dict[str, str],
) -> dict[str, Any]:
    score = (float(numer) / float(denom)) if denom else 0.0
    rid = f"{cms}-{rep['file_tag']}summary-deqm"
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
                    "display": mode,
                },
                {
                    "system": "https://vistaplex.org/fhir/CodeSystem/quality-cohort-size",
                    "code": str(int(cohort_size)),
                    "display": f"cohort-size={int(cohort_size)}",
                },
                {
                    "system": "https://vistaplex.org/fhir/CodeSystem/quality-source",
                    "code": "provenance",
                    "display": source[:200],
                },
            ],
        },
        # Keep only DEQM measureScoring on .extension (IG golden pattern).
        # Cohort provenance lives in meta.tag to avoid supplementalData slice noise.
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
        ],
        "status": "complete",
        "type": "summary",
        "measure": measure_canonical(cms),
        "date": as_of,
        "reporter": {
            "reference": f"Organization/{rep['org_id']}",
            "display": rep["display"],
        },
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
                            # Avoid example.org (validator rejects example URLs).
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
    org_ref = f"Organization/{org['id']}"
    return {
        "resourceType": "Bundle",
        "id": f"{report['id']}-transaction",
        "type": "transaction",
        "timestamp": ts,
        "entry": [
            {
                "fullUrl": f"urn:uuid:{org['id']}",
                "resource": org,
                "request": {"method": "PUT", "url": org_ref},
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
    ap.add_argument(
        "--reporter",
        choices=sorted(REPORTERS),
        default="vistaplex",
        help="Reporter Organization preset (rpms = rpmsfhir lane)",
    )
    args = ap.parse_args()
    rep = REPORTERS[args.reporter]

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
    if args.reporter != "vistaplex" and args.out_dir == str(OUT_DIR):
        out = OUT_DIR / args.reporter
    org = organization(rep)
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
        rep=rep,
    )
    bundle = transaction_bundle(report, org, as_of)
    tag = rep["file_tag"]

    write_json(out / f"Organization-{rep['org_id']}.json", org)
    write_json(out / f"{args.cms}-{tag}summary-deqm.json", report)
    write_json(out / f"Bundle-{args.cms}-{tag}summary-transaction.json", bundle)

    if args.reporter == "vistaplex" and args.out_dir == str(OUT_DIR):
        # Also mirror under cohorts for dashboard adjacency (VistA lane only,
        # default out-dir only — keeps ad-hoc/regression runs from touching
        # the tracked mirror)
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
    print(f"OUT={out / (args.cms + '-' + tag + 'summary-deqm.json')}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
