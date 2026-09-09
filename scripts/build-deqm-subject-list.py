#!/usr/bin/env python3
"""Build a DEQM Subject-List MeasureReport (+ transaction Bundle) from SETPOP flags.

DEQM STU5: type=subject-list; each group.population carries subjectResults ->
a contained List (profile indv-measurereport-list) whose entries reference the
per-patient individual MeasureReports (built by build-deqm-individual.py
shapes). Output: docs/deqm-summary/prototypes/{CMS}-subjectlist-deqm.json and
Bundle-{CMS}-subjectlist-transaction.json (subject-list + individuals +
reporter Organization) ready for the validator and deqm-test-server.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from datetime import datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
SL_PROFILE = "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/subjectlist-measurereport-deqm"
INDV_PROFILE = "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/indv-measurereport-deqm"
LIST_PROFILE = "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/indv-measurereport-list"
SCORING_EXT = "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/extension-measureScoring"
POP_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-population"
SCORING_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-scoring"
IMPROVE_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-improvement-notation"
ORG_ID = "vistaplex-demo"

POPS = [  # (manifest key, population code, display)
    ("ipp", "initial-population", "Initial Population"),
    ("denom", "denominator", "Denominator"),
    ("numer", "numerator", "Numerator"),
    ("denex", "denominator-exclusion", "Denominator Exclusion"),
]


def measure_canonical(cms: str) -> str:
    version = "0.0.1"
    if "v" in cms:
        tail = cms.rsplit("v", 1)[-1]
        if tail.isdigit():
            version = f"{int(tail)}.0.000"
    return f"https://ecqi.healthit.gov/ecqm/ec/{cms}|{version}"


def rows_for(manifest: pathlib.Path, cms: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for line in manifest.read_text().splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) < 8 or parts[0] != cms:
            continue
        out[parts[1]] = {
            "ipp": int(parts[2]), "denom": int(parts[3]),
            "numer": int(parts[4]), "denex": int(parts[5]),
            "evidence": parts[6], "mode": parts[7],
        }
    if not out:
        raise SystemExit(f"No SETPOP rows for {cms} in {manifest}")
    return out


def indv_report(cms: str, dfn: str, row: dict, period: dict, as_of: str) -> dict[str, Any]:
    rep: dict[str, Any] = {
        "resourceType": "MeasureReport",
        "id": f"{cms}-Patient-{dfn}-deqm",
        "meta": {"profile": [INDV_PROFILE]},
        "extension": [{
            "url": SCORING_EXT,
            "valueCodeableConcept": {"coding": [{"system": SCORING_SYSTEM, "code": "proportion"}]},
        }],
        "status": "complete",
        "type": "individual",
        "measure": measure_canonical(cms),
        "subject": {"reference": f"Patient/{dfn}"},
        "date": as_of,
        "reporter": {"reference": f"Organization/{ORG_ID}"},
        "period": period,
        "improvementNotation": {"coding": [{"system": IMPROVE_SYSTEM, "code": "increase"}]},
        "group": [{
            "population": [
                {"code": {"coding": [{"system": POP_SYSTEM, "code": code, "display": disp}]},
                 "count": int(row[key])}
                for key, code, disp in POPS
            ],
        }],
    }
    if row["denom"] and not row["denex"]:
        rep["group"][0]["measureScore"] = {"value": float(row["numer"]) / max(row["denom"], 1)}
    return rep


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cms", default="CMS165v14")
    ap.add_argument("--manifest", default=str(ROOT / "2026/cohorts/SETPOP_MANIFEST.tsv"))
    ap.add_argument("--period-start", default="2026-01-01")
    ap.add_argument("--period-end", default="2026-12-31")
    args = ap.parse_args()

    rows = rows_for(pathlib.Path(args.manifest), args.cms)
    as_of = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    period = {"start": args.period_start, "end": args.period_end}

    contained, groups_pop = [], []
    for key, code, disp in POPS:
        members = [d for d, r in sorted(rows.items()) if r[key]]
        lid = f"list-{code}"
        lst: dict[str, Any] = {
            "resourceType": "List",
            "id": lid,
            "meta": {"profile": [LIST_PROFILE]},
            "status": "current",
            "mode": "snapshot",
        }
        if members:
            lst["entry"] = [{"item": {"reference": f"MeasureReport/{args.cms}-Patient-{d}-deqm"}}
                            for d in members]
        else:  # profile requires subjectResults 1..1; empty List, never entry: []
            lst["emptyReason"] = {"coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/list-empty-reason",
                "code": "unavailable"}], "text": "No subjects in this population"}
        contained.append(lst)
        groups_pop.append({
            "code": {"coding": [{"system": POP_SYSTEM, "code": code, "display": disp}]},
            "count": len(members),
            "subjectResults": {"reference": f"#{lid}"},
        })

    sl: dict[str, Any] = {
        "resourceType": "MeasureReport",
        "id": f"{args.cms}-subjectlist-deqm",
        "meta": {"profile": [SL_PROFILE]},
        "contained": contained,
        "extension": [{
            "url": SCORING_EXT,
            "valueCodeableConcept": {"coding": [{"system": SCORING_SYSTEM, "code": "proportion"}]},
        }],
        "status": "complete",
        "type": "subject-list",
        "measure": measure_canonical(args.cms),
        "date": as_of,
        "reporter": {"reference": f"Organization/{ORG_ID}"},
        "period": period,
        "improvementNotation": {"coding": [{"system": IMPROVE_SYSTEM, "code": "increase"}]},
        "group": [{"population": groups_pop}],
    }

    org = {
        "resourceType": "Organization",
        "id": ORG_ID,
        "meta": {"profile": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-organization"]},
        "active": True,
        "name": "VistAplex Demo Reporting Organization",
        "identifier": [{"system": "urn:ietf:rfc:3986",
                        "value": "urn:uuid:5b1e6f4a-vistaplex-demo"}],
        "telecom": [{"system": "url", "value": "https://vistaplex.org"}],
        "address": [{"country": "US"}],
    }

    entries = [
        {"resource": sl, "request": {"method": "PUT", "url": f"MeasureReport/{sl['id']}"}},
        {"resource": org, "request": {"method": "PUT", "url": f"Organization/{ORG_ID}"}},
    ]
    for dfn, row in sorted(rows.items()):
        rep = indv_report(args.cms, dfn, row, period, as_of)
        entries.append({"resource": rep,
                        "request": {"method": "PUT", "url": f"MeasureReport/{rep['id']}"}})
    bundle = {"resourceType": "Bundle", "type": "transaction", "entry": entries}

    outdir = ROOT / "docs/deqm-summary/prototypes"
    outdir.mkdir(parents=True, exist_ok=True)
    slf = outdir / f"{args.cms}-subjectlist-deqm.json"
    bf = outdir / f"Bundle-{args.cms}-subjectlist-transaction.json"
    slf.write_text(json.dumps(sl, indent=2) + "\n")
    bf.write_text(json.dumps(bundle, indent=2) + "\n")
    counts = {code: p["count"] for p, (_k, code, _d) in zip(groups_pop, POPS)}
    print(f"{args.cms}: {len(rows)} subjects; populations {counts}")
    print(f"subject-list: {slf}\nbundle: {bf} ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
