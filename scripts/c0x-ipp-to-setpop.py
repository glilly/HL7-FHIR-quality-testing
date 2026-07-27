#!/usr/bin/env python3
"""Fetch fhirdev $everything for C0X IPP DFNs, run CQL, merge SETPOP_MANIFEST.tsv."""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]


def fetch_patient_bundle(base: str, dfn: str, dest: pathlib.Path) -> None:
    # Codex patient collection Bundle (Accept JSON). $everything is not wired as Bundle here.
    url = f"{base.rstrip('/')}/fhir?dfn={dfn}"
    req = urllib.request.Request(url, headers={"Accept": "application/fhir+json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        body = resp.read()
    dest.write_bytes(body)
    data = json.loads(body)
    if data.get("resourceType") != "Bundle":
        raise RuntimeError(f"{dfn}: not a Bundle ({data.get('resourceType')})")
    if not data.get("entry"):
        raise RuntimeError(f"{dfn}: empty Bundle")


def load_c0x_dfns(summary: pathlib.Path, measures: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for line in summary.read_text().splitlines()[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        cms, dfns = parts[0], parts[5] if len(parts) > 5 else ""
        if cms not in measures:
            continue
        out[cms] = [d for d in dfns.split(",") if d.strip()]
    return out


def merge_setpop(manifest: pathlib.Path, cms: str, results_tsv: pathlib.Path) -> int:
    existing = manifest.read_text().splitlines()
    header = existing[0] if existing else "cms\tdfn\tipp\tdenom\tnumer\tdenex\tevidence\tmode"
    rows = {}
    for line in existing[1:]:
        if not line.strip():
            continue
        p = line.split("\t")
        rows[(p[0], p[1])] = line

    added = 0
    for line in results_tsv.read_text().splitlines()[1:]:
        if not line.strip():
            continue
        dfn, _path, ipp, denom, numer, denex, _el = (line.split("\t") + [""] * 7)[:7]
        evid = f"c0x-ipp->$everything cql={ipp}/{denom}/{numer}/{denex}"
        row = f"{cms}\t{dfn}\t{ipp}\t{denom}\t{numer}\t{denex}\t{evid}\tofficial-cql"
        key = (cms, dfn)
        if key not in rows:
            added += 1
        rows[key] = row

    lines = [header] + [rows[k] for k in sorted(rows.keys(), key=lambda x: (x[0], int(x[1])))]
    manifest.write_text("\n".join(lines) + "\n")
    return added


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="https://devfhir.vistaplex.org")
    ap.add_argument(
        "--summary",
        default=str(ROOT / "2026/cohorts/c0x-heuristic/IPP_SUMMARY.tsv"),
    )
    ap.add_argument(
        "--measures",
        default="CMS165v14,CMS122v14,CMS130v14",
        help="Comma-separated measure ids",
    )
    ap.add_argument(
        "--manifest",
        default=str(ROOT / "2026/cohorts/SETPOP_MANIFEST.tsv"),
    )
    ap.add_argument("--skip-fetch", action="store_true")
    ap.add_argument("--skip-eval", action="store_true")
    args = ap.parse_args()

    measures = [m.strip() for m in args.measures.split(",") if m.strip()]
    c0x = load_c0x_dfns(pathlib.Path(args.summary), measures)
    if not c0x:
        print("No C0X DFNs for requested measures", file=sys.stderr)
        return 1

    for cms, dfns in c0x.items():
        bundle_dir = ROOT / "2026/cohorts/c0x-heuristic/bundles" / cms
        bundle_dir.mkdir(parents=True, exist_ok=True)
        man_lines = ["bundle_path\tdfn\n"]
        for dfn in dfns:
            dest = bundle_dir / f"{dfn}.json"
            if not args.skip_fetch or not dest.exists():
                print(f"fetch {cms} DFN {dfn}", flush=True)
                try:
                    fetch_patient_bundle(args.base_url, dfn, dest)
                except Exception as exc:
                    print(f"FAIL fetch {dfn}: {exc}", file=sys.stderr)
                    continue
            man_lines.append(f"{dest}\t{dfn}\n")
        man_path = bundle_dir / "eval-manifest.tsv"
        man_path.write_text("".join(man_lines))
        print(f"{cms}: {len(man_lines)-1} bundles -> {man_path}", flush=True)

        if args.skip_eval:
            continue
        cmd = [
            "node",
            str(ROOT / "scripts/evaluate-cqm-manifest.js"),
            cms,
            "--manifest",
            str(man_path),
        ]
        print(" ".join(cmd), flush=True)
        subprocess.check_call(cmd, cwd=str(ROOT))
        results = ROOT / "2026/cohorts" / cms / "c0x-cql" / "cql-results.tsv"
        added = merge_setpop(pathlib.Path(args.manifest), cms, results)
        print(f"{cms}: merged SETPOP (+{added} new/updated keys)", flush=True)

    print(f"MANIFEST={args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
