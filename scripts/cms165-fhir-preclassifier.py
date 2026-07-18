#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, json, pathlib

MEASUREMENT_END = dt.date(2026, 12, 31)
HTN_CODES = {'38341003', '59621000'}
SBP_CODES = {'8480-6'}
DBP_CODES = {'8462-4'}

def parse_date(value: str):
    if not value:
        return None
    try:
        return dt.date.fromisoformat(value[:10])
    except Exception:
        return None

def age_at(birth: str, asof: dt.date) -> int:
    b = parse_date(birth)
    if not b:
        return -1
    return asof.year - b.year - ((asof.month, asof.day) < (b.month, b.day))

def coding_codes(cc):
    codes=[]
    if not isinstance(cc, dict): return codes
    for coding in cc.get('coding', []) or []:
        codes.append((coding.get('system',''), coding.get('code',''), coding.get('display','')))
    return codes

def has_code(cc, wanted):
    return any(code in wanted for _, code, _ in coding_codes(cc))

def text_has(obj, words):
    text=json.dumps(obj).lower()
    return any(w in text for w in words)

def entries(bundle):
    return [e.get('resource', {}) for e in bundle.get('entry', [])]

def patient(resources):
    for r in resources:
        if r.get('resourceType') == 'Patient': return r
    return {}

def obs_day_and_values(obs):
    day=parse_date(obs.get('effectiveDateTime') or obs.get('issued') or '')
    vals=[]
    # Synthea BP commonly has components.
    for comp in obs.get('component', []) or []:
        code=comp.get('code', {})
        val=comp.get('valueQuantity', {})
        if has_code(code, SBP_CODES): vals.append(('sbp', day, val.get('value'), val.get('unit') or val.get('code')))
        if has_code(code, DBP_CODES): vals.append(('dbp', day, val.get('value'), val.get('unit') or val.get('code')))
    val=obs.get('valueQuantity', {})
    if has_code(obs.get('code', {}), SBP_CODES): vals.append(('sbp', day, val.get('value'), val.get('unit') or val.get('code')))
    if has_code(obs.get('code', {}), DBP_CODES): vals.append(('dbp', day, val.get('value'), val.get('unit') or val.get('code')))
    return vals

def classify(path: pathlib.Path):
    bundle=json.loads(path.read_text())
    rs=entries(bundle)
    p=patient(rs)
    age=age_at(p.get('birthDate',''), MEASUREMENT_END)
    has_htn=False
    has_encounter=False
    bps=[]
    for r in rs:
        rt=r.get('resourceType')
        if rt == 'Condition':
            if has_code(r.get('code', {}), HTN_CODES) or text_has(r.get('code', {}), ['hypertension']):
                has_htn=True
        elif rt == 'Encounter':
            status=r.get('status','')
            if status in {'finished','arrived','in-progress','planned',''}:
                has_encounter=True
        elif rt == 'Observation':
            bps.extend(obs_day_and_values(r))
    days={}
    for kind, day, value, unit in bps:
        if day is None or value is None: continue
        try: value=float(value)
        except Exception: continue
        days.setdefault(day, {}).setdefault(kind, []).append(value)
    most_recent=None
    for day in sorted(days):
        if day.year == 2026 and 'sbp' in days[day] and 'dbp' in days[day]:
            most_recent=day
    numerator=False
    sbp=dbp=''
    if most_recent:
        sbp=min(days[most_recent]['sbp'])
        dbp=min(days[most_recent]['dbp'])
        numerator=sbp < 140 and dbp < 90
    denom=(18 <= age <= 85) and has_htn and has_encounter
    return {
        'bundle_path': str(path),
        'patient_id': p.get('id',''),
        'birthDate': p.get('birthDate',''),
        'gender': p.get('gender',''),
        'age': age,
        'denominator': denom,
        'numerator': denom and numerator,
        'has_htn': has_htn,
        'has_encounter': has_encounter,
        'bp_day': str(most_recent or ''),
        'sbp': str(sbp),
        'dbp': str(dbp),
    }

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest', default='2026/patients/devfhir-ingest-load0-success-1000.tsv')
    ap.add_argument('--out-root', default='2026/cohorts/CMS165v14')
    args=ap.parse_args()
    out=pathlib.Path(args.out_root)
    denom=out/'denom'/'cms165-fhir-preclassifier.tsv'
    numer=out/'numer'/'cms165-fhir-preclassifier.tsv'
    reports=out/'reports'/'cms165-fhir-preclassifier-summary.json'
    for p in [denom.parent, numer.parent, reports.parent]: p.mkdir(parents=True, exist_ok=True)
    header=['bundle_path','patient_id','birthDate','gender','age','has_htn','has_encounter','bp_day','sbp','dbp']
    drows=['\t'.join(header)+'\n']
    nrows=['\t'.join(header)+'\n']
    summary={'scanned':0,'denominator':0,'numerator':0}
    for line in pathlib.Path(args.manifest).read_text().splitlines()[1:]:
        parts=line.split('\t')
        if not parts: continue
        path=pathlib.Path(parts[0])
        if not path.exists(): continue
        row=classify(path)
        summary['scanned'] += 1
        values=[str(row[k]) for k in header]
        if row['denominator']:
            summary['denominator'] += 1
            drows.append('\t'.join(values)+'\n')
        if row['numerator']:
            summary['numerator'] += 1
            nrows.append('\t'.join(values)+'\n')
    denom.write_text(''.join(drows))
    numer.write_text(''.join(nrows))
    reports.write_text(json.dumps(summary, indent=2, sort_keys=True)+'\n')
    print('DENOM='+str(denom))
    print('NUMER='+str(numer))
    print('SUMMARY='+str(reports))
    print(summary)
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
