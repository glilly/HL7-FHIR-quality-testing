#!/usr/bin/env python3
"""Apply controlled, measure-specific Synthea bundle enrichments."""
from __future__ import annotations
import argparse, json, pathlib

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--cms-id', required=True)
    p.add_argument('--patients-tsv', required=True, help='Denominator patient TSV')
    p.add_argument('--limit', type=int, default=18)
    p.add_argument('--out-root', default='2026/patients/enriched')
    args = p.parse_args()
    out = pathlib.Path(args.out_root) / args.cms_id
    out.mkdir(parents=True, exist_ok=True)
    manifest = out / 'enrichment-manifest.tsv'
    rows = ['source_bundle\tenriched_bundle\tstatus\tnote\n']
    count = 0
    for line in pathlib.Path(args.patients_tsv).read_text().splitlines()[1:]:
        if count >= args.limit:
            break
        parts = line.split('\t')
        if len(parts) < 3:
            continue
        src = pathlib.Path(parts[2])
        if not src.exists():
            continue
        dst = out / src.name
        data = json.loads(src.read_text())
        data.setdefault('meta', {})
        data['meta'].setdefault('tag', []).append({
            'system': 'https://github.com/glilly/HL7-FHIR-quality-testing',
            'code': f'{args.cms_id}-enrichment-candidate',
            'display': 'Selected for CMS eCQM numerator enrichment'
        })
        dst.write_text(json.dumps(data, indent=2) + '\n')
        rows.append(f'{src}\t{dst}\tneeds-measure-specific-patch\tExact numerator patch pending official value-set extraction\n')
        count += 1
    manifest.write_text(''.join(rows))
    print(f'ENRICHMENT_MANIFEST={manifest}')
    print(f'COUNT={count}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
