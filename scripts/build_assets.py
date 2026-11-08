"""Create original generic QET elements and a contact sheet. Python stdlib only."""
import argparse
import json
import math
import pathlib
import uuid
import textwrap
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
NS = uuid.UUID('6759e540-7c67-46da-885e-43115e8d68dd')
STYLE = 'line-style:normal;line-weight:normal;filling:none;color:black'

def uid(key):
    return '{' + str(uuid.uuid5(NS, key)) + '}'

def sub(parent, tag, **attrs):
    return ET.SubElement(parent, tag, {k: str(v) for k, v in attrs.items()})

def line(d, x1, y1, x2, y2, **attrs):
    return sub(d, 'line', x1=x1, y1=y1, x2=x2, y2=y2, style=STYLE,
               end1='none', end2='none', length1=1.5, length2=1.5, antialias='true', **attrs)

def rect(d, x, y, w, h):
    return sub(d, 'rect', x=x, y=y, width=w, height=h, style=STYLE, antialias='true')

def circle(d, x, y, radius):
    return sub(d, 'ellipse', x=x-radius, y=y-radius, width=radius*2, height=radius*2, style=STYLE, antialias='true')

def text(d, x, y, value, size=9):
    return sub(d, 'text', x=x, y=y, text=value, size=size, rotation=0,
               color='black', font='Arial', style='font-weight:normal;font-style:normal')

def path_lines(d,points):
    for start,end in zip(points,points[1:]):line(d,*start,*end)

def port_stub(d,p,half_width=25,half_height=20):
    x,y=p['x'],p['y']
    ex,ey=(half_width if x>0 else -half_width,y) if abs(x)>abs(y) else (x,half_height if y>0 else -half_height)
    if p['domain'] in ('control','sense'):
        for start,end in ((0,.28),(.48,.72),(.9,1)):
            line(d,x+(ex-x)*start,y+(ey-y)*start,x+(ex-x)*end,y+(ey-y)*end)
    else:line(d,x,y,ex,ey)

def interface_geometry(d,symbol):
    """Original functional interfaces, with dashed logical signals and solid power."""
    k=symbol['id']
    if k=='ac_fuse':
        line(d,-40,0,-20,0);rect(d,-20,-7,40,14);line(d,-20,0,20,0);line(d,20,0,40,0)
    elif k=='ac_fused_disconnect':
        line(d,-40,0,-22,0);line(d,-22,0,-8,-12);line(d,-8,0,-2,0)
        rect(d,-2,-6,18,12);line(d,-2,0,16,0);line(d,16,0,40,0)
    elif k=='remote_operated_breaker':
        line(d,-40,0,-12,0);line(d,12,0,40,0);line(d,-12,0,10,-15);rect(d,-4,-5,8,10)
        rect(d,-6,16,12,10)
        for a,b in ((6,10),(13,16),(26,28),(29,30)):line(d,0,a,0,b)
    elif k=='control_power_supply':
        rect(d,-25,-20,50,40);line(d,-25,20,25,-20);text(d,-20,-5,'AC',7);text(d,5,14,'DC',7)
        for p in symbol['ports']:port_stub(d,p)
    elif k in ('voltage_sensor','power_meter'):
        circle(d,0,0,20);text(d,-6 if k=='voltage_sensor' else -14,4,'V' if k=='voltage_sensor' else 'PWR',9)
        for p in symbol['ports']:port_stub(d,p,20,20)
    else:
        rect(d,-25,-20,50,40)
        glyph=symbol['glyph'];text(d,-len(glyph)*2.6,4,glyph,8)
        for p in symbol['ports']:port_stub(d,p)

