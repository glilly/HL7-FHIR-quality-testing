#!/usr/bin/env python3
"""Round-2 C0X SPARQL IPP-approximation experiment runner.

Posts a per-measure SPARQL query to /c0x/sparql?population=1, collects
candidate DFNs from the dfn bindings, and scores them against:
  - the round-1 single-code heuristic list (2026/cohorts/c0x-heuristic/IPP_SUMMARY.tsv)
  - the official-CQL IPP truth list (2026/cohorts/c0x-sparql-round2/truth/{CMS}-ipp-dfns.txt)
    when present.

See docs/C0X_SPARQL_ROUND2_PLAN.md.

Usage:
  scripts/c0x-sparql-round2.py --cms CMS165v14 [--base https://devfhir.vistaplex.org]
"""

import argparse
import json
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R2DIR = ROOT / "2026/cohorts/c0x-sparql-round2"
IPP_SUMMARY = ROOT / "2026/cohorts/c0x-heuristic/IPP_SUMMARY.tsv"


def run_sparql(base: str, query: str) -> dict:
    url = f"{base.rstrip('/')}/c0x/sparql?population=1"
    req = urllib.request.Request(
        url, data=query.encode(), method="POST",
        headers={"Content-Type": "text/plain"},
    )
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, timeout=300, context=ctx) as resp:
        return json.loads(resp.read())


def extract_dfns(result: dict) -> set[str]:
    dfns = set()
    bindings = result.get("results", {}).get("bindings", {})
    rows = bindings.values() if isinstance(bindings, dict) else bindings
    for row in rows:
        if not isinstance(row, dict):
            continue
        dfn = row.get("dfn", {})
        if isinstance(dfn, dict) and dfn.get("value") is not None:
            dfns.add(str(dfn["value"]))
    return dfns


def round1_dfns(cms: str) -> set[str] | None:
    if not IPP_SUMMARY.exists():
        return None
    for line in IPP_SUMMARY.read_text().splitlines()[1:]:
        parts = line.split("\t")
        if parts and parts[0] == cms:
            return {d for d in parts[-1].split(",") if d.strip()}
    return None


def score(candidates: set[str], truth: set[str]) -> dict:
    tp = candidates & truth
    fp = candidates - truth
    fn = truth - candidates
    return {
        "truth_size": len(truth),
        "candidates": len(candidates),
        "true_positive": len(tp),
        "false_positive": len(fp),
        "false_negative": len(fn),
        "precision": round(len(tp) / len(candidates), 3) if candidates else None,
        "recall": round(len(tp) / len(truth), 3) if truth else None,
        "missed_dfns": sorted(fn, key=lambda d: (len(d), d)),
        "extra_dfns": sorted(fp, key=lambda d: (len(d), d)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cms", required=True, help="e.g. CMS165v14")
    ap.add_argument("--base", default="https://devfhir.vistaplex.org")
    ap.add_argument("--query", help="override query file path")
    args = ap.parse_args()

    qpath = Path(args.query) if args.query else R2DIR / "queries" / f"{args.cms}.sparql"
    if not qpath.exists():
        print(f"missing query file: {qpath}", file=sys.stderr)
        return 1
    query = qpath.read_text()

    result = run_sparql(args.base, query)
    if result.get("error"):
        print(f"SPARQL error: {result['error']}", file=sys.stderr)
        return 1
    candidates = extract_dfns(result)

    out = {
        "cms": args.cms,
        "base": args.base,
        "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "query_file": str(qpath.relative_to(ROOT)),
        "query": query,
        "server_candidates_field": result.get("candidates"),
        "candidate_count": len(candidates),
        "candidate_dfns": sorted(candidates, key=lambda d: (len(d), d)),
    }

    r1 = round1_dfns(args.cms)
    if r1 is not None:
        out["round1_heuristic"] = {
            "count": len(r1),
            "new_in_round2": sorted(candidates - r1, key=lambda d: (len(d), d)),
            "dropped_from_round1": sorted(r1 - candidates, key=lambda d: (len(d), d)),
        }

    truth_path = R2DIR / "truth" / f"{args.cms}-ipp-dfns.txt"
    if truth_path.exists():
        truth = {l.strip() for l in truth_path.read_text().splitlines() if l.strip()}
        out["vs_cql_ipp"] = score(candidates, truth)
        if r1 is not None:
            out["round1_vs_cql_ipp"] = score(r1, truth)

    R2DIR.mkdir(parents=True, exist_ok=True)
    out_path = R2DIR / f"{args.cms}-round2.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    (R2DIR / f"{args.cms}-candidates.txt").write_text(
        "\n".join(out["candidate_dfns"]) + "\n"
    )

    print(f"{args.cms}: {len(candidates)} candidates -> {out_path.relative_to(ROOT)}")
    if "vs_cql_ipp" in out:
        s = out["vs_cql_ipp"]
        print(
            f"  vs CQL IPP({s['truth_size']}): precision={s['precision']} "
            f"recall={s['recall']} missed={s['missed_dfns']}"
        )
    if "round1_vs_cql_ipp" in out:
        s = out["round1_vs_cql_ipp"]
        print(f"  round1 baseline: precision={s['precision']} recall={s['recall']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
