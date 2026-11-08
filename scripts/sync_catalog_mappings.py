"""Declare explicit basic-block fallbacks for QET assets without Draw.io mappings.

Default is read-only. --write appends missing entries; existing mappings are preserved.
No stencil name, exact artwork conversion, project scenario or calculation is invented.
"""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def sync(write=False):
    path=ROOT/'assets/db/glossary_seed.json'
    if not path.exists():return []
    data=json.loads(path.read_text(encoding='utf-8'))
    catalog=json.loads((ROOT/'assets/catalog.json').read_text(encoding='utf-8'))
    known={s['id'] for s in data['symbols']};missing=[s for s in catalog['symbols'] if s['id'] not in known]
    if write and missing:
        for s in missing:
            data['symbols'].append({'id':s['id'],'qet':'bess/'+s['id']+'.elmt','kind':'basic','style':'shape=rectangle;rounded=0;whiteSpace=wrap;html=1;fontSize=9;','w':80,'h':40,'note':'Explicit generic labelled rectangle fallback only; original native QET geometry has not been converted to a verified Draw.io stencil. '+s['meaning']})
        path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    return [s['id'] for s in missing]

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--write',action='store_true');a=p.parse_args();missing=sync(a.write)
    print(json.dumps({'action':'appended basic fallbacks' if a.write else 'read-only missing mapping report','count':len(missing),'assets':missing},indent=2))