def grounding_transfer_geometry(d,symbol):
    """Original grounding, generator and transfer functional artwork."""
    k=symbol['id']
    if k in ('ground_bar','neutral_bar'):
        rect(d,-25,-7,50,14)
        for x in (-17,0,17):circle(d,x,0,2)
        text(d,-7 if k=='ground_bar' else -3,-12,'GB' if k=='ground_bar' else 'N',7)
        for p in symbol['ports']:port_stub(d,p,25,7)
    elif k=='ground_rod':
        line(d,0,-30,0,23);rect(d,-3,-4,6,27);line(d,-20,0,-5,0);line(d,5,0,20,0)
        for x in (-19,-8,7,18):line(d,x,3,x-4,8)
        text(d,8,22,'ROD',6)
    elif k in ('main_bonding_jumper','system_bonding_jumper','equipment_bonding_jumper'):
        line(d,-40,0,-20,0);path_lines(d,[(-20,0),(-13,-9),(13,-9),(20,0)]);line(d,20,0,40,0)
        circle(d,-20,0,2);circle(d,20,0,2);text(d,-12,16,symbol['glyph'],7)
    elif k=='ground_test_link':
        line(d,-40,0,-13,0);line(d,13,0,40,0);rect(d,-13,-4,26,8)
        circle(d,-8,0,2);circle(d,8,0,2);text(d,-13,-12,'TEST',6)
    elif k in ('terminal_block_ac','terminal_block_dc'):
        rect(d,-15,-14,30,28);circle(d,0,0,6);line(d,-40,0,-6,0);line(d,6,0,40,0)
        text(d,-7,-20,'AC' if k=='terminal_block_ac' else 'DC',7)
    elif k=='ct_test_block':
        rect(d,-25,-25,50,50);text(d,-17,4,'CT-TB',7)
        for p in symbol['ports']:port_stub(d,p,25,25)
        for x in (-20,20):
            for y in (-15,15):circle(d,x,y,2)
    elif k=='generator_set':
        circle(d,0,0,20);text(d,-7,5,'G',12)
        for p in symbol['ports']:port_stub(d,p,20,20)
    elif k=='generator_battery_charger':
        rect(d,-25,-20,50,40);line(d,-25,20,25,-20)
        text(d,-20,-5,'AC',7);text(d,5,14,'DC',7);text(d,-10,-25,'CHG',6)
        for p in symbol['ports']:port_stub(d,p)
    elif k=='generator_start_battery':
        rect(d,-25,-20,50,40);line(d,-10,-12,-10,12);line(d,0,-7,0,7)
        text(d,5,4,'ST',7)
        for p in symbol['ports']:port_stub(d,p)
    else:
        rect(d,-25,-20,50,40);glyph=symbol['glyph'];text(d,-len(glyph)*2.6,4,glyph,8)
        for p in symbol['ports']:port_stub(d,p)

def dashed_outline(d,x,y,w,h,dash=8,gap=4):
    for a,b in (((x,y),(x+w,y)),((x+w,y),(x+w,y+h)),((x+w,y+h),(x,y+h)),((x,y+h),(x,y))):
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        for start in range(0,math.ceil(length),dash+gap):
            end=min(start+dash,length)
            line(d,a[0]+dx*start/length,a[1]+dy*start/length,a[0]+dx*end/length,a[1]+dy*end/length)

def swing_arc(d,cx,cy,radius,start,end):
    points=[(cx+radius*math.cos(start+(end-start)*i/12),cy+radius*math.sin(start+(end-start)*i/12)) for i in range(13)]
    path_lines(d,points)

