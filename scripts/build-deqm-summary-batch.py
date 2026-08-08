#!/usr/bin/env python3
"""Build DEQM Summary MeasureReports for every row in a counts TSV."""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_TSV = ROOT / "docs/deqm-summary/official-cql-selected18-counts.tsv"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--counts", default=str(DEFAULT_TSV))
    ap.add_argument("--check", action="store_true", help="run structural gate per report")
    args = ap.parse_args()

    path = pathlib.Path(args.counts)
    built: list[str] = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 7:
            raise SystemExit(f"bad row: {line}")
        cms, ipp, denom, numer, denex, cohort, note = parts[:7]
        cmd = [
            sys.executable,
            str(ROOT / "scripts/build-deqm-summary.py"),
            "--cms",
            cms,
            "--ipp",
            ipp,
            "--denom",
            denom,
            "--numer",
            numer,
            "--denex",
            denex,
            "--cohort-size",
            cohort,
            "--mode",
            "official-cql",
            "--source",
            note,
        ]
        print("+", " ".join(cmd), flush=True)
        subprocess.check_call(cmd)
        report = ROOT / "docs/deqm-summary/prototypes" / f"{cms}-summary-deqm.json"
        if args.check:
            subprocess.check_call(
                [sys.executable, str(ROOT / "scripts/check-deqm-summary.py"), str(report)]
            )
        built.append(cms)

    # Multi-measure transaction: Organization once + all MeasureReports
    import json
    from datetime import datetime, timezone

    org = json.loads(
        (ROOT / "docs/deqm-summary/prototypes/Organization-vistaplex-demo.json").read_text()
    )
    entries = [
        {
            "fullUrl": "urn:uuid:vistaplex-demo",
            "resource": org,
            "request": {"method": "PUT", "url": "Organization/vistaplex-demo"},
        }
    ]
    for cms in built:
        report = json.loads(
            (ROOT / "docs/deqm-summary/prototypes" / f"{cms}-summary-deqm.json").read_text()
        )
        entries.append(
            {
                "fullUrl": f"urn:uuid:{report['id']}",
                "resource": report,
                "request": {
                    "method": "PUT",
                    "url": f"MeasureReport/{report['id']}",
                },
            }
        )
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    bundle = {
        "resourceType": "Bundle",
        "id": "deqm-summary-selected18-transaction",
        "type": "transaction",
        "timestamp": ts,
        "entry": entries,
    }
    out = ROOT / "docs/deqm-summary/prototypes/Bundle-selected18-summary-transaction.json"
    out.write_text(json.dumps(bundle, indent=2) + "\n")
    print(f"BUILT={len(built)} measures; MULTI={out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
