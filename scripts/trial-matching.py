#!/usr/bin/env python3
"""Phase-3 trial-matching MVP (LINKED_DATA_STRATEGY.md).

Pipeline:
  1. fetch real trial metadata (title/status/eligibility) from
     ClinicalTrials.gov API v2 for the trials in 2026/research/trial-criteria.json
  2. run each hand-structured criterion against a C0X node:
       - kind=sparql  -> population VALUES query (type + codes) -> DFN set
       - kind=age/sex -> Patient resource via /c0x/fhir/Patient
  3. eligible = all criteria met; near-miss = exactly one missing
  4. emit FHIR R4 ResearchStudy + ResearchSubject (status=candidate),
     matches.json (for the C0X UI), report.md, index.json
     into 2026/research/out/

Usage: python3 scripts/trial-matching.py [--base https://devfhir.vistaplex.org]
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone, date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CRITERIA = ROOT / "2026" / "research" / "trial-criteria.json"
OUT = ROOT / "2026" / "research" / "out"
UA = "vista-on-fhir-trial-matching/0.1 (https://github.com/glilly/Vista-on-FHIR)"


def http_json(url: str, data: bytes | None = None, ctype: str | None = None):
    req = urllib.request.Request(url, data=data, headers={"Accept": "application/json", "User-Agent": UA})
    if ctype:
        req.add_header("Content-Type", ctype)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def sparql_dfns(base: str, rtype: str, codes: list[str]) -> set[str]:
    vals = " ".join(f'"{c}"' for c in codes)
    q = (
        "PREFIX c0x: <urn:c0x:>\n"
        "SELECT ?resource ?code WHERE {\n"
        f"  VALUES ?code {{ {vals} }}\n"
        f'  ?resource c0x:type "{rtype}" .\n'
        "  ?resource c0x:code ?code .\n"
        "}\nLIMIT 2000"
    )
    body = http_json(f"{base}/c0x/sparql?population=1&source=intake", q.encode(), "application/sparql-query")
    dfns: set[str] = set()
    for k, row in (body.get("results", {}).get("bindings", {}) or {}).items():
        if isinstance(row, dict) and row.get("dfn", {}).get("value") is not None:
            dfns.add(str(row["dfn"]["value"]))
    return dfns


_patients: dict[str, dict] = {}


def patient(base: str, dfn: str) -> dict:
    if dfn not in _patients:
        qs = urllib.parse.urlencode({"dfn": dfn, "patient": dfn, "_count": 2})
        body = http_json(f"{base}/c0x/fhir/Patient?{qs}")
        res = {}
        for e in body.get("entry", []) or []:
            if e.get("resource", {}).get("resourceType") == "Patient":
                res = e["resource"]
                break
        _patients[dfn] = res
    return _patients[dfn]


def age_of(p: dict) -> int | None:
    bd = p.get("birthDate")
    if not bd:
        return None
    y, m, d = (list(map(int, bd.split("-"))) + [1, 1])[:3]
    today = date.today()
    return today.year - y - ((today.month, today.day) < (m, d))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://devfhir.vistaplex.org")
    args = ap.parse_args()
    base = args.base.rstrip("/")

    spec = json.loads(CRITERIA.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    matches: dict[str, dict] = {}
    studies: list[str] = []
    report = [
        "# Trial-matching MVP run — heuristic stage",
        "",
        f"Date: {now} · node: {base} · criteria: `2026/research/trial-criteria.json`",
        "",
        "Heuristic evidence checks via C0X population SPARQL + Patient demographics.",
        "Value-threshold criteria (marked *CQL*) are presence-only here; the",
        "confirmation stage owns thresholds — same two-stage pattern as the",
        "quality measures. All patients are synthetic.",
        "",
    ]

    for nct, tdef in spec["trials"].items():
        # 1. real trial metadata
        ct = http_json(
            f"https://clinicaltrials.gov/api/v2/studies/{nct}"
            "?fields=NCTId,BriefTitle,OverallStatus,EligibilityCriteria,MinimumAge,MaximumAge,Sex"
        )
        ps = ct.get("protocolSection", {})
        title = ps.get("identificationModule", {}).get("briefTitle", tdef["shortName"])
        status = ps.get("statusModule", {}).get("overallStatus", "UNKNOWN")
        elig_text = ps.get("eligibilityModule", {}).get("eligibilityCriteria", "")

        # 2. evidence criteria -> DFN sets
        crit_results = {}
        pool: set[str] = set()
        for c in tdef["criteria"]:
            if c["kind"] == "sparql":
                dfns = sparql_dfns(base, c["type"], c["codes"])
                crit_results[c["id"]] = {"desc": c["desc"], "kind": "sparql", "dfns": sorted(dfns), "count": len(dfns)}
                pool |= dfns
        # 3. demographic criteria evaluated per pooled candidate
        eligible, near_miss = [], {}
        for dfn in sorted(pool, key=int):
            missing = []
            for c in tdef["criteria"]:
                if c["kind"] == "sparql":
                    if dfn not in crit_results[c["id"]]["dfns"]:
                        missing.append(c["id"])
                elif c["kind"] == "age":
                    a = age_of(patient(base, dfn))
                    if a is None or a < c.get("min", 0) or a > c.get("max", 200):
                        missing.append(c["id"])
                elif c["kind"] == "sex":
                    if patient(base, dfn).get("gender") != c["value"]:
                        missing.append(c["id"])
            if not missing:
                eligible.append(dfn)
            elif len(missing) == 1:
                near_miss[dfn] = missing
        matches[nct] = {
            "title": title,
            "shortName": tdef["shortName"],
            "status": status,
            "eligible": eligible,
            "nearMiss": near_miss,
            "criteria": {k: {"desc": v["desc"], "count": v["count"]} for k, v in crit_results.items()},
            "pool": len(pool),
        }

        # 4. FHIR artifacts
        study = {
            "resourceType": "ResearchStudy",
            "id": f"trial-{nct}",
            "identifier": [{"system": "https://clinicaltrials.gov", "value": nct}],
            "title": title,
            "status": "active",
            "description": elig_text,
            "note": [{"text": f"Structured criteria: 2026/research/trial-criteria.json; heuristic match run {now} on {base} (synthetic cohort)"}],
        }
        (OUT / f"ResearchStudy-{nct}.json").write_text(json.dumps(study, indent=2) + "\n")
        studies.append(f"ResearchStudy-{nct}.json")
        subjects = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "ResearchSubject",
                        "id": f"cand-{nct}-{dfn}",
                        "status": "candidate",
                        "study": {"reference": f"ResearchStudy/trial-{nct}"},
                        "individual": {"reference": f"Patient/{dfn}"},
                    }
                }
                for dfn in eligible
            ],
        }
        (OUT / f"ResearchSubjects-{nct}.json").write_text(json.dumps(subjects, indent=2) + "\n")

        report += [f"## {nct} — {title}", "", f"Registry status: {status} · candidate pool {len(pool)} patients", ""]
        for cid, cr in crit_results.items():
            report.append(f"- `{cid}` {cr['desc']}: **{cr['count']}** patients")
        for c in tdef["criteria"]:
            if c["kind"] != "sparql":
                report.append(f"- `{c['id']}` {c['desc']}: demographic check")
        report += ["", f"**Eligible (all criteria): {len(eligible)}** — DFNs {', '.join(eligible) or '—'}"]
        if near_miss:
            report.append(f"Near-miss (one criterion short): " + "; ".join(f"{d} (missing {m[0]})" for d, m in near_miss.items()))
        report.append("")
        print(f"{nct}: pool={len(pool)} eligible={len(eligible)} near-miss={len(near_miss)}")

    (OUT / "matches.json").write_text(json.dumps({"generatedAt": now, "base": base, "trials": matches}, indent=2) + "\n")
    (OUT / "index.json").write_text(json.dumps({"generatedAt": now, "studies": studies, "matches": "matches.json"}, indent=2) + "\n")
    (OUT / "report.md").write_text("\n".join(report) + "\n")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