def location_geometry(d,symbol):
    """NTS previews only: local glyph coordinates never supply physical dimensions."""
    k=symbol['geometry_kind']
    if k=='cabinet_plan':
        rect(d,-25,-20,50,40);line(d,-25,15,25,15);line(d,-3,15,-3,20);line(d,3,15,3,20)
        text(d,-13,3,'BESS',7)
    elif k=='container_plan':
        rect(d,-35,-18,70,36)
        for x in (-27,-18,-9,0,9,18,27):line(d,x,-18,x,-11)
        line(d,-35,12,35,12);text(d,-10,4,'ESS',7)
    elif k=='inverter_plan':
        line(d,-35,-22,35,-22);line(d,-35,-18,35,-18)
        line(d,-12,-18,-12,-12);line(d,12,-18,12,-12);rect(d,-21,-12,42,30);text(d,-10,7,'INV',8)
    elif k=='pv_roof':
        rect(d,-34,-23,68,46);line(d,-34,-23,0,-7);line(d,34,-23,0,-7)
        rect(d,-23,-3,46,20)
        for x in (-11,0,11):line(d,x,-3,x,17)
        line(d,-23,7,23,7)
    elif k=='pv_ground':
        for y in (-20,5):
            rect(d,-30,y,60,15)
            for x in (-15,0,15):line(d,x,y,x,y+15)
        line(d,-25,20,-25,26);line(d,25,20,25,26)
    elif k=='pad':
        rect(d,-33,-23,66,46);rect(d,-23,-13,46,26)
        for x in (-31,-19,-7,5,17):line(d,x,20,x+8,13)
    elif k=='wall_section':
        line(d,-28,-26,-28,25);line(d,-18,-26,-18,25)
        for y in (-20,-8,4,16):line(d,-28,y,-18,y-8)
        for y in (-12,12):line(d,-18,y,-5,y)
        rect(d,-5,-20,30,40)
    elif k=='roof_section':
        line(d,-35,20,35,0);line(d,-35,25,35,5)
        line(d,-25,17,-25,-2);line(d,22,4,22,-15)
        path_lines(d,[(-31,0),(28,-18),(30,-12),(-29,6),(-31,0)])
    elif k=='rack_elevation':
        for x in (-26,26):line(d,x,-25,x,25)
        for y in (-21,-3,15):rect(d,-21,y,42,12)
        line(d,-34,25,34,25)
    elif k=='anchor_reference':
        circle(d,0,0,10);line(d,-17,0,17,0);line(d,0,-17,0,17)
        path_lines(d,[(8,-8),(25,-25),(36,-25)]);text(d,-9,27,'REF',6)
    elif k in ('electrical_envelope','service_envelope','fire_envelope'):
        dashed_outline(d,-34,-23,68,46,8 if k=='electrical_envelope' else 4,4)
        if k=='fire_envelope':dashed_outline(d,-29,-18,58,36,4,4)
        text(d,-14 if k!='service_envelope' else -10,4,{'electrical_envelope':'ELEC','service_envelope':'SVC','fire_envelope':'FIRE'}[k],8)
    elif k=='door_swing':
        line(d,-35,20,-25,20);line(d,20,20,35,20);line(d,-25,20,-25,-25)
        swing_arc(d,-25,20,45,-math.pi/2,0);circle(d,-25,20,2)
    elif k=='access_route':
        for y in (-12,12):
            for x in (-35,-15,5,25):line(d,x,y,min(x+12,35),y)
        line(d,-24,0,25,0);line(d,25,0,15,-6);line(d,25,0,15,6)
    elif k=='fence':
        line(d,-38,0,38,0)
        for x in (-30,-10,10,30):line(d,x-4,-7,x+4,7);line(d,x-4,7,x+4,-7)
    elif k=='gate':
        line(d,-38,20,-28,20);line(d,28,20,38,20)
        path_lines(d,[(-28,20),(-9,-12)]);path_lines(d,[(28,20),(9,-12)])
        swing_arc(d,-28,20,37,-math.pi/3,0);swing_arc(d,28,20,37,math.pi,4*math.pi/3)
        circle(d,-28,20,2);circle(d,28,20,2)
    elif k=='bollard':
        circle(d,0,0,12);circle(d,0,0,4);line(d,-20,0,-14,0);line(d,14,0,20,0)
        line(d,0,-20,0,-14);line(d,0,14,0,20)
    elif k=='north':
        line(d,0,22,0,-20);path_lines(d,[(-8,-6),(0,-22),(8,-6)])
        text(d,-4,-27,'N',9)
    elif k=='roof_edge':
        line(d,-38,-8,38,-8);line(d,-38,-3,38,-3)
        for x in (-30,-10,10,30):line(d,x,-3,x+6,8)
        text(d,-15,22,'EDGE',7)
    elif k=='salt':
        text(d,-15,-8,'SALT',8)
        for y in (4,15):path_lines(d,[(-32,y),(-24,y-5),(-16,y),(-8,y+5),(0,y),(8,y-5),(16,y),(24,y+5),(32,y)])
    elif k=='corrosion':
        rect(d,-26,-4,52,23)
        for x in (-16,0,16):line(d,x,-18,x,-8);line(d,x,-8,x-3,-12);line(d,x,-8,x+3,-12)
        for x in (-16,0,16):line(d,x-3,4,x+3,10);line(d,x-3,10,x+3,4)
        text(d,-15,29,'CORR',7)
    elif k=='flood':
        rect(d,-18,-23,36,26);line(d,-18,3,-18,23);line(d,18,3,18,23)
        path_lines(d,[(-35,10),(-27,5),(-19,10),(-11,15),(-3,10),(5,5),(13,10),(21,15),(29,10),(35,5)])
    elif k=='service_face':
        path_lines(d,[(-11,-2),(0,-15),(11,-2),(-11,-2)]);line(d,0,-2,0,19)
        text(d,-18,-22,'FRONT',7)
    else:raise ValueError('Unknown location preview geometry: '+k)
    text(d,-8,37,'NTS',6)

