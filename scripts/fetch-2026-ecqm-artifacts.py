#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, urllib.request, zipfile

URL = 'https://ecqi.healthit.gov/sites/default/files/2026-EligibleClinician-eCQM_v2.zip'
SHORTLIST = ['CMS122','CMS125','CMS130','CMS131','CMS138','CMS165','CMS2','CMS22','CMS68']

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--out-dir', default='2026/artifacts')
    args = p.parse_args()
    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    zip_path = out / '2026-EligibleClinician-eCQM_v2.zip'
    if not zip_path.exists():
        req = urllib.request.Request(URL, headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=120) as resp:
            zip_path.write_bytes(resp.read())
    extracted = out / 'extracted-shortlist'
    extracted.mkdir(exist_ok=True)
    summary = []
    with zipfile.ZipFile(zip_path) as outer:
        packages = [n for n in outer.namelist() if n.endswith('-QDM.zip')]
        for name in packages:
            if not any(name.startswith(prefix + '-') for prefix in SHORTLIST):
                continue
            idir = extracted / name.replace('.zip','')
            idir.mkdir(exist_ok=True)
            inner_path = idir / name
            if not inner_path.exists():
                inner_path.write_bytes(outer.read(name))
            with zipfile.ZipFile(inner_path) as inner:
                inner.extractall(idir)
                cql = [n for n in inner.namelist() if n.startswith('cql/') and n.endswith('.cql')]
                measure_cql = [n for n in cql if n.split('/')[-1].startswith(name.split('-')[0])]
                summary.append({'package': name, 'measure_cql': measure_cql, 'all_cql': cql})
    summary_path = out / 'shortlist-summary.json'
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(f'ZIP={zip_path}')
    print(f'EXTRACTED={extracted}')
    print(f'SUMMARY={summary_path}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
