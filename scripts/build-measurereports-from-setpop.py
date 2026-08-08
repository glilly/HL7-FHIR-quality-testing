#!/usr/bin/env python3
"""Build FHIR R4 MeasureReports (individual + summary) from SETPOP_MANIFEST.tsv.

Outputs under 2026/cohorts/measurereports/{CMS}/:
  summary.json          — type=summary aggregate
  Patient-{dfn}.json    — type=individual per DFN
  index.json            — lightweight catalog of generated ids/paths
  Bundle-all.json       — collection Bundle of all reports for the measure

These are CQL/SETPOP-derived reports for dashboard linking. Summary reports
use the DEQM Summary MeasureReport profile (QRDA-III replacement). They are
not yet served as native /fhir/MeasureReport resources.
"""
from __future__ import annotations

import argparse
import json
import pathlib
from collections import defaultdict
from datetime import date, datetime, timezone
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
POP_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-population"
SCORING_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-scoring"
IMPROVE_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-improvement-notation"
DEQM_SUMMARY_PROFILE = (
    "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/summary-measurereport-deqm"
)
MEASURE_SCORING_EXT = (
    "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/extension-measureScoring"
)
ORG_REF = "Organization/vistaplex-demo"
DEFAULT_PERIOD = ("2026-01-01", "2026-12-31")


def measure_canonical(cms: str) -> str:
    # DEQM deqm-0 requires |version. Placeholder until CMS FHIR dQM packages pin.
    version = "0.0.1"
    if "v" in cms:
        tail = cms.rsplit("v", 1)[-1]
        if tail.isdigit():
            version = f"{int(tail)}.0.000"
    return f"https://ecqi.healthit.gov/ecqm/ec/{cms}|{version}"


def pop_coding(code: str, display: str) -> dict[str, Any]:
    return {
        "coding": [{"system": POP_SYSTEM, "code": code, "display": display}],
        "text": display,
    }


def population_group(ipp: int, denom: int, numer: int, denex: int) -> dict[str, Any]:
    return {
        "population": [
            {
                "code": pop_coding("initial-population", "Initial Population"),
                "count": int(ipp),
            },
            {
                "code": pop_coding("denominator", "Denominator"),
                "count": int(denom),
            },
            {
                "code": pop_coding("numerator", "Numerator"),
                "count": int(numer),
            },
            {
                "code": pop_coding("denominator-exclusion", "Denominator Exclusion"),
                "count": int(denex),
            },
        ]
    }


def base_report(
    *,
    rid: str,
    rtype: str,
    cms: str,
    period: tuple[str, str],
    as_of: str,
    mode: str,
) -> dict[str, Any]:
    return {
        "resourceType": "MeasureReport",
        "id": rid,
        "meta": {
            "source": "urn:vista:c0fqual:setpop",
            "tag": [
                {
                    "system": "https://vistaplex.org/fhir/CodeSystem/quality-calc-mode",
                    "code": mode or "unknown",
                }
            ],
        },
        "status": "complete",
        "type": rtype,
        "measure": measure_canonical(cms),
        "date": as_of,
        "period": {"start": period[0], "end": period[1]},
        "improvementNotation": {
            "coding": [
                {
                    "system": IMPROVE_SYSTEM,
                    "code": "increase",
                    "display": "Increased score indicates improvement",
                }
            ]
        },
    }


def individual_report(
    cms: str,
    dfn: str,
    ipp: int,
    denom: int,
    numer: int,
    denex: int,
    evidence: str,
    mode: str,
    period: tuple[str, str],
    as_of: str,
) -> dict[str, Any]:
    rid = f"{cms}-Patient-{dfn}"
    rep = base_report(rid=rid, rtype="individual", cms=cms, period=period, as_of=as_of, mode=mode)
    rep["subject"] = {"reference": f"Patient/{dfn}"}
    rep["group"] = [population_group(ipp, denom, numer, denex)]
    if evidence:
        rep["extension"] = [
            {
                "url": "https://vistaplex.org/fhir/StructureDefinition/vista-quality-evidence",
                "valueString": evidence,
            }
        ]
    return rep


def summary_report(
    cms: str,
    rows: list[dict[str, Any]],
    period: tuple[str, str],
    as_of: str,
) -> dict[str, Any]:
    n = len(rows)
    ipp = sum(r["ipp"] for r in rows)
    denom = sum(r["denom"] for r in rows)
    numer = sum(r["numer"] for r in rows)
    denex = sum(r["denex"] for r in rows)
    modes = sorted({r["mode"] for r in rows if r["mode"]})
    mode = modes[0] if len(modes) == 1 else "mixed"
    rid = f"{cms}-summary"
    score = (float(numer) / float(denom)) if denom else 0.0
    rep = base_report(rid=rid, rtype="summary", cms=cms, period=period, as_of=as_of, mode=mode)
    # Upgrade to DEQM Summary profile (QRDA-III replacement path).
    rep["meta"]["profile"] = [DEQM_SUMMARY_PROFILE]
    rep["meta"]["tag"] = [
        {
            "system": "https://vistaplex.org/fhir/CodeSystem/quality-calc-mode",
            "code": mode or "setpop-aggregate",
            "display": mode or "setpop-aggregate",
        },
        {
            "system": "https://vistaplex.org/fhir/CodeSystem/quality-cohort-size",
            "code": str(n),
            "display": f"cohort-size={n}",
        },
        {
            "system": "https://vistaplex.org/fhir/CodeSystem/quality-source",
            "code": "provenance",
            "display": "SETPOP_MANIFEST.tsv (cqm-execution / curated flags)",
        },
    ]
    rep["extension"] = [
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
        }
    ]
    rep["reporter"] = {
        "reference": ORG_REF,
        "display": "VistaPlex FHIR Quality Demo",
    }
    group = population_group(ipp, denom, numer, denex)
    group["code"] = {
        "coding": [
            {
                "system": "https://vistaplex.org/fhir/CodeSystem/measure-group",
                "code": "group-1",
                "display": "group-1",
            }
        ],
        "text": "group-1",
    }
    group["measureScore"] = {"value": round(score, 6)}
    rep["group"] = [group]
    return rep


