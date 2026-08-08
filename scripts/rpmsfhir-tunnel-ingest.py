#!/usr/bin/env python3
"""POST Synthea bundles to rpmsfhir via local SSH tunnel (default http://127.0.0.1:19080)."""
from __future__ import annotations

import argparse
import json
import pathlib
import time
import urllib.error
import urllib.request
from http.client import IncompleteRead


def extract_ids(data: dict) -> tuple[str, str]:
    ien = str(data.get("ien") or data.get("IEN") or "")
    dfn = str(data.get("dfn") or data.get("DFN") or "")
    patient = data.get("patient") if isinstance(data.get("patient"), dict) else {}
    if not dfn:
        dfn = str(patient.get("dfn") or patient.get("DFN") or "")
    if not ien:
        ien = str(patient.get("ien") or patient.get("IEN") or "")
    return ien, dfn


def post(endpoint: str, body: bytes, timeout: int) -> tuple[str, str]:
    req = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/fhir+json",
            "Accept": "application/json",
            "Expect": "",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return str(resp.status), resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return str(exc.code), exc.read().decode("utf-8", errors="replace")
    except IncompleteRead as exc:
        partial = exc.partial.decode("utf-8", errors="replace") if exc.partial else ""
        if partial.strip().startswith("{"):
            return "206", partial
        return "000", json.dumps({"error": f"IncompleteRead: {exc}"})
    except Exception as exc:
        return "000", json.dumps({"error": str(exc)})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--base-url", default="http://127.0.0.1:19080")
    ap.add_argument("--load", default="1")
    ap.add_argument("--out", required=True)
    ap.add_argument("--response-dir", required=True)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--sleep", type=float, default=0.2)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    response_dir = pathlib.Path(args.response_dir)
    response_dir.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        out.write_text("bundle_path\thttp_code\tien\tdfn\tresponse_file\n")

    done: set[str] = set()
    for line in out.read_text().splitlines()[1:]:
        parts = line.split("\t")
        if not parts:
            continue
        code = parts[1] if len(parts) > 1 else ""
        dfn = parts[3] if len(parts) > 3 else ""
        if args.load == "1":
            if dfn:
                done.add(parts[0])
        elif code.startswith("2"):
            done.add(parts[0])

    rows: list[str] = []
    for line in pathlib.Path(args.manifest).read_text().splitlines()[1:]:
        path = line.split("\t", 1)[0]
        if path and path not in done and pathlib.Path(path).is_file():
            rows.append(path)
    if args.limit:
        rows = rows[: args.limit]

    endpoint = args.base_url.rstrip("/") + f"/addpatient?load={args.load}"
    print(f"REMAINING={len(rows)} COMPLETED={len(done)} ENDPOINT={endpoint}", flush=True)

    for idx, path in enumerate(rows, start=1):
        body = pathlib.Path(path).read_bytes()
        t0 = time.time()
        code, text = "000", ""
        ien = dfn = ""
        for attempt in range(args.retries + 1):
            code, text = post(endpoint, body, args.timeout)
            try:
                data = json.loads(text) if text.strip().startswith("{") else {}
                ien, dfn = extract_ids(data)
                if data.get("status") == "ok" and (ien or dfn) and not str(code).startswith("2"):
                    code = "201"
            except Exception:
                ien = dfn = ""
            ok = str(code).startswith("2") and (args.load != "1" or bool(dfn))
            if ok:
                break
            if attempt < args.retries:
                time.sleep(2 * (attempt + 1))

        resp = response_dir / f"tunnel-ingest-{idx}-{int(t0)}.json"
        resp.write_text(text)
        with out.open("a") as handle:
            handle.write(f"{path}\t{code}\t{ien}\t{dfn}\t{resp}\n")
        print(
            f"[{idx}/{len(rows)}] HTTP {code} ien={ien} dfn={dfn} "
            f"{time.time() - t0:.1f}s {pathlib.Path(path).name}",
            flush=True,
        )
        if args.sleep:
            time.sleep(args.sleep)

    print("DONE", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
