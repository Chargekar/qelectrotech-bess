"""Build an embedded native QET asset gallery; no connected project scenario."""
import argparse
import json
import pathlib
import textwrap
import xml.etree.ElementTree as ET
from build_assets import ROOT, definition, sub, uid, xml_write

def annotation(inputs,x,y,value,size=9):
    return sub(inputs,'input',x=x,y=y,rotation=0,text=value,font=f'Arial,{size},-1,5,50,0,0,0,0,0')

def build(output):
    catalog=json.loads((ROOT/'assets/catalog.json').read_text(encoding='utf-8'))
    symbols=catalog['symbols']
    p=ET.Element('project',{'title':'Renewable engineering asset library','version':'0.90'})
    props=sub(p,'properties');sub(props,'property',name='asset_purpose',show=1).text='Unconnected symbol gallery. Not an electrical design.'
    nd=sub(p,'newdiagrams');sub(nd,'border',cols=17,colsize=60,rows=8,rowsize=80,displaycols='false',displayrows='false')
    sub(nd,'inset',title='ASSET LIBRARY - REVIEW',author='qelectrotech-bess',folio='%id/%total',date='null',displayAt='bottom')
    sub(nd,'conductors',type='multi',color='#000000',numsize=8,displaytext=1)
    terminal_id=0
    for page in range((len(symbols)+8)//9):
        d=sub(p,'diagram',title=f'GENERIC SYMBOLS - {page+1}',folio='%id/%total',order=page+1,cols=17,colsize=60,rows=8,rowsize=80,
              displaycols='false',displayrows='false',height=660,displayAt='bottom',date='null',author='qelectrotech-bess',version='0.90')
        elements=sub(d,'elements');inputs=sub(d,'inputs');sub(d,'conductors')
        annotation(inputs,35,25,'ORIGINAL GENERIC ASSET GALLERY | UNCONNECTED | NOT A PROJECT DESIGN',12)
        annotation(inputs,35,48,'CC0-1.0 artwork. Terminal roles/domains are catalog contracts; ratings, mounting and compliance require project evidence.',8)
        for i,s in enumerate(symbols[page*9:page*9+9]):
            x=165+(i%3)*320;y=125+(i//3)*175
            e=sub(elements,'element',x=x,y=y,z=10,orientation=0,type='embed://import/bess/'+s['id']+'.elmt',uuid=uid('gallery/'+s['id']),prefix='',freezeLabel='true')
            terminals=sub(e,'terminals')
            for port in s['ports']:
                sub(terminals,'terminal',id=terminal_id,x=port['x'],y=port['y'],orientation={'n':0,'e':1,'s':2,'w':3}[port['orientation']],name=port['id'])
                terminal_id+=1
            sub(e,'inputs');info=sub(e,'elementInformations')
            sub(info,'elementInformation',name='label',show=1).text=s['id']
            sub(info,'elementInformation',name='comment',show=1).text=s['meaning']
            sub(e,'dynamic_texts');sub(e,'texts_groups')
            annotation(inputs,x-120,y+43,s['id'],10)
            annotation(inputs,x-120,y+62,'Family: '+s.get('family','unclassified'),8)
            ports='Ports: '+', '.join(v['id']+' / '+v['domain'] for v in s['ports']) if s['ports'] else 'No electrical terminals; graphic only.'
            for n,chunk in enumerate(textwrap.wrap(ports,width=49)):
                annotation(inputs,x-120,y+80+n*13,chunk,8)
    collection=sub(p,'collection');imp=sub(collection,'category',name='import');ns=sub(imp,'names');sub(ns,'name',lang='en').text='Imported elements'
    cat=sub(imp,'category',name='bess');ns=sub(cat,'names');sub(ns,'name',lang='en').text='Original renewable engineering assets'
    for s in symbols:sub(cat,'element',name=s['id']+'.elmt').append(definition(s))
    output.mkdir(parents=True,exist_ok=True)
    path=output/'asset-gallery.qet';xml_write(p,path)
    print(f'Created {path}: {len(symbols)} elements, {(len(symbols)+8)//9} sheets, zero project conductors.')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=pathlib.Path,default=ROOT/'assets/library');a=p.parse_args();build(a.output)
