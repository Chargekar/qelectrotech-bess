"""Build original blank QET schedule forms, header-only CSVs and a native title block."""
import argparse
import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from build_assets import ROOT,sub,uid,rect,line,text,xml_write
from build_gallery import annotation

ASSET=ROOT/'assets/drafting'

def load(root=ROOT):return json.loads((root/'assets/drafting/forms.json').read_text(encoding='utf-8'))

def form_definition(form):
    width=sum(c['width'] for c in form['columns'])
    title_h,header_h,row_h=form['title_height'],form['header_height'],form['row_height']
    height=title_h+header_h+form['blank_rows']*row_h
    r=ET.Element('definition',{'type':'element','version':'0.80','width':str(width),'height':str(height),
        'hotspot_x':'0','hotspot_y':'0','orientation':'dyyy','link_type':'simple'})
    sub(r,'uuid',uuid=uid('draft-form/'+form['id']))
    names=sub(r,'names');sub(names,'name',lang='en').text='Blank '+form['title'].lower()
    sub(r,'informations').text='Original CC0-1.0 blank drafting form. No project rows, ratings, calculations or approval. No electrical terminals.'
    d=sub(r,'description');rect(d,0,0,width,height)
    text(d,12,22,form['title'],11);line(d,0,title_h,width,title_h)
    for row in range(form['blank_rows']+1):
        y=title_h+header_h+row*row_h
        if y<height:line(d,0,y,width,y)
    x=0
    for col in form['columns']:
        if x:line(d,x,title_h,x,height)
        text(d,x+8,title_h+20,col['label'],8)
        x+=col['width']
    return r

def titleblock_definition(name):
    r=ET.Element('titleblocktemplate',{'name':name})
    sub(r,'information').text='Original CC0-1.0 review title block. Blank professional area; no generated seal, signature or identity.'
    sub(r,'logos');g=sub(r,'grid',cols='t16%;t16%;r100%;t16%;t16%;t18%;',rows='24;28;24;24;')
    def field(row,col,name,label,value,colspan=1,rowspan=1,size=8):
        # Native span attributes count additional cells, rather than total cells.
        f=sub(g,'field',row=row,col=col,name=name,colspan=colspan-1,rowspan=rowspan-1,
              align='left',valign='center',displaylabel='true' if label else 'false',hadjust='true',fontsize=size)
        v=sub(f,'value');sub(v,'translation',lang='en').text=value
        l=sub(f,'label');sub(l,'translation',lang='en').text=label
    field(0,0,'review_status','','PRELIMINARY / NOT FOR CONSTRUCTION',5,size=9)
    field(0,5,'blank_professional_area','','',rowspan=4)
    field(1,0,'project','Project','%{project_id}',2)
    field(1,2,'title','Sheet title','%{title}',3,size=10)
    for col,name,label,value in [(0,'folio','Sheet','%{folio}'),(1,'revision','Rev','%{indexrev}'),
            (2,'scale','Scale','%{drawing_scale}'),(3,'author','Drawn','%{author}'),(4,'checker','Checked','%{checked_by}')]:
        field(2,col,name,label,value)
    field(3,0,'site','Site','%{site_id}',2)
    field(3,2,'date','Date','%{date}')
    field(3,3,'basis','Basis','%{basis_ref}',2)
    return r

def gallery_definition(data):
    name=data['titleblock_name']
    p=ET.Element('project',{'title':'Original blank drawing forms - asset review','version':'0.90',
        'uuid':uid('blank-forms-gallery')})
    tb=sub(p,'titleblocktemplates');tb.append(titleblock_definition(name))
    props=sub(p,'properties');sub(props,'property',name='asset_purpose',show=1).text='Blank forms only; no equipment, project scenario or calculation.'
    nd=sub(p,'newdiagrams');sub(nd,'border',cols=17,colsize=60,rows=8,rowsize=80,displaycols='false',displayrows='false')
    for i,form in enumerate(data['forms']):
        d=sub(p,'diagram',title='BLANK '+form['title'],folio='%id/%total',order=i+1,cols=17,colsize=60,
            rows=8,rowsize=80,displaycols='false',displayrows='false',height=660,displayAt='bottom',
            date='null',author='',indexrev='',titleblocktemplate=name,titleblocktemplateCollection='embedded',version='0.90')
        properties=sub(d,'properties')
        for key in data['titleblock_custom_keys']:sub(properties,'property',name=key,show=1).text=''
        elements=sub(d,'elements');e=sub(elements,'element',x=50,y=150,z=10,orientation=0,
            type='embed://import/drawing_forms/'+form['id']+'.elmt',uuid=uid('form-gallery/'+form['id']),prefix='',freezeLabel='true')
        sub(e,'terminals');sub(e,'inputs');sub(e,'elementInformations');sub(e,'dynamic_texts');sub(e,'texts_groups')
        inputs=sub(d,'inputs');sub(d,'conductors')
        annotation(inputs,40,25,'ORIGINAL BLANK DRAWING FORMS | ASSET REVIEW | NO PROJECT DATA',12)
        annotation(inputs,40,52,'Header-only schedules; all data rows are intentionally blank. Native title block has an empty professional area.',9)
        annotation(inputs,50,430,'Populate only from an authorized project model; reconcile identities, units, evidence revisions and review before issue.',9)
        annotation(inputs,50,456,'Form outlines are drawing units. Actual sheet size, print scale, legibility and receiving-agency requirements must be checked.',9)
    collection=sub(p,'collection');imp=sub(collection,'category',name='import');ns=sub(imp,'names');sub(ns,'name',lang='en').text='Imported original forms'
    cat=sub(imp,'category',name='drawing_forms');ns=sub(cat,'names');sub(ns,'name',lang='en').text='Original blank drawing forms'
    for form in data['forms']:sub(cat,'element',name=form['id']+'.elmt').append(form_definition(form))
    return p

