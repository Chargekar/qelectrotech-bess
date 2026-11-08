"""Validate library contracts, generated assets and resource references. Stdlib only."""
import json
import pathlib
import re
import sys
import uuid
import xml.etree.ElementTree as ET
from build_assets import ROOT, definition, uid
from build_drafting import validate as validate_drafting

def validate(root=ROOT):
    errors=[]
    def require(ok,msg):
        if not ok:errors.append(msg)
    catalog=json.loads((root/'assets/catalog.json').read_text(encoding='utf-8'))
    symbols=catalog['symbols'];seen=set();all_uuids=set()
    for s in symbols:
        key=s['id'];require(key not in seen,f'duplicate symbol: {key}');seen.add(key)
        require(bool(s.get('family')),f'missing family: {key}')
        require(bool(s.get('meaning')),f'missing meaning: {key}')
        if s.get('geometry_family')=='location-preview':
            require(s.get('ports')==[],f'physical preview has electrical ports: {key}')
            require(s.get('drawing_space')=='symbol-preview' and s.get('physical_scale_use')=='preview-only',f'physical preview silently claims scale: {key}')
            resource,sep,block_id=s.get('physical_contract_ref','').partition('#')
            require(sep and (root/resource).is_file(),f'physical preview lacks a geometry contract: {key}')
            if sep and (root/resource).is_file():
                contract=json.loads((root/resource).read_text(encoding='utf-8'))
                require(any(b['id']==block_id and b.get('physical_dimensions_selected') is False for b in contract.get('blocks',[])),f'physical block contract missing or preselects dimensions: {key}')
        if s.get('connection_semantics')=='internal-common-within-declared-domain':
            require(len(s['ports'])>1,f'common bar lacks multiple terminals: {key}')
            require(len({(p['domain'],p.get('representation')) for p in s['ports']})==1,f'common bar silently bridges domains: {key}')
        require(s.get('view_kind') in ('single-line-functional','installation-legend'),f'unknown view contract: {key}')
        if s.get('view_kind')=='installation-legend':
            require(s.get('ports')==[],f'installation annotation has electrical terminals: {key}')
            require(s.get('connection_semantics')=='non-electrical-annotation',f'installation annotation semantics missing: {key}')
            require(bool(s.get('required_project_fields')),f'installation annotation lacks project input contract: {key}')
            for anchor in s.get('annotation_anchors',[]):
                require(-50<=anchor['x']<=50 and -40<=anchor['y']<=40,f'annotation anchor outside bounds: {key}')
        path=root/'assets/library/elements/bess'/(key+'.elmt')
        require(path.exists(),f'missing generated symbol: {key}')
        if not path.exists():continue
        d=ET.parse(path).getroot();expected=definition(s)
        if s.get('geometry_family')=='location-preview':
            require(any(t.get('text')=='NTS' for t in d.findall('description/text')),f'physical preview lacks visible NTS label: {key}')
        require(ET.tostring(d)==ET.tostring(expected) or canonical(d)==canonical(expected),f'stale generated geometry/metadata: {key}')
        native_ports=d.findall('description/terminal');require(len(native_ports)==len(s['ports']),f'port count mismatch: {key}')
        require(len({p['id'] for p in s['ports']})==len(s['ports']),f'duplicate port: {key}')
        for port in s['ports']:
            require(port['domain'] in ('ac','dc','pe','control','sense'),f'unknown domain: {key}.{port["id"]}')
            require(port.get('representation') in ('circuit-bundle','individual-conductor','protective-bond','functional-signal'),f'port representation missing: {key}.{port["id"]}')
            allowed={'ac':('circuit-bundle','individual-conductor'),'dc':('circuit-bundle','individual-conductor'),'pe':('protective-bond',),'control':('functional-signal',),'sense':('functional-signal',)}
            require(port.get('representation') in allowed.get(port['domain'],()),f'domain/representation mismatch: {key}.{port["id"]}')
            if port['id'] in ('positive','negative'):
                require(port['domain']=='dc' and port.get('representation')=='individual-conductor',f'polarity port is not an individual DC conductor: {key}.{port["id"]}')
            require(-50<=port['x']<=50 and -40<=port['y']<=40,f'port outside bounds: {key}')
        for v in [d.find('uuid').get('uuid')]+[n.get('uuid') for n in native_ports]:
            try:uuid.UUID(v.strip('{}'))
            except (ValueError,AttributeError):errors.append(f'invalid UUID: {key}')
            require(v not in all_uuids,f'duplicate native UUID: {key}');all_uuids.add(v)
    schema=json.loads((root/'assets/ontology/domain.schema.json').read_text(encoding='utf-8'))
    glossary=root/'assets/db/glossary_seed.json'
    if glossary.exists():
        mapped={s['id'] for s in json.loads(glossary.read_text(encoding='utf-8'))['symbols']}
        require(seen.issubset(mapped),'catalog assets missing explicit Draw.io mappings/fallbacks: '+', '.join(sorted(seen-mapped)))
    def walk(value):
        if isinstance(value,dict):
            require('state' not in value.get('properties',{}),'ambiguous property state in schema')
            if '$ref' in value:
                r=value['$ref'];require(r.startswith('#/$defs/') and r[8:] in schema['$defs'],f'broken schema reference: {r}')
            for child in value.values():walk(child)
        elif isinstance(value,list):
            for child in value:walk(child)
    walk(schema)
    location_contract=root/'assets/location/geometry-contracts.json'
    if location_contract.exists():
        location=json.loads(location_contract.read_text(encoding='utf-8'))
        require(len({b['id'] for b in location['blocks']})==len(location['blocks']),'duplicate physical preview contract')
        for block in location['blocks']:
            require(block['id'] in seen and block['contract'] in schema['$defs'],f'unknown physical block/definition: {block["id"]}')
    for md in root.rglob('*.md'):
        if '__pycache__' in str(md):continue
        content=md.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)',content):
            if re.match(r'^(https?:|#|mailto:)',target):continue
            require((md.parent/target.split('#')[0]).exists(),f'broken resource link in {md.relative_to(root)}: {target}')
    profiles=json.loads((root/'assets/profiles/index.json').read_text(encoding='utf-8'))
    for profile in profiles['profiles']:require((root/'assets/profiles'/profile['path']).exists(),f'missing jurisdiction profile: {profile["id"]}')
    notes=json.loads((root/'assets/notes/compliance-notes.json').read_text(encoding='utf-8'))
    registered_sources=set(re.findall(r'^\| ([A-Z][A-Z0-9-]+) \|',(root/'references/sources.md').read_text(encoding='utf-8'),re.M))
    def source_links(value,context):
        if isinstance(value,dict):
            for key,child in value.items():
                if key in ('source_id','starting_source_id') and child:
                    require(child in registered_sources,f'unregistered source in {context}: {child}')
                elif key=='source_refs' and isinstance(child,list):
                    for source in child:require(source in registered_sources,f'unregistered source in {context}: {source}')
                else:source_links(child,context)
        elif isinstance(value,list):
            for child in value:source_links(child,context)
    source_links(catalog,'catalog');source_links(notes,'note templates')
    if location_contract.exists():source_links(location,'location geometry contracts')
    applicability_contract=root/'assets/compliance/applicability-contracts.json'
    if applicability_contract.exists():source_links(json.loads(applicability_contract.read_text(encoding='utf-8')),'applicability contracts')
    drafting=root/'assets/drafting/forms.json'
    if drafting.exists():source_links(json.loads(drafting.read_text(encoding='utf-8')),'drafting forms')
    for profile in profiles['profiles']:
        data=json.loads((root/'assets/profiles'/profile['path']).read_text(encoding='utf-8'))
        source_links(data,profile['id'])
        require(data.get('id')==profile['id'],f'profile identity mismatch: {profile["id"]}')
        require(data.get('binding_project_defaults') is False,f'research profile silently binds project defaults: {profile["id"]}')
        if profile['id']!='US-BASE':
            require(data.get('subdivision_code')==profile['id'] and bool(re.fullmatch(r'US-[A-Z]{2}',profile['id'])),f'profile is not a geographic subdivision: {profile["id"]}')
    require(len({n['id'] for n in notes['templates']})==len(notes['templates']),'duplicate compliance-note id')
    for n in notes['templates']:
        require(n['review_status']=='open',f'template claims approval: {n["id"]}')
        require(n.get('applicability_resolution')=='undetermined' and n.get('applicability_decision_ref') is None,f'template preselects project applicability: {n["id"]}')
        require(n.get('requires_project_resolution') is True and bool(n.get('required_context_fields')),f'note lacks project-resolution contract: {n["id"]}')
        require(bool(re.findall(r'\{[^}]+\}',n['template'])),f'non-parameterized note: {n["id"]}')
    gallery=root/'assets/library/asset-gallery.qet'
    if gallery.exists():
        g=ET.parse(gallery).getroot()
        require(len(g.findall('diagram/elements/element'))==len(symbols),'gallery/catalog count mismatch')
        require(len(g.findall('diagram/conductors/conductor'))==0,'asset gallery unexpectedly contains project circuits')
        require(len(g.findall('collection//definition'))==len(symbols),'gallery does not embed all definitions')
    else:errors.append('missing native asset gallery')
    drawing_result=validate_drafting(root)
    errors.extend(drawing_result['errors'])
    return {'symbols':len(symbols),'blank_forms':drawing_result['blank_forms'],'native_titleblocks':drawing_result['native_titleblocks'],
            'note_templates':len(notes['templates']),'schema_definitions':len(schema['$defs']),'errors':errors}

def _num(v):
    # Floats from trig differ in the last digit across platforms (Windows vs Linux libm); compare at 1e-6.
    try:return format(round(float(v),6),'.6f') if any(ch in v for ch in '.eE') else v
    except ValueError:return v

def canonical(e):
    return (e.tag,tuple(sorted((k,_num(v)) for k,v in e.attrib.items())),(e.text or '').strip(),tuple(canonical(c) for c in e))

if __name__=='__main__':
    result=validate();print(json.dumps(result,indent=2));sys.exit(bool(result['errors']))