def read_manifest(path: pathlib.Path) -> dict[str, list[dict[str, Any]]]:
    by_cms: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for line in path.read_text().splitlines()[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 8:
            continue
        cms, dfn, ipp, denom, numer, denex, evid, mode = parts[:8]
        if cms.lower() == "cms":
            continue
        by_cms[cms].append(
            {
                "dfn": dfn,
                "ipp": int(ipp),
                "denom": int(denom),
                "numer": int(numer),
                "denex": int(denex),
                "evidence": evid,
                "mode": mode,
            }
        )
    return by_cms


def write_json(path: pathlib.Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n")


def write_text(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n")


def html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def write_root_index_html(path: pathlib.Path, catalog: dict[str, Any]) -> None:
    rows = []
    for cms, info in sorted(catalog.get("measures", {}).items()):
        deqm = info.get("summaryDeqm") or f"{cms}/summary-deqm.json"
        rows.append(
            "<tr>"
            f"<td><a href=\"{html_escape(cms)}/index.html\">{html_escape(cms)}</a></td>"
            f"<td><a href=\"{html_escape(info['summary'])}\">summary.json</a></td>"
            f"<td><a href=\"{html_escape(deqm)}\">summary-deqm.json</a></td>"
            f"<td><a href=\"{html_escape(info['bundle'])}\">Bundle-all.json</a></td>"
            f"<td>{info.get('patients', 0)}</td>"
            "</tr>"
        )
    body = "\n".join(rows) if rows else "<tr><td colspan='5'>No measures</td></tr>"
    write_text(
        path,
        f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Quality MeasureReports</title>
  <style>
    body {{ font-family: Georgia, "Times New Roman", serif; margin: 2rem; color: #1b1b1b; background: #f7f4ef; }}
    a {{ color: #0b4f6c; }}
    table {{ border-collapse: collapse; width: 100%; background: #fff; }}
    th, td {{ border: 1px solid #d6d0c4; padding: .5rem .75rem; text-align: left; }}
    th {{ background: #ebe4d6; }}
    .muted {{ color: #666; }}
  </style>
</head>
<body>
  <h1>Quality MeasureReports</h1>
  <p class="muted">Generated {html_escape(catalog.get("generatedAt", ""))} from {html_escape(catalog.get("source", "SETPOP"))}.
  %webapi cannot list directories — use this page or explicit JSON paths.</p>
  <p><a href="index.json">index.json</a></p>
  <table>
    <tr><th>Measure</th><th>Summary (SETPOP)</th><th>DEQM freeze</th><th>Bundle</th><th>Patients</th></tr>
    {body}
  </table>
</body>
</html>
""",
    )


def write_measure_index_html(path: pathlib.Path, index: dict[str, Any]) -> None:
    cms = index["measure"]
    rows = []
    for ind in index.get("individuals", []):
        rows.append(
            "<tr>"
            f"<td>{html_escape(str(ind['dfn']))}</td>"
            f"<td><a href=\"{html_escape(ind['path'])}\">{html_escape(ind['id'])}</a></td>"
            f"<td>{ind['ipp']}</td><td>{ind['denom']}</td><td>{ind['numer']}</td><td>{ind['denex']}</td>"
            f"<td class=\"muted\">{html_escape(ind.get('mode', ''))}</td>"
            "</tr>"
        )
    body = "\n".join(rows) if rows else "<tr><td colspan='7'>No individuals</td></tr>"
    c = index.get("counts", {})
    write_text(
        path,
        f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html_escape(cms)} MeasureReports</title>
  <style>
    body {{ font-family: Georgia, "Times New Roman", serif; margin: 2rem; color: #1b1b1b; background: #f7f4ef; }}
    a {{ color: #0b4f6c; }}
    table {{ border-collapse: collapse; width: 100%; background: #fff; }}
    th, td {{ border: 1px solid #d6d0c4; padding: .45rem .7rem; text-align: left; }}
    th {{ background: #ebe4d6; }}
    .muted {{ color: #666; }}
  </style>
</head>
<body>
  <p><a href="../index.html">All measures</a> ·
     <a href="/fhir-quality-dashboards/{html_escape(cms)}">Quality dashboard</a></p>
  <h1>{html_escape(cms)} MeasureReports</h1>
  <p>IPP <strong>{c.get("ipp", 0)}</strong> · DENOM <strong>{c.get("denom", 0)}</strong> ·
     NUMER <strong>{c.get("numer", 0)}</strong> · DENEX <strong>{c.get("denex", 0)}</strong>
     (n={c.get("patients", 0)})</p>
  <p>
    <a href="summary.json">summary.json</a> (SETPOP aggregate, DEQM profile) ·
    <a href="summary-deqm.json">summary-deqm.json</a> (official-cql freeze when present) ·
    <a href="Bundle-all.json">Bundle-all.json</a> ·
    <a href="index.json">index.json</a>
  </p>
  <table>
    <tr><th>DFN</th><th>MeasureReport</th><th>IPP</th><th>DENOM</th><th>NUMER</th><th>DENEX</th><th>Mode</th></tr>
    {body}
  </table>
</body>
</html>
""",
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--manifest",
        default=str(ROOT / "2026/cohorts/SETPOP_MANIFEST.tsv"),
    )
    p.add_argument(
        "--out",
        default=str(ROOT / "2026/cohorts/measurereports"),
    )
    p.add_argument("--period-start", default=DEFAULT_PERIOD[0])
    p.add_argument("--period-end", default=DEFAULT_PERIOD[1])
    p.add_argument("--as-of", default=date.today().isoformat())
    args = p.parse_args()

    manifest = pathlib.Path(args.manifest)
    out_root = pathlib.Path(args.out)
    period = (args.period_start, args.period_end)
    by_cms = read_manifest(manifest)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    catalog: dict[str, Any] = {
        "generatedAt": generated_at,
        "source": str(manifest.relative_to(ROOT)),
        "period": {"start": period[0], "end": period[1]},
        "measures": {},
    }

    for cms, rows in sorted(by_cms.items()):
        mdir = out_root / cms
        if mdir.exists():
            for old in mdir.glob("*.json"):
                old.unlink()
        summary = summary_report(cms, rows, period, args.as_of)
        write_json(mdir / "summary.json", summary)
        # Preserve official-cql DEQM freeze if present under docs/deqm-summary/
        freeze = (
            ROOT / "docs/deqm-summary/prototypes" / f"{cms}-summary-deqm.json"
        )
        if freeze.exists():
            write_json(mdir / "summary-deqm.json", json.loads(freeze.read_text()))
        else:
            # Fallback: SETPOP aggregate already DEQM-profiled
            write_json(mdir / "summary-deqm.json", summary)
        individuals: list[dict[str, Any]] = []
        entries = []
        for row in sorted(rows, key=lambda r: int(r["dfn"])):
            rep = individual_report(
                cms,
                row["dfn"],
                row["ipp"],
                row["denom"],
                row["numer"],
                row["denex"],
                row["evidence"],
                row["mode"],
                period,
                args.as_of,
            )
            fname = f"Patient-{row['dfn']}.json"
            write_json(mdir / fname, rep)
            individuals.append(
                {
                    "id": rep["id"],
                    "dfn": row["dfn"],
                    "path": fname,
                    "ipp": row["ipp"],
                    "denom": row["denom"],
                    "numer": row["numer"],
                    "denex": row["denex"],
                    "mode": row["mode"],
                }
            )
            entries.append({"fullUrl": f"MeasureReport/{rep['id']}", "resource": rep})
        entries.insert(0, {"fullUrl": f"MeasureReport/{summary['id']}", "resource": summary})
        bundle = {
            "resourceType": "Bundle",
            "id": f"{cms}-measurereports",
            "type": "collection",
            "timestamp": generated_at,
            "total": len(entries),
            "entry": entries,
        }
        write_json(mdir / "Bundle-all.json", bundle)
        index = {
            "measure": cms,
            "canonical": measure_canonical(cms),
            "summary": "summary.json",
            "summaryDeqm": "summary-deqm.json",
            "bundle": "Bundle-all.json",
            "individuals": individuals,
            "counts": {
                "patients": len(rows),
                "ipp": sum(r["ipp"] for r in rows),
                "denom": sum(r["denom"] for r in rows),
                "numer": sum(r["numer"] for r in rows),
                "denex": sum(r["denex"] for r in rows),
            },
        }
        write_json(mdir / "index.json", index)
        write_measure_index_html(mdir / "index.html", index)
        catalog["measures"][cms] = {
            "path": f"{cms}/index.json",
            "html": f"{cms}/index.html",
            "summary": f"{cms}/summary.json",
            "summaryDeqm": f"{cms}/summary-deqm.json",
            "bundle": f"{cms}/Bundle-all.json",
            "patients": len(rows),
        }
        print(
            f"{cms}: {len(rows)} individual + summary "
            f"(IPP={index['counts']['ipp']} DENOM={index['counts']['denom']} "
            f"NUMER={index['counts']['numer']})",
            flush=True,
        )

    write_json(out_root / "index.json", catalog)
    write_root_index_html(out_root / "index.html", catalog)
    print(f"OUT={out_root}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
