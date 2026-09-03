#!/usr/bin/env python3
"""Phase-2 confirmation for round-2 C0X SPARQL candidates.

For each measure: read {CMS}-candidates.txt, fetch each candidate's
round-trip export bundle (GET /fhir?dfn=), run official CQL
(scripts/evaluate-cqm-manifest.js) over the exports, merge the confirmed
IPP DFNs into truth/{CMS}-ipp-dfns.txt, and rescore with
scripts/c0x-sparql-round2.py. This matches the round-1 c0x-cql lane,
which also evaluated the server's own export surface.

Usage:
  scripts/c0x-round2-confirm.py --cms CMS165v14 [--base https://devfhir.vistaplex.org]
"""

import argparse
import json
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R2DIR = ROOT / "2026/cohorts/c0x-sparql-round2"

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def fetch_bundle(base: str, dfn: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 100:
        return True
    url = f"{base.rstrip('/')}/fhir?dfn={dfn}"
    try:
        with urllib.request.urlopen(url, timeout=600, context=CTX) as resp:
            data = resp.read()
        doc = json.loads(data)
        if doc.get("resourceType") != "Bundle":
            print(f"  dfn {dfn}: not a Bundle", file=sys.stderr)
            return False
        dest.write_bytes(data)
        return True
    except Exception as exc:
        print(f"  dfn {dfn}: export fetch failed: {exc}", file=sys.stderr)
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cms", required=True)
    ap.add_argument("--base", default="https://devfhir.vistaplex.org")
    ap.add_argument("--skip-eval", action="store_true",
                    help="only rebuild truth from an existing cql run")
    args = ap.parse_args()
    cms = args.cms

    cand_file = R2DIR / f"{cms}-candidates.txt"
    if not cand_file.exists():
        print(f"missing {cand_file}; run c0x-sparql-round2.py first", file=sys.stderr)
        return 1
    dfns = [l.strip() for l in cand_file.read_text().splitlines() if l.strip()]

    out_dir = R2DIR / f"{cms}-cql"
    bdir = out_dir / "fhir-bundles"
    bdir.mkdir(parents=True, exist_ok=True)
    manifest = R2DIR / f"{cms}-eval-manifest.tsv"
    rows, failed = [], []
    for dfn in dfns:
        dest = bdir / f"{dfn}.json"
        if fetch_bundle(args.base, dfn, dest):
            rows.append(f"{dest.relative_to(ROOT)}\t{dfn}")
        else:
            failed.append(dfn)
    manifest.write_text("bundle_path\tdfn\n" + "\n".join(rows) + "\n")
    print(f"{cms}: {len(rows)} export bundles, {len(failed)} failed {failed}")

    if not args.skip_eval:
        cmd = ["node", str(ROOT / "scripts/evaluate-cqm-manifest.js"), cms,
               "--manifest", str(manifest), "--out-dir", str(out_dir)]
        res = subprocess.run(cmd, cwd=ROOT)
        if res.returncode != 0:
            print(f"  evaluator failed rc={res.returncode}", file=sys.stderr)
            return 1

    results = out_dir / "cql-results.tsv"
    confirmed = set()
    for line in results.read_text().splitlines()[1:]:
        parts = line.split("\t")
        if len(parts) >= 3 and parts[2] == "1":
            confirmed.add(parts[0])

    truth_file = R2DIR / "truth" / f"{cms}-ipp-dfns.txt"
    prior = set()
    if truth_file.exists():
        prior = {l.strip() for l in truth_file.read_text().splitlines() if l.strip()}
    merged = sorted(prior | confirmed, key=lambda d: (len(d), d))
    truth_file.parent.mkdir(parents=True, exist_ok=True)
    truth_file.write_text("\n".join(merged) + "\n")
    print(f"  CQL IPP confirmed {len(confirmed)} of {len(rows)} evaluated; "
          f"truth now {len(merged)} (was {len(prior)})")

    subprocess.run([sys.executable, str(ROOT / "scripts/c0x-sparql-round2.py"),
                    "--cms", cms, "--base", args.base], cwd=ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