def installation_geometry(d,symbol):
    """Original NTS installation/legend graphics; deliberately no electrical ports."""
    if symbol.get('geometry_family')=='location-preview':return location_geometry(d,symbol)
    if symbol.get('geometry_family')=='drafting-marker':return drafting_geometry(d,symbol)
    k=symbol['geometry_kind']
    if k in ('tube','flex'):
        line(d,-38,-7,38,-7);line(d,-38,7,38,7)
        if k=='flex':
            for x in range(-30,35,8):line(d,x,-7,x-5,7)
        else:
            line(d,-30,-10,-30,10);line(d,30,-10,30,10)
        text(d,-18,-13,symbol['legend_text'],7)
    elif k=='elbow':
        path_lines(d,[(-38,-7),(7,-7),(7,30)]);path_lines(d,[(-38,7),(-7,7),(-7,30)])
    elif k=='offset':
        path_lines(d,[(-38,12),(-15,12),(10,-12),(38,-12)])
        path_lines(d,[(-38,20),(-11,20),(14,-4),(38,-4)])
    elif k in ('riser_up','riser_down'):
        circle(d,0,0,13);line(d,-38,0,-13,0)
        if k=='riser_up':line(d,-7,0,7,0);line(d,0,-7,0,7)
        else:line(d,-6,-6,6,6);line(d,-6,6,6,-6)
        text(d,17,4,'UP' if k=='riser_up' else 'DN',7)
    elif k in ('underground','overhead'):
        for start,end in [(-38,-24),(-17,-3),(4,18),(25,38)]:line(d,start,0,end,0)
        text(d,-8,-9,'UG' if k=='underground' else 'OH',8)
    elif k in ('sleeve','firestop'):
        line(d,-15,-24,-15,24);line(d,15,-24,15,24)
        rect(d,-20,-11,40,22);line(d,-38,-5,38,-5);line(d,-38,5,38,5)
        if k=='firestop':
            for x in (-17,-8,1,10):line(d,x,-11,x+6,-5);line(d,x,5,x+6,11)
            text(d,-7,-16,'FS',7)
    elif k=='expansion':
        line(d,-38,-5,-18,-5);line(d,-38,5,-18,5)
        rect(d,-18,-10,35,20);rect(d,2,-6,22,12)
        line(d,24,-5,38,-5);line(d,24,5,38,5)
    elif k=='support':
        circle(d,0,0,10);path_lines(d,[(-16,-10),(-16,14),(16,14),(16,-10)])
        line(d,-28,22,28,22);line(d,0,14,0,22)
    elif k=='conduit_body':
        rect(d,-22,-13,44,26);rect(d,-16,-8,32,16)
        circle(d,-16,0,1.5);circle(d,16,0,1.5)
        line(d,-38,-5,-22,-5);line(d,-38,5,-22,5);line(d,22,-5,38,-5);line(d,22,5,38,5)
    elif k=='pull_box':
        rect(d,-20,-20,40,40);line(d,-20,-20,20,20);line(d,-20,20,20,-20)
        text(d,24,4,'PB',7)
    elif k=='transition':
        line(d,-38,-7,-8,-7);line(d,-38,7,-8,7);rect(d,-8,-11,16,22)
        line(d,8,-7,38,-7);line(d,8,7,38,7)
        for x in range(15,37,7):line(d,x,-7,x-4,7)
    elif k=='pv_boundary':
        for x in (-35,-15,5,25):line(d,x,-22,min(x+12,35),-22);line(d,x,22,min(x+12,35),22)
        for y in (-22,-2,16):line(d,-35,y,-35,min(y+10,22));line(d,35,y,35,min(y+10,22))
        text(d,-7,4,'PV',9)
    elif k=='role_marker':
        path_lines(d,[(-21,0),(-14,-12),(18,-12),(25,0),(18,12),(-14,12),(-21,0)])
        line(d,-40,0,-21,0);text(d,-10,4,symbol['legend_text'],8)
    elif k=='fuel_tank':
        rect(d,-25,-14,50,28);line(d,-15,14,-15,23);line(d,15,14,15,23)
        line(d,0,-14,0,-23);line(d,-5,-23,5,-23);text(d,-14,4,'FUEL',7)
    elif k=='exhaust':
        rect(d,-27,3,20,17);path_lines(d,[(-17,3),(-17,-14),(32,-14)])
        line(d,32,-14,23,-20);line(d,32,-14,23,-8);text(d,2,13,'EXH',7)
    else:raise ValueError('Unknown installation geometry: '+k)

