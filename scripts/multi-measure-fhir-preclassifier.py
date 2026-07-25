#!/usr/bin/env python3
"""Heuristic FHIR preclassifiers for September first-wave eCQMs.

Not official CQL. Used to pick Synthea showcase patients for Inferno coverage
and later enrichment / CQL verification.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
from typing import Any, Callable

MEASUREMENT_END = dt.date(2026, 12, 31)

DM_CODES = {"44054006", "73211009", "46635009", "15777000"}
HTN_CODES = {"38341003", "59621000"}
SBP_CODES = {"8480-6"}
DBP_CODES = {"8462-4"}
A1C_CODES = {"4548-4", "17856-6", "17855-8", "4549-2"}
SMOKING_CODES = {"72166-2", "11367-0", "68535-4"}
PHQ_CODES = {"44249-1", "44250-9", "44261-6", "55758-7"}
FIT_CODES = {"77353-1", "77354-9", "58453-2", "29771-3"}
MAMMO_CODES = {"24604-1", "24605-8", "24606-6", "24610-8", "363653007", "71651007"}
COLON_CODES = {"73761001", "444783004", "274025005", "310634005"}
EYE_CODES = {"252416005", "410451007", "274738001", "314971001"}
TOBACCO_COUNSEL_CODES = {"171055003", "225323000", "710081004"}


def parse_date(value: str):
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value[:10])
    except Exception:
        return None


def age_at(birth: str, asof: dt.date) -> int:
    b = parse_date(birth)
    if not b:
        return -1
    return asof.year - b.year - ((asof.month, asof.day) < (b.month, b.day))


def coding_codes(cc):
    codes = []
    if not isinstance(cc, dict):
        return codes
    for coding in cc.get("coding", []) or []:
        codes.append((coding.get("system", ""), coding.get("code", ""), coding.get("display", "")))
    if cc.get("text"):
        codes.append(("", "", cc.get("text")))
    return codes


def has_code(cc, wanted):
    return any(code in wanted for _, code, _ in coding_codes(cc))


def text_blob(obj) -> str:
    # Avoid json.dumps on huge bundles; stringify only the local object.
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj.lower()
    try:
        return json.dumps(obj, separators=(",", ":")).lower()
    except Exception:
        return str(obj).lower()


def text_has(obj, words):
    text = text_blob(obj)
    return any(w in text for w in words)


def bundle_haystack(resources) -> str:
    """One lowercase haystack per bundle for cheap keyword probes."""
    parts = []
    for r in resources:
        rt = r.get("resourceType", "")
        if rt in {
            "Condition",
            "Observation",
            "Procedure",
            "DiagnosticReport",
            "ServiceRequest",
            "MedicationRequest",
            "DocumentReference",
            "CarePlan",
            "Task",
            "Encounter",
        }:
            parts.append(text_blob(r.get("code")))
            parts.append(text_blob(r.get("type")))
            parts.append(text_blob(r.get("category")))
            parts.append(text_blob(r.get("medicationCodeableConcept")))
            parts.append(text_blob(r.get("conclusion")))
            parts.append(str(r.get("description") or ""))
    return " ".join(parts).lower()


def entries(bundle):
    return [e.get("resource", {}) for e in bundle.get("entry", [])]


def patient(resources):
    for r in resources:
        if r.get("resourceType") == "Patient":
            return r
    return {}


def has_encounter(resources) -> bool:
    for r in resources:
        if r.get("resourceType") == "Encounter":
            return True
    return False


def has_condition(resources, codes, words) -> bool:
    for r in resources:
        if r.get("resourceType") != "Condition":
            continue
        code = r.get("code", {})
        if has_code(code, codes) or text_has(code, words):
            return True
    return False


def obs_matches(resources, codes=None, words=None, category=None) -> list[dict]:
    out = []
    for r in resources:
        if r.get("resourceType") != "Observation":
            continue
        if category:
            cats = r.get("category") or []
            cat_ok = any(
                has_code(c, {category}) or text_has(c, [category.lower()])
                for c in cats
            )
            if not cat_ok and not (codes or words):
                continue
        code = r.get("code", {})
        ok = False
        if codes and has_code(code, codes):
            ok = True
        if words and text_has(code, words):
            ok = True
        if ok or (category and codes is None and words is None):
            out.append(r)
    return out


def proc_matches(resources, codes=None, words=None) -> list[dict]:
    out = []
    for r in resources:
        if r.get("resourceType") not in {"Procedure", "DiagnosticReport", "ServiceRequest"}:
            continue
        code = r.get("code", {}) or r.get("type", {})
        if codes and has_code(code, codes):
            out.append(r)
            continue
        if words and (text_has(code, words) or text_has(r.get("text"), words)):
            out.append(r)
    return out


def med_requests(resources) -> list[dict]:
    return [r for r in resources if r.get("resourceType") == "MedicationRequest"]


def base_row(path: pathlib.Path, p: dict, age: int) -> dict[str, Any]:
    return {
        "bundle_path": str(path),
        "patient_id": p.get("id", ""),
        "birthDate": p.get("birthDate", ""),
        "gender": p.get("gender", ""),
        "age": age,
    }


def classify_cms165(path: pathlib.Path, resources, p, age):
    has_htn = has_condition(resources, HTN_CODES, ["hypertension"])
    enc = has_encounter(resources)
    days = {}
    for r in resources:
        if r.get("resourceType") != "Observation":
            continue
        day = parse_date(r.get("effectiveDateTime") or r.get("issued") or "")
        for comp in r.get("component") or []:
            code = comp.get("code", {})
            val = (comp.get("valueQuantity") or {}).get("value")
            if day is None or val is None:
                continue
            try:
                val = float(val)
            except Exception:
                continue
            if has_code(code, SBP_CODES):
                days.setdefault(day, {}).setdefault("sbp", []).append(val)
            if has_code(code, DBP_CODES):
                days.setdefault(day, {}).setdefault("dbp", []).append(val)
    most = None
    for day in sorted(days):
        if day.year == 2026 and "sbp" in days[day] and "dbp" in days[day]:
            most = day
    numer = False
    sbp = dbp = ""
    if most:
        sbp = min(days[most]["sbp"])
        dbp = min(days[most]["dbp"])
        numer = sbp < 140 and dbp < 90
    denom = (18 <= age <= 85) and has_htn and enc
    row = base_row(path, p, age)
    row.update(
        {
            "denominator": denom,
            "numerator": denom and numer,
            "has_htn": has_htn,
            "has_encounter": enc,
            "detail": f"bp={sbp}/{dbp}@{most or ''}",
        }
    )
    return row


def classify_cms122(path, resources, p, age):
    has_dm = has_condition(resources, DM_CODES, ["diabetes"])
    enc = has_encounter(resources)
    a1c = obs_matches(resources, A1C_CODES, ["a1c", "hemoglobin a1"])
    best = None
    for r in a1c:
        day = parse_date(r.get("effectiveDateTime") or r.get("issued") or "")
        val = (r.get("valueQuantity") or {}).get("value")
        if day is None or val is None or day.year != 2026:
            continue
        try:
            val = float(val)
        except Exception:
            continue
        if best is None or day > best[0]:
            best = (day, val)
    # CMS122 poor control: HbA1c > 9. Heuristic numer = has recent A1c (any) for Inferno lab coverage;
    # track poor_control separately for CQL follow-up.
    denom = (18 <= age <= 75) and has_dm and enc
    has_a1c = best is not None
    poor = has_a1c and best[1] > 9
    row = base_row(path, p, age)
    row.update(
        {
            "denominator": denom,
            "numerator": denom and has_a1c,  # evidence present for Inferno/lab path
            "poor_control": poor,
            "has_diabetes": has_dm,
            "has_encounter": enc,
            "detail": f"a1c={best[1] if best else ''}@{best[0] if best else ''}",
        }
    )
    return row


def classify_cms138(path, resources, p, age):
    enc = has_encounter(resources)
    smoke = obs_matches(resources, SMOKING_CODES, ["tobacco", "smoking", "smoke"])
    counsel = proc_matches(resources, TOBACCO_COUNSEL_CODES, ["tobacco", "smoking", "cessation"])
    meds = [
        m
        for m in med_requests(resources)
        if text_has(m.get("medicationCodeableConcept"), ["nicotine", "varenicline", "bupropion", "chantix"])
        or text_has(m.get("medicationReference"), ["nicotine", "varenicline", "bupropion", "chantix"])
    ]
    denom = age >= 18 and enc
    has_status = bool(smoke)
    intervened = bool(counsel or meds)
    # Numerator proxy: screened; if current smoker words present, also want intervention.
    smoker = any(text_has(s, ["current", "smokes", "every day", "some day"]) for s in smoke)
    numer = denom and has_status and ((not smoker) or intervened)
    row = base_row(path, p, age)
    row.update(
        {
            "denominator": denom,
            "numerator": numer,
            "has_smoking_status": has_status,
            "has_intervention": intervened,
            "detail": f"smoke_obs={len(smoke)};counsel={len(counsel)};meds={len(meds)}",
        }
    )
    return row


def classify_cms2(path, resources, p, age):
    enc = has_encounter(resources)
    screens = obs_matches(
        resources,
        PHQ_CODES,
        ["phq", "depression screen", "patient health questionnaire"],
        category=None,
    )
    # also category survey / screening
    for r in resources:
        if r.get("resourceType") != "Observation":
            continue
        if text_has(r.get("category", {}), ["survey", "screening"]) and text_has(
            r.get("code", {}), ["depression", "phq", "mood"]
        ):
            screens.append(r)
    follow = proc_matches(
        resources,
        None,
        ["depression", "follow-up", "follow up", "referral", "behavioral", "psychiatr"],
    )
    careplans = [r for r in resources if r.get("resourceType") in {"CarePlan", "ServiceRequest", "Task"}]
    denom = age >= 12 and enc
    screened = bool(screens)
    positive = any(text_has(s, ["positive", "moderate", "severe"]) for s in screens)
    followed = bool(follow or careplans)
    numer = denom and screened and ((not positive) or followed)
    row = base_row(path, p, age)
    row.update(
        {
            "denominator": denom,
            "numerator": numer,
            "has_screen": screened,
            "detail": f"screens={len(screens)};follow={len(follow)};plans={len(careplans)}",
        }
    )
    return row


def classify_cms130(path, resources, p, age):
    enc = has_encounter(resources)
    colon = proc_matches(resources, COLON_CODES, ["colonoscopy", "sigmoidoscopy", "colorectal"])
    fit = obs_matches(resources, FIT_CODES, ["fit", "fobt", "occult blood", "stool dna", "cologuard"])
    fit += proc_matches(resources, FIT_CODES, ["fit", "fobt", "occult", "stool dna"])
    denom = (45 <= age <= 75) and enc
    numer = denom and bool(colon or fit)
    row = base_row(path, p, age)
    row.update(
        {
            "denominator": denom,
            "numerator": numer,
            "detail": f"colon={len(colon)};fit={len(fit)}",
        }
    )
    return row


def classify_cms125(path, resources, p, age):
    enc = has_encounter(resources)
    female = (p.get("gender") or "").lower() in {"female", "f"}
    mammo = proc_matches(resources, MAMMO_CODES, ["mammograph", "mammogram", "breast imaging"])
    denom = female and (40 <= age <= 74) and enc
    numer = denom and bool(mammo)
    row = base_row(path, p, age)
    row.update(
        {
            "denominator": denom,
            "numerator": numer,
            "detail": f"mammo={len(mammo)}",
        }
    )
    return row


def classify_cms131(path, resources, p, age):
    has_dm = has_condition(resources, DM_CODES, ["diabetes"])
    enc = has_encounter(resources)
    eye = proc_matches(resources, EYE_CODES, ["retinal", "eye exam", "diabetic eye", "ophthalm"])
    eye += obs_matches(resources, None, ["retinal", "eye exam", "diabetic retinopathy"])
    denom = (18 <= age <= 75) and has_dm and enc
    numer = denom and bool(eye)
    row = base_row(path, p, age)
    row.update(
        {
            "denominator": denom,
            "numerator": numer,
            "detail": f"eye={len(eye)}",
        }
    )
    return row


def classify_cms68(path, resources, p, age):
    enc = has_encounter(resources)
    meds = med_requests(resources)
    docs = [
        r
        for r in resources
        if r.get("resourceType") == "DocumentReference"
        and text_has(r, ["medication", "med list", "current medication"])
    ]
    denom = age >= 18 and enc
    numer = denom and (bool(meds) or bool(docs))
    row = base_row(path, p, age)
    row.update(
        {
            "denominator": denom,
            "numerator": numer,
            "detail": f"meds={len(meds)};docs={len(docs)}",
        }
    )
    return row


def classify_cms22(path, resources, p, age):
    # BP screening + follow-up documented
    enc = has_encounter(resources)
    bps = obs_matches(resources, SBP_CODES | DBP_CODES, ["blood pressure"])
    follow = proc_matches(resources, None, ["follow-up", "follow up", "referral"]) + [
        r for r in resources if r.get("resourceType") == "ServiceRequest"
    ]
    denom = age >= 18 and enc
    screened = bool(bps)
    numer = denom and screened  # follow-up optional for proxy
    row = base_row(path, p, age)
    row.update(
        {
            "denominator": denom,
            "numerator": numer and (True if not follow else True),
            "detail": f"bp_obs={len(bps)};follow={len(follow)}",
        }
    )
    # Prefer patients that also have follow-up for showcase ranking
    row["numerator"] = denom and screened
    row["has_followup"] = bool(follow)
    return row


CLASSIFIERS: dict[str, Callable] = {
    "CMS165v14": classify_cms165,
    "CMS122v14": classify_cms122,
    "CMS138v14": classify_cms138,
    "CMS2v15": classify_cms2,
    "CMS130v14": classify_cms130,
    "CMS125v14": classify_cms125,
    "CMS131v14": classify_cms131,
    "CMS68v15": classify_cms68,
    "CMS22v14": classify_cms22,
}


def load_ingest_index(manifest: pathlib.Path) -> dict[str, dict[str, str]]:
    """Map absolute bundle_path -> {ien,dfn}."""
    idx = {}
    if not manifest.exists():
        return idx
    lines = manifest.read_text().splitlines()
    if not lines:
        return idx
    header = lines[0].split("\t")
    for line in lines[1:]:
        parts = line.split("\t")
        row = {header[i]: parts[i] if i < len(parts) else "" for i in range(len(header))}
        bp = row.get("bundle_path", "")
        if bp:
            idx[str(pathlib.Path(bp).resolve())] = {
                "graph_ien": row.get("ien", ""),
                "dfn": row.get("dfn", ""),
            }
            idx[bp] = idx[str(pathlib.Path(bp).resolve())]
    return idx


def write_cohort(cms_id: str, rows: list[dict], out_root: pathlib.Path, ingest_idx: dict):
    out = out_root / cms_id
    denom_p = out / "denom" / "fhir-preclassifier.tsv"
    numer_p = out / "numer" / "fhir-preclassifier.tsv"
    showcase_p = out / "numer" / "showcase-1.tsv"
    selected_p = out / "numer" / "selected-18.tsv"
    reports = out / "reports" / "fhir-preclassifier-summary.json"
    for p in [denom_p.parent, numer_p.parent, reports.parent]:
        p.mkdir(parents=True, exist_ok=True)

    header = [
        "bundle_path",
        "patient_id",
        "birthDate",
        "gender",
        "age",
        "detail",
        "graph_ien",
        "dfn",
    ]
    drows = ["\t".join(header) + "\n"]
    nrows = ["\t".join(header) + "\n"]
    numer_rows = []
    summary = {"cms_id": cms_id, "scanned": 0, "denominator": 0, "numerator": 0}

    for row in rows:
        summary["scanned"] += 1
        path = row["bundle_path"]
        link = ingest_idx.get(path) or ingest_idx.get(str(pathlib.Path(path).resolve())) or {}
        values = [
            path,
            str(row.get("patient_id", "")),
            str(row.get("birthDate", "")),
            str(row.get("gender", "")),
            str(row.get("age", "")),
            str(row.get("detail", "")),
            str(link.get("graph_ien", "")),
            str(link.get("dfn", "")),
        ]
        if row.get("denominator"):
            summary["denominator"] += 1
            drows.append("\t".join(values) + "\n")
        if row.get("numerator"):
            summary["numerator"] += 1
            nrows.append("\t".join(values) + "\n")
            numer_rows.append(values)

    denom_p.write_text("".join(drows))
    numer_p.write_text("".join(nrows))

    # Prefer rows with graph_ien for showcase / selected-18
    numer_rows.sort(key=lambda v: (0 if v[6] else 1, v[0]))
    selected = numer_rows[:18]
    showcase = numer_rows[:1]
    selected_p.write_text("\t".join(header) + "\n" + "".join("\t".join(r) + "\n" for r in selected))
    showcase_p.write_text("\t".join(header) + "\n" + "".join("\t".join(r) + "\n" for r in showcase))
    reports.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="2026/patients/devfhir-ingest-load0-success-1000.tsv")
    ap.add_argument("--out-root", default="2026/cohorts")
    ap.add_argument(
        "--measures",
        default=",".join(CLASSIFIERS.keys()),
        help="Comma-separated CMS ids",
    )
    args = ap.parse_args()
    measures = [m.strip() for m in args.measures.split(",") if m.strip()]
    ingest_idx = load_ingest_index(pathlib.Path(args.manifest))
    # Cache bundles by path
    paths = []
    for line in pathlib.Path(args.manifest).read_text().splitlines()[1:]:
        parts = line.split("\t")
        if not parts:
            continue
        path = pathlib.Path(parts[0])
        if path.exists():
            paths.append(path)

    results_by_measure: dict[str, list[dict]] = {m: [] for m in measures if m in CLASSIFIERS}
    print(f"Scanning {len(paths)} bundles for {list(results_by_measure)}", flush=True)
    for i, path in enumerate(paths, 1):
        try:
            # Large Synthea bundles — avoid re-encoding repeatedly in classifiers.
            bundle = json.loads(path.read_text())
        except Exception as exc:
            print(f"SKIP {path}: {exc}", flush=True)
            continue
        rs = entries(bundle)
        p = patient(rs)
        age = age_at(p.get("birthDate", ""), MEASUREMENT_END)
        for cms_id in list(results_by_measure):
            fn = CLASSIFIERS[cms_id]
            results_by_measure[cms_id].append(fn(path, rs, p, age))
        if i % 50 == 0:
            print(f"... {i}/{len(paths)}", flush=True)

    summaries = []
    out_root = pathlib.Path(args.out_root)
    for cms_id, rows in results_by_measure.items():
        summary = write_cohort(cms_id, rows, out_root, ingest_idx)
        summaries.append(summary)
        print(summary, flush=True)

    rollup = out_root / "OVERNIGHT_PRECLASSIFIER_SUMMARY.json"
    rollup.write_text(json.dumps(summaries, indent=2, sort_keys=True) + "\n")
    print(f"ROLLUP={rollup}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
