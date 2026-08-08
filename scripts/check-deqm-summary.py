#!/usr/bin/env python3
"""Structural gate for DEQM Summary MeasureReport prototypes.

Does not replace full FHIR Validator + DEQM package validation (Phase 2).
Exits non-zero on missing Must-Have fields for Connectathon dry-runs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROFILE = (
    "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/summary-measurereport-deqm"
)
SCORING_EXT = (
    "http://hl7.org/fhir/us/davinci-deqm/StructureDefinition/extension-measureScoring"
)
NEEDED_POPS = {
    "initial-population",
    "denominator",
    "numerator",
    "denominator-exclusion",
}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if len(sys.argv) < 2:
        fail("usage: check-deqm-summary.py <MeasureReport.json>")
    path = Path(sys.argv[1])
    rep = json.loads(path.read_text())
    if rep.get("resourceType") != "MeasureReport":
        fail("resourceType != MeasureReport")
    profiles = (rep.get("meta") or {}).get("profile") or []
    if PROFILE not in profiles:
        fail(f"missing meta.profile {PROFILE}")
    if rep.get("status") != "complete":
        fail("status != complete")
    if rep.get("type") != "summary":
        fail("type != summary")
    if not rep.get("measure"):
        fail("missing measure")
    if not (rep.get("reporter") or {}).get("reference"):
        fail("missing reporter.reference")
    period = rep.get("period") or {}
    if not period.get("start") or not period.get("end"):
        fail("missing period.start/end")
    exts = rep.get("extension") or []
    if not any(e.get("url") == SCORING_EXT for e in exts):
        fail("missing extension-measureScoring")
    if not rep.get("improvementNotation"):
        fail("missing improvementNotation")
    groups = rep.get("group") or []
    if not groups:
        fail("missing group")
    pops = {
        (((p.get("code") or {}).get("coding") or [{}])[0].get("code")): p.get("count")
        for p in groups[0].get("population") or []
    }
    missing = NEEDED_POPS - set(pops)
    if missing:
        fail(f"missing populations: {sorted(missing)}")
    for code, count in pops.items():
        if not isinstance(count, int):
            fail(f"population {code} count not int")
    score = (groups[0].get("measureScore") or {}).get("value")
    if score is None:
        fail("missing group.measureScore.value")
    denom = pops["denominator"]
    numer = pops["numerator"]
    expected = (float(numer) / float(denom)) if denom else 0.0
    if abs(float(score) - expected) > 1e-6:
        fail(f"measureScore {score} != numer/denom {expected}")
    print(
        f"OK {path.name}: IPP={pops['initial-population']} "
        f"DENOM={denom} NUMER={numer} DENEX={pops['denominator-exclusion']} "
        f"score={score}"
    )
    print("NOTE: structural gate only — run FHIR Validator + DEQM package next.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
