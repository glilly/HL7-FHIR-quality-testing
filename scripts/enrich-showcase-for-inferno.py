#!/usr/bin/env python3
"""Enrich showcase bundles with measure-specific FHIR facts for Inferno coverage.

Writes enriched transaction bundles under 2026/patients/enriched/<cms>/ and a
load manifest. Intended for overnight marathon: add Smoking Status, PHQ screen,
FIT/colonoscopy, mammography, eye exam, etc. when missing.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import pathlib
import uuid

NOW = "2026-06-15T14:30:00Z"


def uid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


def add_entry(bundle: dict, resource: dict, method: str = "POST") -> str:
    full = f"urn:uuid:{resource['id']}"
    bundle.setdefault("entry", []).append(
        {
            "fullUrl": full,
            "resource": resource,
            "request": {"method": method, "url": resource["resourceType"]},
        }
    )
    return full


def patient_id(bundle: dict) -> str:
    for e in bundle.get("entry") or []:
        r = e.get("resource") or {}
        if r.get("resourceType") == "Patient":
            return r.get("id") or "patient"
    return "patient"


def has_text(bundle: dict, words) -> bool:
    blob = json.dumps(bundle).lower()
    return any(w in blob for w in words)


def ensure_smoking(bundle: dict, pid: str):
    if has_text(bundle, ["72166-2", "smoking status", "tobacco smoking status"]):
        return False
    add_entry(
        bundle,
        {
            "resourceType": "Observation",
            "id": uid("smoke"),
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "social-history",
                            "display": "Social History",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "72166-2",
                        "display": "Tobacco smoking status",
                    }
                ],
                "text": "Tobacco smoking status",
            },
            "subject": {"reference": f"Patient/{pid}"},
            "effectiveDateTime": NOW,
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "266919005",
                        "display": "Never smoked tobacco",
                    }
                ],
                "text": "Never smoker",
            },
        },
    )
    return True


def ensure_phq(bundle: dict, pid: str):
    if has_text(bundle, ["44249-1", "phq-9", "patient health questionnaire"]):
        return False
    add_entry(
        bundle,
        {
            "resourceType": "Observation",
            "id": uid("phq"),
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "survey",
                            "display": "Survey",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "44249-1",
                        "display": "PHQ-9 quick depression assessment panel",
                    }
                ],
                "text": "PHQ-9",
            },
            "subject": {"reference": f"Patient/{pid}"},
            "effectiveDateTime": NOW,
            "valueQuantity": {
                "value": 2,
                "unit": "score",
                "system": "http://unitsofmeasure.org",
                "code": "{score}",
            },
        },
    )
    return True


def ensure_procedure(bundle: dict, pid: str, code: str, display: str, words) -> bool:
    if has_text(bundle, words):
        return False
    add_entry(
        bundle,
        {
            "resourceType": "Procedure",
            "id": uid("proc"),
            "status": "completed",
            "code": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": code,
                        "display": display,
                    }
                ],
                "text": display,
            },
            "subject": {"reference": f"Patient/{pid}"},
            "performedDateTime": NOW,
        },
    )
    return True


def ensure_fit(bundle: dict, pid: str) -> bool:
    if has_text(bundle, ["77353-1", "fecal immunochemical", "fit test"]):
        return False
    add_entry(
        bundle,
        {
            "resourceType": "Observation",
            "id": uid("fit"),
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory",
                            "display": "Laboratory",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "77353-1",
                        "display": "Noninvasive colorectal cancer DNA and occult blood screening",
                    }
                ],
                "text": "FIT / stool DNA screening",
            },
            "subject": {"reference": f"Patient/{pid}"},
            "effectiveDateTime": NOW,
            "valueCodeableConcept": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "260385009",
                        "display": "Negative",
                    }
                ],
                "text": "Negative",
            },
        },
    )
    return True


def ensure_a1c(bundle: dict, pid: str) -> bool:
    if has_text(bundle, ["4548-4", "hemoglobin a1c"]):
        return False
    add_entry(
        bundle,
        {
            "resourceType": "Observation",
            "id": uid("a1c"),
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory",
                            "display": "Laboratory",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "4548-4",
                        "display": "Hemoglobin A1c",
                    }
                ],
                "text": "Hemoglobin A1c",
            },
            "subject": {"reference": f"Patient/{pid}"},
            "effectiveDateTime": NOW,
            "valueQuantity": {
                "value": 7.2,
                "unit": "%",
                "system": "http://unitsofmeasure.org",
                "code": "%",
            },
        },
    )
    return True


def ensure_servicerequest(bundle: dict, pid: str, display: str, words) -> bool:
    if has_text(bundle, words):
        return False
    add_entry(
        bundle,
        {
            "resourceType": "ServiceRequest",
            "id": uid("sr"),
            "status": "active",
            "intent": "order",
            "code": {"text": display},
            "subject": {"reference": f"Patient/{pid}"},
            "authoredOn": NOW,
        },
    )
    return True


ENRICHERS = {
    "CMS138v14": lambda b, p: ensure_smoking(b, p),
    "CMS2v15": lambda b, p: ensure_phq(b, p)
    or ensure_servicerequest(b, p, "Depression follow-up referral", ["depression follow", "behavioral health referral"]),
    "CMS130v14": lambda b, p: ensure_procedure(
        b, p, "73761001", "Colonoscopy", ["colonoscopy"]
    )
    or ensure_fit(b, p),
    "CMS125v14": lambda b, p: ensure_procedure(
        b, p, "71651007", "Mammography", ["mammograph", "mammogram"]
    )
    or ensure_servicerequest(b, p, "Screening mammography", ["mammograph"]),
    "CMS131v14": lambda b, p: ensure_procedure(
        b, p, "252416005", "Retinal screening", ["retinal", "eye exam"]
    ),
    "CMS122v14": lambda b, p: ensure_a1c(b, p),
    "CMS68v15": lambda b, p: ensure_servicerequest(
        b, p, "Medication list review documented", ["medication list", "current medication"]
    ),
    "CMS22v14": lambda b, p: ensure_servicerequest(
        b, p, "Blood pressure follow-up", ["blood pressure follow"]
    ),
}


def enrich_one(cms_id: str, src: pathlib.Path, out_dir: pathlib.Path) -> pathlib.Path | None:
    bundle = json.loads(src.read_text())
    if bundle.get("resourceType") != "Bundle":
        return None
    bundle = copy.deepcopy(bundle)
    bundle["type"] = bundle.get("type") or "transaction"
    bundle.setdefault("meta", {})
    bundle["meta"]["tag"] = [
        {
            "system": "https://github.com/glilly/HL7-FHIR-quality-testing",
            "code": f"enriched-{cms_id}",
            "display": f"Overnight enrichment for {cms_id}",
        }
    ]
    pid = patient_id(bundle)
    fn = ENRICHERS.get(cms_id)
    changed = False
    if fn:
        changed = bool(fn(bundle, pid))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{src.stem}.enriched.json"
    out.write_text(json.dumps(bundle, indent=2) + "\n")
    return out if changed or True else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--measures",
        default="CMS122v14,CMS138v14,CMS2v15,CMS130v14,CMS125v14,CMS131v14,CMS68v15,CMS22v14",
    )
    ap.add_argument("--out-root", default="2026/patients/enriched")
    args = ap.parse_args()
    root = pathlib.Path(".")
    manifest_lines = ["bundle_path\n"]
    for cms_id in [m.strip() for m in args.measures.split(",") if m.strip()]:
        showcase = root / f"2026/cohorts/{cms_id}/numer/showcase-1.tsv"
        selected = root / f"2026/cohorts/{cms_id}/numer/selected-18.tsv"
        src_tsv = showcase if showcase.exists() else selected
        if not src_tsv.exists():
            print(f"SKIP {cms_id}: no showcase/selected TSV")
            continue
        lines = src_tsv.read_text().splitlines()[1:]
        if not lines:
            print(f"SKIP {cms_id}: empty cohort")
            continue
        # Enrich first 3 numerator candidates for load/Inferno experiments
        out_dir = pathlib.Path(args.out_root) / cms_id
        for line in lines[:3]:
            src = pathlib.Path(line.split("\t")[0])
            if not src.exists():
                continue
            out = enrich_one(cms_id, src, out_dir)
            if out:
                manifest_lines.append(str(out.resolve()) + "\n")
                print(f"ENRICHED {cms_id} -> {out}")
    man = pathlib.Path(args.out_root) / "overnight-enrich-manifest.tsv"
    man.parent.mkdir(parents=True, exist_ok=True)
    man.write_text("".join(manifest_lines))
    print(f"MANIFEST={man}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
