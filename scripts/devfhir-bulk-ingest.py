#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, threading, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('manifest')
    p.add_argument('--base-url', default='https://devfhir.vistaplex.org')
    p.add_argument('--load', default='0', choices=['0','1'])
    p.add_argument('--out', default='2026/patients/devfhir-ingest.tsv')
    p.add_argument('--response-dir', default='2026/patients/ingest-responses')
    p.add_argument('--workers', type=int, default=8)
    args = p.parse_args()
    manifest = pathlib.Path(args.manifest)
    out = pathlib.Path(args.out)
    response_dir = pathlib.Path(args.response_dir)
    response_dir.mkdir(parents=True, exist_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        out.write_text('bundle_path\thttp_code\tien\tdfn\tresponse_file\n')
    completed = set()
    for line in out.read_text().splitlines()[1:]:
        parts = line.split('\t')
        if len(parts) > 1 and parts[1].startswith('2'):
            completed.add(parts[0])
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
        req = urllib.request.Request(endpoint, data=body, method='POST', headers={'Content-Type':'application/json','Expect':''})
        code = '000'; text = ''; ien = ''; dfn = ''
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                code = str(resp.status); text = resp.read().decode('utf-8', errors='replace')
        except urllib.error.HTTPError as exc:
            code = str(exc.code); text = exc.read().decode('utf-8', errors='replace')
        except Exception as exc:
            text = json.dumps({'error': str(exc)})
        response_file = response_dir / f'ingest-response-{idx}.json'
        response_file.write_text(text)
        try:
            data = json.loads(text)
            ien = str(data.get('ien') or data.get('IEN') or '')
            dfn = str(data.get('dfn') or data.get('DFN') or '')
        except Exception:
            pass
        return path, code, ien, dfn, str(response_file)
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(post, item) for item in enumerate(rows, start=1)]
        for done, future in enumerate(as_completed(futures), start=1):
            path, code, ien, dfn, response_file = future.result()
            with lock:
                with out.open('a') as f:
                    f.write(f'{path}\t{code}\t{ien}\t{dfn}\t{response_file}\n')
            if done % 25 == 0 or not code.startswith('2'):
                print(f'[{done}/{len(rows)}] HTTP {code} ien={ien} {path}')
    print(f'INGEST_MANIFEST={out}')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
