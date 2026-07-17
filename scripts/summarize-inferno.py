#!/usr/bin/env python3
from __future__ import annotations
import argparse, collections, json, pathlib

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('scorecard')
    p.add_argument('--out')
    args = p.parse_args()
    data = json.loads(pathlib.Path(args.scorecard).read_text())
    results = data.get('results', [])
    counts = collections.Counter(r.get('result', 'unknown') for r in results)
    lines = [f"# Inferno Scorecard Summary\n", "\n"]
    lines.append(f"- Session: `{data.get('session_id','')}`\n")
    lines.append(f"- Run: `{data.get('run_id','')}`\n")
    lines.append(f"- URL: `{data.get('url','')}`\n")
    lines.append(f"- Patient IDs: `{data.get('patient_ids','')}`\n")
    if data.get('session_url'):
        lines.append(f"- Session URL: {data['session_url']}\n")
    lines.append("\n## Result Counts\n\n")
    for key in ['pass','fail','error','skip','omit','wait','cancel','unknown']:
        if counts.get(key):
            lines.append(f"- {key}: {counts[key]}\n")
    lines.append("\n## Non-Passing Results\n\n")
    for r in results:
        if r.get('result') == 'pass':
            continue
        title = r.get('title') or r.get('test_id') or r.get('test_group_id') or r.get('id')
        msg = (r.get('result_message') or '').replace('\n', ' ')
        lines.append(f"- `{r.get('result','unknown')}` {title}: {msg}\n")
    out = pathlib.Path(args.out) if args.out else pathlib.Path(args.scorecard).with_suffix('.md')
    out.write_text(''.join(lines))
    print(f'SUMMARY={out}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
