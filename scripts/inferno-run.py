#!/usr/bin/env python3
"""Run hosted Inferno US Quality Core sessions and save result JSON."""
from __future__ import annotations
import argparse, json, pathlib, time, urllib.error, urllib.request

API = 'https://inferno.healthit.gov/suites/api'

def request(method: str, path: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode('utf-8')
    req = urllib.request.Request(API + path, data=data, method=method, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode('utf-8')
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'{method} {path} failed: HTTP {exc.code}: {raw}') from exc
    return json.loads(raw) if raw else {}

def inputs(url: str, patient_ids: str) -> list[dict[str, str]]:
    return [
        {'name': 'url', 'value': url},
        {'name': 'patient_ids', 'value': patient_ids},
        {'name': 'smart_auth_info', 'value': '{}'},
    ]

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--url', required=True, help='FHIR base URL, e.g. https://devfhir.vistaplex.org/altfhir')
    p.add_argument('--patient-ids', required=True, help='Comma-separated patient ids / graph IENs')
    p.add_argument('--title', default='VistA FHIR Quality Testing')
    p.add_argument('--suite', default='us_quality_core_v050-us_quality_core_v050_fhir_api')
    p.add_argument('--test-suite-id', default='us_quality_core_v050')
    p.add_argument('--out', default='2026/scorecards/inferno/latest.json')
    p.add_argument('--poll-seconds', type=int, default=10)
    p.add_argument('--timeout-seconds', type=int, default=1800)
    args = p.parse_args()

    session = request('POST', '/test_sessions', {'test_suite_id': args.test_suite_id, 'title': args.title})
    session_id = session.get('id') or session.get('test_session', {}).get('id')
    if not session_id:
        raise SystemExit(f'Could not determine session id: {session}')

    run = request('POST', '/test_runs', {
        'test_session_id': session_id,
        'test_group_id': args.suite,
        'inputs': inputs(args.url, args.patient_ids)
    })
    run_id = run.get('id') or run.get('test_run', {}).get('id')
    if not run_id:
        raise SystemExit(f'Could not determine run id: {run}')

    deadline = time.time() + args.timeout_seconds
    status = run
    while time.time() < deadline:
        status = request('GET', f'/test_runs/{run_id}')
        state = str(status.get('status') or status.get('state') or '').lower()
        if state in {'done', 'completed', 'complete', 'cancelled', 'canceled', 'errored', 'error'}:
            break
        time.sleep(args.poll_seconds)

    results = request('GET', f'/test_runs/{run_id}/results')
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        'session_id': session_id,
        'run_id': run_id,
        'url': args.url,
        'patient_ids': args.patient_ids,
        'status': status,
        'results': results,
        'session_url': f'https://inferno.healthit.gov/suites/{args.test_suite_id}/{session_id}'
    }, indent=2, sort_keys=True) + '\n')
    print(f'SESSION={session_id}')
    print(f'RUN={run_id}')
    print(f'OUT={out}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