def drafting_geometry(d,symbol):
    k=symbol['geometry_kind'];label=symbol['marker_text']
    if k=='tag':
        rect(d,-36,-11,72,22);text(d,-len(label)*2.6,4,label,8)
    elif k=='note':
        circle(d,0,0,14);text(d,-7,4,label,9)
    elif k in ('detail','section'):
        circle(d,0,0,20);line(d,-20,0,20,0);text(d,-7,-5,label,8);text(d,-7,14,'S?',8)
        if k=='section':path_lines(d,[(-20,-7),(-32,0),(-20,7)])
    elif k=='revision':
        path_lines(d,[(-21,18),(0,-19),(21,18),(-21,18)]);text(d,-3,10,label,9)
    elif k=='match':
        line(d,-3,-22,-3,17);line(d,3,-22,3,17)
        line(d,-20,-12,20,-12);line(d,-20,10,20,10);text(d,-10,31,label,7)
    elif k=='scope':
        rect(d,-23,-12,46,24);text(d,-len(label)*2.7,4,label,8)
    elif k=='continuation':
        path_lines(d,[(-33,-12),(16,-12),(31,0),(16,12),(-33,12),(-33,-12)]);text(d,-14,4,label,8)
    elif k=='bidirectional':
        line(d,-35,0,35,0)
        for x,sign in ((-35,1),(35,-1)):line(d,x,0,x+sign*10,-6);line(d,x,0,x+sign*10,6)
        text(d,-12,-10,label,7)
    elif k=='control_legend':
        for x in (-35,-15,5,25):line(d,x,0,min(x+12,35),0)
        text(d,-15,-10,label,7)
    else:raise ValueError('Unknown drafting geometry: '+k)

def pv_geometry(d,symbol):
    """Functional PV blocks with explicit bundle/conductor/control port contracts."""
    k=symbol['id']
    if k=='pv_module':
        rect(d,-25,-20,50,40)
        for x in (-9,9):line(d,x,-20,x,20)
        line(d,-25,0,25,0);line(d,-40,0,-25,0);line(d,25,0,40,0)
        text(d,-22,-8,'+',7);text(d,14,-8,'-',7)
    elif k in ('pv_string','pv_string_polarized'):
        for x in (-26,-7,12):
            rect(d,x,-10,14,20)
            if x<12:line(d,x+14,0,x+19,0)
        if k=='pv_string':line(d,26,0,40,0)
        else:
            path_lines(d,[(26,0),(30,0),(30,-15),(40,-15)])
            path_lines(d,[(-26,0),(-31,0),(-31,25),(31,25),(31,15),(40,15)])
            text(d,34,-19,'+',6);text(d,34,12,'-',6)
    elif k=='pv_dc_combiner':
        rect(d,-25,-25,50,50);line(d,0,-15,0,15)
        line(d,-40,-15,0,-15);line(d,-40,15,0,15);line(d,0,0,40,0)
    elif k in ('pv_optimizer','pv_rapid_shutdown','pv_junction_box'):
        rect(d,-25,-20,50,40);line(d,-40,0,-25,0);line(d,25,0,40,0)
        text(d,-17,4,{'pv_optimizer':'OPT','pv_rapid_shutdown':'RSD','pv_junction_box':'JB'}[k],8)
        if k=='pv_junction_box':line(d,0,20,0,30)
        if k=='pv_rapid_shutdown':port_stub(d,next(p for p in symbol['ports'] if p['domain']=='control'))
    elif k=='pv_shutdown_initiator':
        rect(d,-24,-18,48,36);circle(d,0,0,10);text(d,-6,3,'S',8)
        port_stub(d,symbol['ports'][0],24,18)
    elif k=='pv_ac_module':
        rect(d,-25,-20,50,40);line(d,-4,-20,-4,20)
        line(d,-25,0,-4,0);line(d,-14,-20,-14,20)
        text(d,1,4,'AC',7);line(d,25,0,40,0);line(d,0,20,0,30)
    elif k=='pv_microinverter':
        rect(d,-25,-20,50,40);line(d,-25,20,25,-20);line(d,-40,0,-25,0);line(d,25,0,40,0)
        text(d,-20,-5,'DC',7);text(d,5,14,'AC',7);text(d,-16,-25,'MICRO',6)
    elif k=='pv_string_inverter_dual_mppt':
        rect(d,-25,-25,50,50);line(d,-25,25,25,-25)
        line(d,-40,-15,-25,-15);line(d,-40,15,-25,15);line(d,25,0,40,0)
        text(d,-20,-8,'DC',7);text(d,5,18,'AC',7)
    else:raise ValueError('Unknown PV geometry: '+k)

