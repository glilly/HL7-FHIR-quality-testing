#!/usr/bin/env python3
"""Trial-matching confirmation stage (sprint Day 3; LINKED_DATA_STRATEGY Phase 3).

The heuristic stage (trial-matching.py) used presence-only SPARQL checks for
value-threshold criteria (flagged cql=true in trial-criteria.json). This
stage fetches the actual observation values per candidate and applies the
threshold — the same two-stage pattern as the quality measures — and writes
a precision scorecard of heuristic vs confirmed.

Currently implements the one cql-flagged criterion in the criteria file:
NCT06862739 "a1c" — latest HbA1c (LOINC 4548-4) >= 8.0 %.

Updates 2026/research/out/matches.json in place (adds a "confirmation"
block per trial) and appends a confirmation section to report.md.
All patients are synthetic.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "2026" / "research" / "out"
A1C_LOINC = "4548-4"
THRESHOLD = 8.0


def fetch_bundle(base: str, dfn: str) -> dict:
    # /showfhir serves the intake graph — the same source the SPARQL heuristic
    # queried (labs live there; they are not all filed to native VistA files)
    with urllib.request.urlopen(f"{base}/showfhir?dfn={dfn}", timeout=300) as r:
        return json.loads(r.read().decode())


def latest_a1c(bundle: dict) -> tuple[float | None, str]:
    best: tuple[str, float] | None = None  # (date, value)
    for e in bundle.get("entry", []):
        res = e.get("resource") or {}
        if res.get("resourceType") != "Observation":
            continue
        codes = [c.get("code") for c in (res.get("code") or {}).get("coding", [])]
        if A1C_LOINC not in codes:
            continue
        vq = res.get("valueQuantity") or {}
        val = vq.get("value")
        if val is None:
            continue
        when = res.get("effectiveDateTime") or res.get("issued") or ""
        if best is None or when > best[0]:
            best = (when, float(val))
    if best is None:
        return None, ""
    return best[1], best[0]


def sparql_dfns(base: str, rtype: str, codes: list[str]) -> set[str]:
    # same population query the heuristic stage uses (trial-matching.py)
    vals = " ".join(f'"{c}"' for c in codes)
    q = (
        "PREFIX c0x: <urn:c0x:>\n"
        "SELECT ?resource ?code WHERE {\n"
        f"  VALUES ?code {{ {vals} }}\n"
        f'  ?resource c0x:type "{rtype}" .\n'
        "  ?resource c0x:code ?code .\n"
        "}\nLIMIT 2000"
    )
    req = urllib.request.Request(
        f"{base}/c0x/sparql?population=1&source=intake", q.encode(),
        {"Content-Type": "application/sparql-query"})
    with urllib.request.urlopen(req, timeout=300) as r:
        body = json.loads(r.read().decode())
    dfns: set[str] = set()
    for _k, row in (body.get("results", {}).get("bindings", {}) or {}).items():
        if isinstance(row, dict) and row.get("dfn", {}).get("value") is not None:
            dfns.add(str(row["dfn"]["value"]))
    return dfns


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://devfhir.vistaplex.org")
    ap.add_argument("--scan-pool", action="store_true",
                    help="also scan every A1c-present patient for latest >= threshold")
    args = ap.parse_args()
    base = args.base.rstrip("/")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    matches = json.loads((OUT / "matches.json").read_text())
    trial = matches["trials"]["NCT06862739"]
    eligible = list(trial.get("eligible", []))
    if not eligible:
        print("no heuristic-eligible candidates to confirm")
        return 0

    per_patient = {}
    confirmed, rejected, novalue = [], [], []
    for dfn in eligible:
        val, when = latest_a1c(fetch_bundle(base, dfn))
        per_patient[dfn] = {"latestA1c": val, "date": when}
        if val is None:
            novalue.append(dfn)
        elif val >= THRESHOLD:
            confirmed.append(dfn)
        else:
            rejected.append(dfn)
        print(f"  dfn {dfn}: latest HbA1c = {val}% ({when or 'n/a'})"
              f" -> {'CONFIRMED' if dfn in confirmed else 'not >= 8%' if val is not None else 'no value'}")

    precision = len(confirmed) / len(eligible)
    trial["confirmation"] = {
        "criterion": "a1c",
        "rule": f"latest HbA1c (LOINC {A1C_LOINC}) >= {THRESHOLD}%",
        "ranAt": now,
        "node": base,
        "perPatient": per_patient,
        "confirmed": confirmed,
        "rejectedByValue": rejected,
        "noValue": novalue,
        "scorecard": {
            "heuristicEligible": len(eligible),
            "confirmedEligible": len(confirmed),
            "precisionOfHeuristic": round(precision, 3),
            "recallNote": ("presence-heuristic recall is 1.0 by construction: a value "
                            "threshold cannot pass without a result being present"),
        },
    }
    pool_scan = None
    if args.scan_pool:
        pool = sorted(sparql_dfns(base, "Observation", [A1C_LOINC]))
        print(f"  pool scan: {len(pool)} patients with any HbA1c on record")
        over = {}
        for dfn in pool:
            if dfn in per_patient:
                val = per_patient[dfn]["latestA1c"]
            else:
                val, _ = latest_a1c(fetch_bundle(base, dfn))
            if val is not None and val >= THRESHOLD:
                over[dfn] = val
        pool_scan = {
            "poolWithA1c": len(pool),
            "latestOverThreshold": over,
            "note": ("empirical recall check: every patient whose latest value "
                      "clears the threshold; compare against heuristic-eligible"),
        }
        trial["confirmation"] = trial.get("confirmation", {})
        print(f"  pool scan: {len(over)} of {len(pool)} have latest HbA1c >= {THRESHOLD}%: {over}")

    if pool_scan:
        trial.setdefault("confirmation", {})["poolScan"] = pool_scan
    (OUT / "matches.json").write_text(json.dumps(matches, indent=1) + "\n")

    lines = [
        "",
        "## Confirmation stage — NCT06862739 HbA1c >= 8%",
        "",
        f"Ran {now} against `{base}` (values read from the intake graph via "
        "/showfhir — the SPARQL stage's source; threshold applied to the "
        "**latest** result).",
        "",
        "| DFN | Latest HbA1c | Date | Confirmed |",
        "|---|---|---|---|",
    ]
    for dfn in eligible:
        pp = per_patient[dfn]
        lines.append(f"| {dfn} | {pp['latestA1c']}% | {pp['date'][:10]} | "
                     f"{'yes' if dfn in confirmed else 'no'} |")
    lines += [
        "",
        f"Scorecard: {len(eligible)} heuristic-eligible -> {len(confirmed)} confirmed "
        f"(heuristic precision {precision:.0%}). Recall is 1.0 by construction "
        "(value thresholds require a present result). Same two-stage pattern as "
        "the CMS quality measures: cheap population SPARQL first, value-accurate "
        "confirmation second.",
    ]
    if pool_scan:
        over = pool_scan["latestOverThreshold"]
        lines += [
            "",
            f"Pool scan: of {pool_scan['poolWithA1c']} patients with any HbA1c on "
            f"record, {len(over)} have a latest value >= {THRESHOLD}%: "
            + (", ".join(f"DFN {d} ({v}%)" for d, v in sorted(over.items())) or "none")
            + ". Cross-reference with the near-miss list: value-qualified patients "
            "excluded only by missing diagnosis/medication codes are exactly the "
            "chart-review candidates a recruitment workflow should surface.",
        ]
    with (OUT / "report.md").open("a") as f:
        f.write("\n".join(lines) + "\n")

    print(f"confirmed {len(confirmed)}/{len(eligible)} "
          f"(precision {precision:.0%}); matches.json + report.md updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
