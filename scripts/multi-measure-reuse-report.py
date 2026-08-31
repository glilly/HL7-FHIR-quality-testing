#!/usr/bin/env python3
"""Multi-measure cohort reuse orchestrator (Phase 7).

Does NOT revive Tacoma fhir-patient-generator. Workflow:

  1. Inventory existing patients from SETPOP_MANIFEST and/or cqm-execution
     batch reports under 2026/cohorts/*/
  2. Build a patient → measures membership matrix (reuse across CMS*)
  3. For a target measure, report who already qualifies vs gap cells
  4. Emit a reuse report JSON + optional SETPOP rows for cross-fill

Official membership remains cqm-execution / dashboard Re-evaluate CQL.
C0X POPIDX / SPARQL is the fast prefilter when scanning fhir-intake live.

Usage:
  python3 scripts/multi-measure-reuse-report.py \\
    --target CMS165v14 \\
    --out 2026/cohorts/MULTI_MEASURE_REUSE_REPORT.json

  python3 scripts/multi-measure-reuse-report.py --target CMS2v15 --need-numer 10
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
from collections import defaultdict
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
COHORTS = ROOT / "2026" / "cohorts"
DEFAULT_SHORTLIST = [
    "CMS165v14",
    "CMS122v14",
    "CMS130v14",
    "CMS138v14",
    "CMS2v15",
    "CMS125v14",
    "CMS22v14",
    "CMS131v14",
    "CMS68v15",
]


def load_setpop_manifest(path: pathlib.Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows = []
    with path.open() as f:
        r = csv.DictReader(f, delimiter="\t")
        for row in r:
            rows.append(
                {
                    "cms": row.get("cms") or row.get("measure") or "",
                    "dfn": str(row.get("dfn") or "").strip(),
                    "ipp": int(row.get("ipp") or 0),
                    "denom": int(row.get("denom") or 0),
                    "numer": int(row.get("numer") or 0),
                    "denex": int(row.get("denex") or 0),
                    "source": "setpop_manifest",
                }
            )
    return rows


def load_cqm_batch(path: pathlib.Path, cms: str) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []
    rows = []
    # Accept either list of patient results or {patients: [...]} / batch shapes
    items = data if isinstance(data, list) else data.get("patients") or data.get("results") or []
    if isinstance(data, dict) and not items and "byPatient" in data:
        items = [{"id": k, **v} for k, v in data["byPatient"].items()]
    for it in items:
        if not isinstance(it, dict):
            continue
        dfn = str(it.get("dfn") or it.get("DFN") or it.get("id") or "").strip()
        ipp = int(it.get("ipp") or it.get("IPP") or 0)
        denom = int(it.get("denom") or it.get("DENOM") or 0)
        numer = int(it.get("numer") or it.get("NUMER") or 0)
        denex = int(it.get("denex") or it.get("DENEX") or 0)
        # nested populationCriteria
        pc = it.get("populationCriteria") or it.get("PopulationCriteria1") or {}
        if isinstance(pc, dict):
            ipp = ipp or int(bool(pc.get("IPP") or pc.get("ipp")))
            denom = denom or int(bool(pc.get("DENOM") or pc.get("denom")))
            numer = numer or int(bool(pc.get("NUMER") or pc.get("numer")))
            denex = denex or int(bool(pc.get("DENEX") or pc.get("denex")))
        if not dfn and not (ipp or denom or numer):
            continue
        rows.append(
            {
                "cms": cms,
                "dfn": dfn or it.get("patientName") or it.get("name") or "",
                "ipp": ipp,
                "denom": denom,
                "numer": numer,
                "denex": denex,
                "source": path.name,
            }
        )
    return rows


def inventory(shortlist: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    man = COHORTS / "SETPOP_MANIFEST.tsv"
    rows.extend(load_setpop_manifest(man))
    for cms in shortlist:
        batch = COHORTS / cms / "reports" / "cqm-execution-batch.json"
        rows.extend(load_cqm_batch(batch, cms))
        # also summary sidecar if present
        summary = COHORTS / cms / "reports" / "cqm-execution-summary.json"
        if summary.is_file() and not batch.is_file():
            try:
                s = json.loads(summary.read_text())
                # summary-only: no per-patient — skip
                _ = s
            except Exception:
                pass
    return rows


def build_matrix(rows: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, int]]]:
    """patient_key -> cms -> {ipp,denom,numer,denex}"""
    matrix: dict[str, dict[str, dict[str, int]]] = defaultdict(dict)
    for r in rows:
        key = r["dfn"]
        if not key:
            continue
        cms = r["cms"]
        if not cms:
            continue
        cur = matrix[key].get(cms) or {"ipp": 0, "denom": 0, "numer": 0, "denex": 0}
        for k in ("ipp", "denom", "numer", "denex"):
            cur[k] = max(cur[k], int(r.get(k) or 0))
        matrix[key][cms] = cur
    return matrix


def gap_report(
    matrix: dict[str, dict[str, dict[str, int]]],
    target: str,
    need_ipp: int,
    need_numer: int,
) -> dict[str, Any]:
    reuse_ipp = []
    reuse_numer = []
    multi = []
    for patient, measures in matrix.items():
        hits = [m for m, flags in measures.items() if flags.get("ipp") or flags.get("numer")]
        if len(hits) > 1:
            multi.append({"patient": patient, "measures": hits})
        flags = measures.get(target) or {}
        if flags.get("ipp") or flags.get("denom"):
            reuse_ipp.append(patient)
        if flags.get("numer"):
            reuse_numer.append(patient)
    gap_ipp = max(0, need_ipp - len(reuse_ipp))
    gap_numer = max(0, need_numer - len(reuse_numer))
    return {
        "target": target,
        "reuseIppCount": len(reuse_ipp),
        "reuseNumerCount": len(reuse_numer),
        "reuseIppSample": reuse_ipp[:25],
        "reuseNumerSample": reuse_numer[:25],
        "needIpp": need_ipp,
        "needNumer": need_numer,
        "gapIppToSynthesize": gap_ipp,
        "gapNumerToSynthesize": gap_numer,
        "multiMeasurePatients": len(multi),
        "multiMeasureSample": multi[:40],
        "guidance": [
            "Prefer SETPOP cross-fill from reuse* lists before Synthea.",
            "Use C0X /c0x/cohort?code=… or measure presets (POPIDX) to prefilter fhir-intake.",
            "Confirm with cds1 /quality/evaluate-cohort or dashboard Re-evaluate CQL.",
            "Only synthesize gapIppToSynthesize / gapNumerToSynthesize cells.",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True, help="CMS measure id e.g. CMS165v14")
    ap.add_argument("--shortlist", nargs="*", default=DEFAULT_SHORTLIST)
    ap.add_argument("--need-ipp", type=int, default=18)
    ap.add_argument("--need-numer", type=int, default=10)
    ap.add_argument(
        "--out",
        type=pathlib.Path,
        default=COHORTS / "MULTI_MEASURE_REUSE_REPORT.json",
    )
    args = ap.parse_args()

    rows = inventory(args.shortlist)
    matrix = build_matrix(rows)
    gaps = gap_report(matrix, args.target, args.need_ipp, args.need_numer)

    # Cross-fill suggestions: patients in other measures with no target row yet
    cross = []
    for patient, measures in matrix.items():
        if args.target in measures:
            continue
        others = [m for m, f in measures.items() if f.get("ipp") or f.get("numer")]
        if others:
            cross.append({"patient": patient, "alreadyIn": others})

    report = {
        "mode": "multi-measure-reuse",
        "poolPatients": len(matrix),
        "inventoryRows": len(rows),
        "shortlist": args.shortlist,
        "gaps": gaps,
        "crossFillCandidates": cross[:50],
        "crossFillCount": len(cross),
        "nextSteps": [
            f"If gapIppToSynthesize={gaps['gapIppToSynthesize']} or gapNumerToSynthesize={gaps['gapNumerToSynthesize']}, run Synthea/QDM generation only for those cells.",
            "Load new bundles → fhir-intake → POST /c0x/index/reindex (builds POPIDX).",
            "Re-run this report; then fhirdev-apply-setpop.sh / dashboard CQL.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"wrote": str(args.out), "poolPatients": len(matrix), "gaps": gaps}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