def definition(symbol):
    root = ET.Element('definition', {'type':'element','version':'0.80','width':'100','height':'80',
        'hotspot_x':'50','hotspot_y':'40','orientation':'dyyy','link_type':'simple'})
    sub(root, 'uuid', uuid=uid('symbol/'+symbol['id']))
    names = sub(root, 'names')
    sub(names, 'name', lang='en').text = symbol['name']
    sub(root, 'informations').text = ('Original generic artwork generated by qelectrotech-bess. CC0-1.0. '
        'Not a manufacturer-certified or exact standards-library symbol. ' + symbol['meaning'])
    d = sub(root, 'description')
    kind = symbol['id']
    if symbol.get('view_kind')=='installation-legend':
        installation_geometry(d,symbol)
    elif symbol.get('geometry_family')=='pv-detail':
        pv_geometry(d,symbol)
    elif symbol.get('geometry_family')=='interface-functional':
        interface_geometry(d,symbol)
    elif symbol.get('geometry_family')=='grounding-transfer':
        grounding_transfer_geometry(d,symbol)
    elif kind == 'utility':
        circle(d,0,0,20); text(d,-12,4,'GRID',7); line(d,20,0,40,0)
    elif kind == 'meter':
        circle(d,0,0,20); text(d,-5,5,'M',12); line(d,-40,0,-20,0); line(d,20,0,40,0)
    elif kind in ('breaker','disconnect','dc_disconnect'):
        line(d,-40,0,-12,0); line(d,12,0,40,0); line(d,-12,0,10,-15)
        if kind == 'breaker': rect(d,-4,-5,8,10)
    elif kind == 'bus':
        line(d,-40,0,40,0); line(d,0,-30,0,30)
    elif kind in ('battery','battery_module','battery_cell'):
        rect(d,-25,-20,50,40); line(d,-40,0,-25,0); line(d,25,0,40,0)
        line(d,-8,-12,-8,12); line(d,3,-7,3,7)
        if kind in ('battery_cell','battery_module'):text(d,-21,-7,'+',9)
        else:text(d,7,13,'DC',7)
    elif kind in ('pv_inverter','power_conversion_system','hybrid_inverter'):
        rect(d,-25,-20,50,40); line(d,-25,20,25,-20); line(d,-40,0,-25,0); line(d,25,0,40,0)
        text(d,-20,-5,'DC',7); text(d,5,14,'AC',7)
        if kind == 'hybrid_inverter': line(d,0,20,0,30)
    elif kind == 'pv_array':
        rect(d,-25,-20,50,40)
        for x in (-9,9): line(d,x,-20,x,20)
        line(d,-25,0,25,0); line(d,25,0,40,0)
    elif kind == 'transformer':
        circle(d,-8,0,16); circle(d,8,0,16); line(d,-40,0,-24,0); line(d,24,0,40,0)
    elif kind in ('load_panel','transfer_switch'):
        rect(d,-25,-20,50,40); line(d,-40,0,-25,0)
        text(d,-17,4,'LOAD' if kind=='load_panel' else 'XFER',8)
        if kind=='transfer_switch': line(d,25,0,40,0); line(d,0,20,0,30)
    elif kind == 'ground':
        line(d,0,-30,0,0); line(d,-18,0,18,0); line(d,-12,6,12,6); line(d,-6,12,6,12)
    elif kind in ('battery_rack','bess_cabinet','bess_container'):
        rect(d,-25,-25,50,50)
        if kind=='battery_rack':
            for y in (-17,-3,11): rect(d,-18,y,36,9)
        if kind=='bess_cabinet':
            line(d,0,-25,0,25);rect(d,7,-15,11,9)
        if kind=='bess_container':
            for x in (-20,-10,0,10,20): line(d,x,-25,x,25)
        for p in symbol['ports']:
            line(d,p['x'],p['y'],p['x']*0.625,p['y']*0.625)
    elif kind=='dc_fuse':
        line(d,-40,0,-20,0);rect(d,-20,-7,40,14);line(d,-20,0,20,0);line(d,20,0,40,0)
    elif kind=='dc_combiner':
        rect(d,-25,-25,50,50);line(d,0,-15,0,15)
        line(d,-40,-15,0,-15);line(d,-40,15,0,15);line(d,0,0,40,0)
    elif kind in ('controller','current_sensor','estop','bms'):
        rect(d,-25,-20,50,40); text(d,-19,4,{'controller':'CTRL','current_sensor':'CT','estop':'STOP','bms':'BMS'}[kind],8)
        for p in symbol['ports']:port_stub(d,p)
    else:
        raise ValueError(f'No geometry implemented for {kind}')
    for port in symbol['ports']:
        sub(d, 'terminal', x=port['x'], y=port['y'], orientation=port['orientation'],
            name=port['id'], uuid=uid('port/'+kind+'/'+port['id']))
    return root