def build(root=ROOT):
    data=load(root);target=root/'assets/drafting'
    for form in data['forms']:
        xml_write(form_definition(form),target/'elements'/f"{form['id']}.elmt")
        path=target/'csv'/f"{form['id']}.csv";path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('w',encoding='utf-8',newline='') as stream:
            csv.writer(stream).writerow([c['key'] for c in form['columns']])
    directory=ET.Element('qet-directory');names=sub(directory,'names');sub(names,'name',lang='en').text='Original blank drawing forms'
    xml_write(directory,target/'elements/qet_directory')
    xml_write(titleblock_definition(data['titleblock_name']),target/'titleblocks'/f"{data['titleblock_name']}.titleblock")
    xml_write(gallery_definition(data),target/'blank-forms.qet')
    print(f"Built {len(data['forms'])} blank native forms, {len(data['forms'])} header-only CSVs, one native title block and a blank-forms gallery.")

def canonical(e):return (e.tag,tuple(sorted(e.attrib.items())),(e.text or '').strip(),tuple(canonical(c) for c in e))

def validate(root=ROOT):
    errors=[];data=load(root);target=root/'assets/drafting'
    def require(ok,message):
        if not ok:errors.append(message)
    require(len({f['id'] for f in data['forms']})==len(data['forms']),'duplicate drafting form id')
    for f in data['forms']:
        require(f['row_records']==[],'blank form preselects project rows: '+f['id'])
        require(len({c['key'] for c in f['columns']})==len(f['columns']),'duplicate schedule column: '+f['id'])
        path=target/'elements'/f"{f['id']}.elmt"
        r=ET.parse(path).getroot()
        require(canonical(r)==canonical(form_definition(f)),'stale native blank form: '+f['id'])
        require(not r.findall('description/terminal'),'blank form has electrical terminals: '+f['id'])
        with (target/'csv'/f"{f['id']}.csv").open(encoding='utf-8',newline='') as stream:rows=list(csv.reader(stream))
        require(rows==[[c['key'] for c in f['columns']]],'CSV contains non-header project data or wrong columns: '+f['id'])
    name=data['titleblock_name'];tb=ET.parse(target/'titleblocks'/f'{name}.titleblock').getroot()
    require(canonical(tb)==canonical(titleblock_definition(name)),'stale native title block')
    professional=tb.find("grid/field[@name='blank_professional_area']")
    require(professional is not None and all(not (t.text or '').strip() for t in professional.findall('.//translation')),'professional title-block area is not blank')
    require(not list(tb.find('logos')),'generated title block contains a logo/seal image')
    occupied=set();grid=tb.find('grid')
    row_count=len([x for x in grid.get('rows').split(';') if x]);col_count=len([x for x in grid.get('cols').split(';') if x])
    for cell in grid:
        row,col=int(cell.get('row')),int(cell.get('col'))
        rows,cols=int(cell.get('rowspan','0'))+1,int(cell.get('colspan','0'))+1
        require(row>=0 and col>=0 and row+rows<=row_count and col+cols<=col_count,'title-block span outside grid: '+cell.get('name',''))
        for rr in range(row,row+rows):
            for cc in range(col,col+cols):
                require((rr,cc) not in occupied,'overlapping title-block cells: '+cell.get('name',''))
                occupied.add((rr,cc))
    require(len(occupied)==row_count*col_count,'title-block grid has unaccounted cells')
    gallery=ET.parse(target/'blank-forms.qet').getroot()
    require(canonical(gallery)==canonical(gallery_definition(data)),'stale blank-forms gallery')
    require(not gallery.findall('diagram/conductors/conductor'),'blank-forms gallery contains electrical circuits')
    require(len(gallery.findall('diagram/elements/element'))==len(data['forms']),'blank gallery form count mismatch')
    return {'blank_forms':len(data['forms']),'native_titleblocks':1,'errors':errors}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--validate',action='store_true');a=ap.parse_args()
    if a.validate:
        result=validate();print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
    build()
