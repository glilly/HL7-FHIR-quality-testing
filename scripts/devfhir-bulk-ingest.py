#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, threading, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.client import IncompleteRead


def _extract_ids(data: dict) -> tuple[str, str]:
    ien = str(data.get('ien') or data.get('IEN') or '')
    dfn = str(data.get('dfn') or data.get('DFN') or '')
    patient = data.get('patient') if isinstance(data.get('patient'), dict) else {}
    if not dfn:
        dfn = str(patient.get('dfn') or patient.get('DFN') or '')
    if not ien:
        ien = str(patient.get('ien') or patient.get('IEN') or '')
    return ien, dfn


def _post_once(endpoint: str, body: bytes, timeout: int) -> tuple[str, str]:
    req = urllib.request.Request(
        endpoint, data=body, method='POST',
        headers={'Content-Type': 'application/json', 'Expect': ''},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return str(resp.status), resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as exc:
        return str(exc.code), exc.read().decode('utf-8', errors='replace')
    except IncompleteRead as exc:
        # Large bundles sometimes truncate the read after a successful create.
        partial = exc.partial.decode('utf-8', errors='replace') if exc.partial else ''
        if partial.strip().startswith('{'):
            return '206', partial
        return '000', json.dumps({'error': f'IncompleteRead: {exc}'})
    except Exception as exc:
        return '000', json.dumps({'error': str(exc)})


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('manifest')
    p.add_argument('--base-url', default='https://devfhir.vistaplex.org')
    p.add_argument('--load', default='0', choices=['0', '1'])
    p.add_argument('--out', default='2026/patients/devfhir-ingest.tsv')
    p.add_argument('--response-dir', default='2026/patients/ingest-responses')
    p.add_argument('--workers', type=int, default=2)
    p.add_argument('--timeout', type=int, default=300)
    p.add_argument('--retries', type=int, default=2)
    args = p.parse_args()
    manifest = pathlib.Path(args.manifest)
    out = pathlib.Path(args.out)
    response_dir = pathlib.Path(args.response_dir)
    response_dir.mkdir(parents=True, exist_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        out.write_text('bundle_path\thttp_code\tien\tdfn\tresponse_file\n')
    # Prefer successful 2xx rows; allow retry of bare 000 with no ien/dfn.
    completed: set[str] = set()
    best: dict[str, list[str]] = {}
    for line in out.read_text().splitlines()[1:]:
        parts = line.split('\t')
        if not parts or not parts[0]:
            continue
        prev = best.get(parts[0])
        code = parts[1] if len(parts) > 1 else ''
        if prev is None or (code.startswith('2') and not prev[1].startswith('2')):
            best[parts[0]] = parts
    for path, parts in best.items():
        code = parts[1] if len(parts) > 1 else ''
        ien = parts[2] if len(parts) > 2 else ''
        dfn = parts[3] if len(parts) > 3 else ''
        if code.startswith('2') or (args.load == '0' and ien) or (args.load == '1' and dfn):
            completed.add(path)
    rows = []
    for line in manifest.read_text().splitlines()[1:]:
        parts = line.split('\t')
        if parts and parts[0] not in completed:
            rows.append(parts[0])
    print(f'REMAINING={len(rows)} COMPLETED={len(completed)}')
    endpoint = args.base_url.rstrip('/') + f'/addpatient?load={args.load}'
    lock = threading.Lock()

    def post(idx_path):
        idx, path = idx_path
        body = pathlib.Path(path).read_bytes()
        code, text = '000', ''
        for attempt in range(args.retries + 1):
            code, text = _post_once(endpoint, body, args.timeout)
            ien = dfn = ''
            try:
                data = json.loads(text)
                ien, dfn = _extract_ids(data)
                if data.get('status') == 'ok' and (ien or dfn) and not code.startswith('2'):
                    code = '201'
            except Exception:
                pass
            if code.startswith('2') or (args.load == '0' and ien) or (args.load == '1' and dfn):
                break
            if attempt < args.retries:
                time.sleep(2 * (attempt + 1))
        response_file = response_dir / f'ingest-response-{idx}.json'
        response_file.write_text(text)
        try:
            data = json.loads(text)
            ien, dfn = _extract_ids(data)
            if data.get('status') == 'ok' and (ien or dfn) and not code.startswith('2'):
                code = '201'
        except Exception:
            ien = dfn = ''
        return path, code, ien, dfn, str(response_file)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(post, item) for item in enumerate(rows, start=1)]
        for done, future in enumerate(as_completed(futures), start=1):
            path, code, ien, dfn, response_file = future.result()
            with lock:
                with out.open('a') as f:
                    f.write(f'{path}\t{code}\t{ien}\t{dfn}\t{response_file}\n')
            if done % 25 == 0 or not code.startswith('2'):
                print(f'[{done}/{len(rows)}] HTTP {code} ien={ien} dfn={dfn} {path}')
    print(f'INGEST_MANIFEST={out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