def xml_write(root, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root)
    ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)

def symbol_svg(symbol, x=0, y=0):
    """Same original geometry for the contact sheet, not a QET renderer."""
    d = definition(symbol).find('description')
    g = ET.Element('g', {'transform':f'translate({x} {y})', 'fill':'none','stroke':'black','stroke-width':'1.4'})
    for el in d:
        a=el.attrib
        if el.tag=='line': ET.SubElement(g,'line',{k:a[k] for k in ('x1','y1','x2','y2')})
        elif el.tag=='rect': ET.SubElement(g,'rect',{k:a[k] for k in ('x','y','width','height')})
        elif el.tag=='ellipse': ET.SubElement(g,'ellipse',{'cx':str(float(a['x'])+float(a['width'])/2),'cy':str(float(a['y'])+float(a['height'])/2),'rx':str(float(a['width'])/2),'ry':str(float(a['height'])/2)})
        elif el.tag=='text':
            ET.SubElement(g,'text',{'x':a['x'],'y':a['y'],'font-size':a['size'],'font-family':'Arial','stroke':'none','fill':'black'}).text=a['text']
        elif el.tag=='terminal': ET.SubElement(g,'circle',{'cx':a['x'],'cy':a['y'],'r':'2','fill':'white'})
    return g

def build(output):
    catalog=json.loads((ROOT/'assets/catalog.json').read_text(encoding='utf-8'))
    target=output/'elements/bess'
    for s in catalog['symbols']: xml_write(definition(s),target/(s['id']+'.elmt'))
    cat=ET.Element('qet-directory'); names=sub(cat,'names'); sub(names,'name',lang='en').text='PV and BESS - original generic assets'
    xml_write(cat,target/'qet_directory')
    height=100+((len(catalog['symbols'])+3)//4)*130
    svg=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','viewBox':f'0 0 1000 {height}','width':'1000','height':str(height)})
    sub(svg,'rect',x=0,y=0,width=1000,height=height,fill='white')
    sub(svg,'text',x=30,y=30,fill='black',**{'font-family':'Arial','font-size':'20'}).text='PV / BESS ORIGINAL GENERIC SYMBOL LIBRARY'
    sub(svg,'text',x=30,y=52,fill='black',**{'font-family':'Arial','font-size':'12'}).text='CC0-1.0 artwork | schematic and installation legend assets | electrical terminals only where applicable'
    for i,s in enumerate(catalog['symbols']):
        x=125+(i%4)*245; y=110+(i//4)*130
        svg.append(symbol_svg(s,x,y))
        sub(svg,'text',x=x,y=y+53,fill='black',**{'text-anchor':'middle','font-family':'Arial','font-size':'12'}).text=s['id']
        port_label=', '.join(p['id']+':'+p['domain'] for p in s['ports']) if s['ports'] else 'Graphic only; no electrical terminals'
        for n,chunk in enumerate(textwrap.wrap(port_label,width=38)):
            sub(svg,'text',x=x,y=y+70+n*11,fill='black',**{'text-anchor':'middle','font-family':'Arial','font-size':'9'}).text=chunk
    xml_write(svg,output/'symbol-contact-sheet.svg')
    print(f"Created {len(catalog['symbols'])} original elements in {target}")

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--output',type=pathlib.Path,default=ROOT/'assets/library'); a=p.parse_args(); build(a.output)
