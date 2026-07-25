#!/usr/bin/env python3
"""Run Inferno US Quality Core sessions (hosted or local) and save result JSON."""
from __future__ import annotations
import argparse, json, pathlib, time, urllib.error, urllib.request

DEFAULT_API = 'https://inferno.healthit.gov/suites/api'
DEFAULT_UI = 'https://inferno.healthit.gov/suites'

def request(api: str, method: str, path: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode('utf-8')
    req = urllib.request.Request(
        api.rstrip('/') + path,
        data=data,
        method=method,
        headers={'Content-Type': 'application/json'},
    )
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
    p.add_argument('--url', required=True, help='FHIR base URL seen by Inferno')
    p.add_argument('--patient-ids', required=True, help='Comma-separated patient ids / graph IENs')
    p.add_argument('--title', default='VistA FHIR Quality Testing')
    p.add_argument('--suite', default='us_quality_core_v050-us_quality_core_v050_fhir_api')
    p.add_argument('--test-suite-id', default='us_quality_core_v050')
    p.add_argument('--api', default=DEFAULT_API, help='Inferno suites API base')
    p.add_argument(
        '--ui-base',
        default=DEFAULT_UI,
        help='Inferno UI base for session_url (no trailing slash)',
    )
    p.add_argument('--out', default='2026/scorecards/inferno/latest.json')
    p.add_argument('--poll-seconds', type=int, default=10)
    p.add_argument('--timeout-seconds', type=int, default=1800)
    args = p.parse_args()

    def log(msg: str) -> None:
        print(msg, flush=True)

    log(f'Creating session via {args.api} …')
    session = request(args.api, 'POST', '/test_sessions', {
        'test_suite_id': args.test_suite_id,
        'title': args.title,
    })
    session_id = session.get('id') or session.get('test_session', {}).get('id')
    if not session_id:
        raise SystemExit(f'Could not determine session id: {session}')
    log(f'SESSION={session_id}')

    log('Starting test run …')
    run = request(args.api, 'POST', '/test_runs', {
        'test_session_id': session_id,
        'test_group_id': args.suite,
        'inputs': inputs(args.url, args.patient_ids),
    })
    run_id = run.get('id') or run.get('test_run', {}).get('id')
    if not run_id:
        raise SystemExit(f'Could not determine run id: {run}')
    log(f'RUN={run_id}')

    deadline = time.time() + args.timeout_seconds
    status = run
    while time.time() < deadline:
        status = request(args.api, 'GET', f'/test_runs/{run_id}')
        state = str(status.get('status') or status.get('state') or '').lower()
        log(f'poll status={state or "?"}')
        if state in {'done', 'completed', 'complete', 'cancelled', 'canceled', 'errored', 'error'}:
            break
        time.sleep(args.poll_seconds)

    results = request(args.api, 'GET', f'/test_runs/{run_id}/results')
    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    ui = args.ui_base.rstrip('/')
    out.write_text(json.dumps({
        'session_id': session_id,
        'run_id': run_id,
        'api': args.api,
        'url': args.url,
        'patient_ids': args.patient_ids,
        'status': status,
        'results': results,
        'session_url': f'{ui}/{args.test_suite_id}/{session_id}',
    }, indent=2, sort_keys=True) + '\n')
    log(f'OUT={out}')
    log(f'SESSION_URL={ui}/{args.test_suite_id}/{session_id}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
