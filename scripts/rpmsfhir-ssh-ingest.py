#!/usr/bin/env python3
"""POST Synthea bundles to rpmsfhir via scp + host-local curl to :9080."""
from __future__ import annotations
import argparse, json, pathlib, subprocess, time, uuid

def extract_ids(data: dict) -> tuple[str, str]:
    ien = str(data.get('ien') or data.get('IEN') or '')
    dfn = str(data.get('dfn') or data.get('DFN') or '')
    patient = data.get('patient') if isinstance(data.get('patient'), dict) else {}
    if not dfn:
        dfn = str(patient.get('dfn') or patient.get('DFN') or '')
    if not ien:
        ien = str(patient.get('ien') or patient.get('IEN') or '')
    return ien, dfn

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('manifest')
    ap.add_argument('--host', default='root@rpmsfhir.vistaplex.org')
    ap.add_argument('--load', default='1')
    ap.add_argument('--out', required=True)
    ap.add_argument('--response-dir', required=True)
    ap.add_argument('--timeout', type=int, default=1800)
    ap.add_argument('--sleep', type=float, default=0.25)
    ap.add_argument('--limit', type=int, default=0)
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    response_dir = pathlib.Path(args.response_dir)
    response_dir.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        out.write_text('bundle_path\thttp_code\tien\tdfn\tresponse_file\n')
    done: set[str] = set()
    for line in out.read_text().splitlines()[1:]:
        parts = line.split('\t')
        if not parts:
            continue
        code = parts[1] if len(parts) > 1 else ''
        dfn = parts[3] if len(parts) > 3 else ''
        if code.startswith('2') or dfn:
            done.add(parts[0])
    rows = []
    for line in pathlib.Path(args.manifest).read_text().splitlines()[1:]:
        path = line.split('\t', 1)[0]
        if path and path not in done and pathlib.Path(path).is_file():
            rows.append(path)
    if args.limit:
        rows = rows[: args.limit]
    print(f'REMAINING={len(rows)} COMPLETED={len(done)}', flush=True)
    for idx, path in enumerate(rows, start=1):
        t0 = time.time()
        remote_in = f'/tmp/rpmsfhir-bundle-{uuid.uuid4().hex}.json'
        remote_out = f'/tmp/rpmsfhir-resp-{uuid.uuid4().hex}.json'
        code, text = '000', ''
        try:
            subprocess.run(
                ['scp', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=30', path, f'{args.host}:{remote_in}'],
                check=True, capture_output=True, timeout=600,
            )
            curl = (
                f'code=$(curl -sS -H "Content-Type: application/fhir+json" -H "Accept: application/json" '
                f'-H "Expect:" --data-binary @{remote_in} -o {remote_out} -w "%{{http_code}}" '
                f'--max-time {args.timeout} "http://127.0.0.1:9080/addpatient?load={args.load}"); '
                f'printf "%s" "$code"; rm -f {remote_in}'
            )
            proc = subprocess.run(
                ['ssh', '-o', 'BatchMode=yes', '-o', 'ServerAliveInterval=30',
                 '-o', 'ConnectTimeout=30', args.host, curl],
                capture_output=True, timeout=args.timeout + 120, text=True,
            )
            code = (proc.stdout or '').strip() or '000'
            pull = subprocess.run(
                ['ssh', '-o', 'BatchMode=yes', args.host, f'cat {remote_out}'],
                capture_output=True, timeout=120,
            )
            text = pull.stdout.decode('utf-8', errors='replace') if pull.returncode == 0 else ''
            if pull.returncode != 0 and not text:
                text = json.dumps({'error': pull.stderr.decode('utf-8', errors='replace')})
            subprocess.run(
                ['ssh', '-o', 'BatchMode=yes', args.host, f'rm -f {remote_out}'],
                capture_output=True, timeout=60,
            )
            if not code.isdigit():
                text = json.dumps({'error': proc.stderr or code, 'stdout': proc.stdout})
                code = '000'
        except Exception as exc:
            code, text = '000', json.dumps({'error': str(exc)})
        ien = dfn = ''
        try:
            data = json.loads(text) if text.strip().startswith('{') else {}
            ien, dfn = extract_ids(data)
            if data.get('status') == 'ok' and (ien or dfn) and not str(code).startswith('2'):
                code = '201'
        except Exception:
            pass
        resp = response_dir / f'ssh-ingest-{idx}-{int(t0)}.json'
        resp.write_text(text)
        with out.open('a') as f:
            f.write(f'{path}\t{code}\t{ien}\t{dfn}\t{resp}\n')
        print(f'[{idx}/{len(rows)}] HTTP {code} ien={ien} dfn={dfn} {time.time()-t0:.1f}s {pathlib.Path(path).name}', flush=True)
        if args.sleep:
            time.sleep(args.sleep)
    print('DONE', flush=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
