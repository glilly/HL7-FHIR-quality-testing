#!/usr/bin/env python3
"""Classify devfhir graph IENs by CQL/DEQM MeasureReport membership."""
from __future__ import annotations
import argparse, json, pathlib, urllib.parse, urllib.request

def pop_count(report: dict, code: str) -> int:
    total = 0
    for group in report.get('group', []):
        for pop in group.get('population', []):
            coding = pop.get('code', {}).get('coding', [])
            codes = {c.get('code') for c in coding}
            if code in codes:
                total += int(pop.get('count') or 0)
    return total

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--measure-server', required=True, help='FHIR base with Measure/$evaluate-measure')
    p.add_argument('--measure', required=True, help='Measure id or canonical URL')
    p.add_argument('--cms-id', required=True)
    p.add_argument('--ingest-manifest', required=True)
    p.add_argument('--period-start', default='2026-01-01')
    p.add_argument('--period-end', default='2026-12-31')
    p.add_argument('--out-root', default='2026/cohorts')
    args = p.parse_args()
    out = pathlib.Path(args.out_root) / args.cms_id
    reports = out / 'reports'
    denom = out / 'denom' / 'patients.tsv'
    numer = out / 'numer' / 'patients.tsv'
    for d in [reports, denom.parent, numer.parent]:
        d.mkdir(parents=True, exist_ok=True)
    denom_rows = ['ien\tdfn\tbundle_path\treport\n']
    numer_rows = ['ien\tdfn\tbundle_path\treport\n']
    lines = pathlib.Path(args.ingest_manifest).read_text().splitlines()[1:]
    for line in lines:
        bundle, http_code, ien, dfn, response = (line.split('\t') + ['','','','',''])[:5]
        if not ien:
            continue
        params = {'periodStart': args.period_start, 'periodEnd': args.period_end, 'subject': f'Patient/{ien}'}
        measure_path = args.measure if args.measure.startswith('http') else f'Measure/{args.measure}'
        url = args.measure_server.rstrip('/') + '/' + measure_path + '/$evaluate-measure?' + urllib.parse.urlencode(params)
        report_file = reports / f'{ien}.json'
        try:
            with urllib.request.urlopen(url, timeout=120) as resp:
                body = resp.read().decode('utf-8')
            report = json.loads(body)
            report_file.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
        except Exception as exc:
            report_file.write_text(json.dumps({'error': str(exc), 'url': url}, indent=2) + '\n')
            continue
        row = f'{ien}\t{dfn}\t{bundle}\t{report_file}\n'
        if pop_count(report, 'denominator') > 0:
            denom_rows.append(row)
        if pop_count(report, 'numerator') > 0:
            numer_rows.append(row)
    denom.write_text(''.join(denom_rows))
    numer.write_text(''.join(numer_rows))
    print(f'DENOM={denom}')
    print(f'NUMER={numer}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
