from sceneact import *
import bpy, math, random
from mathutils import Vector

# Reference inventory, approximate normalized image bounds:
# Architecture: pale cream room (0,0)-(1,1), yellow lower walls, glossy beige
# tiled floor below y=.43; ceiling with cross beams and five visible fans.
# Left windows/doors occupy x=0-.30, y=.16-.53, with bright window openings,
# dark timber frames and shutters. Right openings occupy x=.68-.99,y=.14-.60.
# Back stage x=.37-.66,y=.24-.44: green side curtains, dark recess, scalloped
# cream valance, central green chalkboard, pale blue board at its right.
# Wooden desks and benches overlap in receding rows, x=0-.93,y=.42-.89;
# their thin legs, open under-table spaces and detached benches are important.
# Foreground backpacks: black (.09,.72)-(.17,.91), black horizontal bag
# (.18,.76)-(.30,.84), blue (.63,.68)-(.73,.86), blue (.76,.58)-(.83,.74),
# dark bag (.48,.63)-(.56,.75). Small books lie on several desktops.
# Speakers high on both side walls, framed pictures and ceiling tube lights.
# Hidden rear furniture and the interiors behind doors remain uncertain.
# Assets below retain semantic child parts. Approximate expanded mesh count:
# architecture/openings 115; 21 desk/bench groups x 12 =252; stage 27;
# fans 30; bags 35; books/pictures/lights 30: approximately 490 primitives.
# No fillet-box, Boolean, or dense tube expansions are used.

random.seed(6)
scene = Scene('Sunlit classroom')
cream=(.87,.86,.68)
yellow=(.93,.68,.025)
wood=(.25,.18,.095)
topwood=(.30,.255,.17)
framewood=(.29,.24,.15)
black=(.018,.025,.027)
green=(.045,.19,.105)

def cube(parent,name,size,center,color):
    n=box(size=size,center=center,color=color)
    parent.include(name,n)
    return n

architecture=Asset('Room architecture')
cube(architecture,'Tiled floor',(9.2,20,.16),(0,6,-.08),(.69,.58,.36))
cube(architecture,'Left wall',( .18,19,4.8),(-4.55,6,2.4),cream)
cube(architecture,'Right wall',(.18,19,4.8),(4.55,6,2.4),cream)
cube(architecture,'Back wall',(9.2,.18,4.8),(0,15.45,2.4),cream)
cube(architecture,'Left yellow dado',(.025,19,1.12),(-4.445,6,.56),yellow)
cube(architecture,'Right yellow dado',(.025,19,1.12),(4.445,6,.56),yellow)
cube(architecture,'Back yellow dado',(9,.025,1.12),(0,15.34,.56),yellow)
cube(architecture,'Ceiling',(9.2,20,.15),(0,6,4.85),(.91,.91,.81))
for j,y in enumerate((-1.0,4.7,10.5)):
    cube(architecture,'Ceiling crossbeam%d'%j,(9,.23,.32),(0,y,4.62),(.89,.88,.77))
# Tile joints: a restrained grid; the surface shader adds subtle mottling.
for j in range(29):
    cube(architecture,'Floor transverse grout%d'%j,(9,.009,.003),(0,-3+j*.66,.004),(.49,.43,.30))
for j in range(15):
    cube(architecture,'Floor lengthwise grout%d'%j,(.009,19,.003),(-4.5+j*.66,6,.004),(.53,.46,.32))
scene.include('Architecture',architecture)

openings=Asset('Side windows and timber doors')
for side in (-1,1):
    x=side*4.43
    for j,y in enumerate((-.2,3.25,6.65,10.1,13.0)):
        a=Asset(('Left' if side<0 else 'Right')+' opening '+str(j))
        # Light panels stand slightly inside wall faces, framed as visible recesses.
        cube(a,'Dark wooden surround',(.09,1.72,2.85),(x,y,1.88),wood)
        cube(a,'Bright upper window',(.025,1.43,1.26),(x-side*.065,y,2.57),(.87,.94,.89))
        cube(a,'Window crossbar',(.055,1.5,.075),(x-side*.09,y,2.54),framewood)
        cube(a,'Window central mullion',(.055,.065,1.28),(x-side*.09,y,2.57),framewood)
        cube(a,'Lower timber door',(.06,1.42,1.48),(x-side*.07,y,1.16),(.37,.29,.15))
        for dy in (-.48,0,.48):
            cube(a,'Door panel stile'+str(dy),(.035,.035,1.32),(x-side*.115,y+dy,1.15),(.51,.41,.24))
        cube(a,'Door lower rail',(.035,1.4,.07),(x-side*.115,y,.58),framewood)
        cube(a,'Door upper rail',(.035,1.4,.07),(x-side*.115,y,1.7),framewood)
        openings.include(a.name,a)
# A partly opened right shutter near the rear.
shutter=box((.09,1.25,2.5),center=(4.05,10.8,1.55),color=(.37,.29,.18))
shutter.turn('z',-27)
openings.include('Open right shutter',shutter)
scene.include('Openings',openings)

stage=Asset('Rear teaching stage')
cube(stage,'Low raised platform',(5.9,2.35,.23),(0,14.15,.115),(.39,.31,.16))
cube(stage,'Dark stage recess',(5.55,.1,2.85),(0,15.18,2.3),(.065,.045,.025))
for x in (-2.64,2.64):
    cube(stage,'Green side curtain'+str(x),(.43,.18,2.98),(x,14.84,2.65),green)
    for dx in (-.13,.05,.17):
        cube(stage,'Curtain fold'+str((x,dx)),(.07,.055,2.96),(x+dx,14.72,2.65),(.07,.25,.12))
cube(stage,'Valance header',(5.55,.22,.30),(0,14.73,3.98),(.87,.84,.62))
for j in range(12):
    n=ball(.24,center=(-2.48+j*.45,14.70,3.77),color=(.86,.83,.65))
    n.resize((1,.42,.65))
    stage.include('Scalloped valance%d'%j,n)
board=Asset('Central chalkboard with stand')
cube(board,'Wooden outer frame',(2.65,.12,1.40),(.12,13.79,1.72),(.30,.30,.20))
cube(board,'Green writing surface',(2.49,.025,1.25),(.12,13.71,1.73),(.095,.23,.18))
cube(board,'Chalk tray',(2.7,.20,.055),(.12,13.60,1.04),(.46,.42,.25))
for x in (-.95,1.18):
    cube(board,'Support'+str(x),(.055,.09,1.07),(x,13.86,.65),framewood)
    board.include('Foot'+str(x),rod(.025,start=(x,13.35,.1),end=(x,14.25,.1),color=framewood))
board.include('Diagonal chalk mark',rod(.008,start=(-.85,13.69,1.1),end=(-.52,13.69,2.25),color=(.58,.64,.49)))
stage.include('Chalkboard',board)
cube(stage,'Pale blue display board',(.65,.09,1.48),(2.3,14.05,1.45),(.35,.66,.69))
scene.include('Stage',stage)

# Open wooden desk frames. Explicit dimensions control the occupied space and gaps.
DESK_W=1.68
DESK_D=.64
DESK_H=1.02
BENCH_D=.28
def school_desk(name,x,y):
    a=Asset(name)
    cube(a,'Broad worn desktop',(DESK_W,DESK_D,.085),(x,y,DESK_H),topwood)
    cube(a,'Front apron',(DESK_W-.10,.055,.17),(x,y-.25,.88),wood)
    for sx in (-1,1):
        for sy in (-1,1):
            cube(a,'Desk leg%d%d'%(sx,sy),(.065,.065,.96),
                 (x+sx*(DESK_W/2-.10),y+sy*.24,.49),framewood)
    cube(a,'Bench seat',(DESK_W-.08,BENCH_D,.065),(x,y-.72,.57),(.32,.26,.16))
    for sx in (-1,1):
        for sy in (-1,1):
            cube(a,'Bench leg%d%d'%(sx,sy),(.058,.055,.55),
                 (x+sx*.67,y-.72+sy*.085,.28),framewood)
    cube(a,'Bench low stretcher',(1.38,.045,.055),(x,y-.72,.23),framewood)
    return a

desks=[]
for col,(x,start,count) in enumerate(((-3.25,2.6,5),(-1.22,.95,6),(1.46,2.05,6),(3.55,3.55,4))):
    for row in range(count):
        y=start+row*1.65
        a=school_desk('Desk column%d row%d'%(col,row),x,y)
        scene.include(a.name,a)
        desks.append((x,y,col,row))
books=Asset('Books and classroom supplies')
for i,(x,y,c,r) in enumerate(desks):
    if i%3==0 or (c==1 and r==0):
        cube(books,'Book pages%d'%i,(.42,.27,.035),(x-.22,y,1.084),(.76,.73,.62))
        cube(books,'Book cover%d'%i,(.44,.28,.012),(x-.22,y,1.108),
             ((.16,.24,.31) if i%2 else (.34,.14,.16)))
    if i in (2,10,15):
        cube(books,'White notebook%d'%i,(.28,.22,.018),(x+.35,y+.04,1.077),(.85,.84,.74))
scene.include('Desktop supplies',books)

def backpack(name,x,y,h,color,tilt=0):
    a=Asset(name)
    body=ball(1,center=(x,y,h*.51),color=color)
    body.resize((h*.31,h*.19,h*.47))
    if tilt: body.turn('y',tilt)
    a.include('Rounded fabric body',body)
    pocket=ball(1,center=(x,y-h*.17,h*.35),color=tuple(v*.8 for v in color))
    pocket.resize((h*.245,h*.065,h*.24))
    a.include('Front pocket',pocket)
    a.include('Top carrying loop',sweep_tube(points=[(x-h*.09,y,h*.91),(x-h*.075,y,h*1.02),(x+h*.07,y,h*1.02),(x+h*.10,y,h*.91)],radius=.015,color=black))
    for s in (-1,1):
        a.include('Shoulder strap'+str(s),sweep_tube(points=[(x+s*h*.21,y+.04,h*.8),(x+s*h*.34,y+.11,h*.34),(x+s*h*.39,y-.03,.055)],radius=.024,color=black))
    a.include('Pocket zipper',rod(.009,start=(x-h*.20,y-h*.23,h*.48),end=(x+h*.20,y-h*.23,h*.48),color=(.45,.48,.43)))
    scene.include(name,a)
backpack('Foreground left black backpack',-2.95,-.02,.86,(.025,.045,.065),-12)
backpack('Foreground blue backpack',1.67,.43,.92,(.018,.25,.46),-7)
backpack('Right turquoise backpack',3.26,3.1,.83,(.015,.34,.44),12)
backpack('Central dark backpack',.27,3.0,.69,(.018,.025,.035),10)
backpack('Left middle blue backpack',-2.02,5.0,.58,(.02,.26,.47))
bag=Asset('Horizontal black school bag')
n=ball(1,center=(-1.95,.23,.15),color=(.018,.025,.029))
n.resize((.53,.20,.13))
bag.include('Soft bag body',n)
bag.include('Carrying strap',sweep_tube(points=[(-2.25,.22,.2),(-2.07,.20,.35),(-1.73,.20,.34),(-1.55,.2,.17)],radius=.022,color=black))
scene.include('Horizontal bag',bag)

fixtures=Asset('Wall fixtures and framed pictures')
for side,y,z in ((-1,1.2,3.55),(-1,11.8,3.35),(1,7.9,3.4)):
    speaker=box((.32,.48,.67),center=(side*4.22,y,z),color=(.025,.055,.06))
    speaker.turn('y',side*12)
    fixtures.include('Wall loudspeaker'+str((side,y)),speaker)
for side,ys in ((-1,(2.2,8.9)),(1,(3.2,6.2,11.9))):
    for j,y in enumerate(ys):
        cube(fixtures,'Picture frame'+str((side,j)),(.07,.47,.63),(side*4.40,y,3.93),(.35,.29,.14))
        cube(fixtures,'Picture paper'+str((side,j)),(.025,.38,.53),(side*4.35,y,3.93),(.76,.78,.63))
        cube(fixtures,'Portrait silhouette'+str((side,j)),(.015,.14,.29),(side*4.33,y,3.94),(.25,.36,.34))
scene.include('Fixtures',fixtures)

fans=Asset('Ceiling fans and fluorescent lights')
for j,(x,y) in enumerate(((-2.2,-.3),(2.25,.2),(-2.25,6.2),(2.20,6.6),(0,12))):
    a=Asset('Ceiling fan%d'%j)
    a.include('Downrod',rod(.027,start=(x,y,4.77),end=(x,y,4.27),color=(.27,.25,.20)))
    n=ball(.115,center=(x,y,4.25),color=(.23,.21,.17))
    n.resize((1,1,.55))
    a.include('Motor',n)
    for k in range(3):
        theta=math.radians(k*120+18+j*22)
        blade=box((.98,.16,.026),center=(x+math.cos(theta)*.56,y+math.sin(theta)*.56,4.25),color=(.27,.25,.21))
        blade.turn('z',math.degrees(theta))
        a.include('Fan blade%d'%k,blade)
    fans.include(a.name,a)
for j,y in enumerate((1.2,7.6,12.3)):
    cube(fans,'Tube light housing%d'%j,(2.5,.12,.065),(0,y,4.55),(.69,.69,.60))
    cube(fans,'White fluorescent tube%d'%j,(2.3,.065,.04),(0,y,4.50),(.95,.96,.85))
scene.include('Ceiling equipment',fans)

realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
nodes=sc.world.node_tree.nodes
background=nodes.get('Background')
if background is None:
    background=nodes.new('ShaderNodeBackground')
output=nodes.get('World Output')
if output is None:
    output=nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.80,.85,.77,1)
background.inputs['Strength'].default_value=.40

# Low, wide photographic viewpoint; the vanishing point lies near the rear board.
set_view((.05,-4.6,2.42),(0,10.8,1.95),lens=23.0,sensor=36)
area_emitter((-3.6,2.0,3.2),power=1500,size=4.5,target=(0,4,0),color=(1,.95,.78))
area_emitter((-3.5,9.6,3.2),power=1200,size=4,target=(0,9,1),color=(1,.98,.88))
area_emitter((3.3,5.0,3.6),power=900,size=4,target=(0,5,0),color=(1,.95,.80))
area_emitter((0,-1,4.3),power=650,size=5,target=(0,6,.4),color=(1,.96,.86))

# Restrained procedural variation gives broad timber and tile surfaces a worn finish.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Roughness'].default_value=.69
        col=bsdf.inputs['Base Color'].default_value
        if .55 < col[0] < .8 and .42 < col[1] < .7 and col[2] < .5:
            nt=mat.node_tree
            tex=nt.nodes.new('ShaderNodeTexNoise')
            tex.inputs['Scale'].default_value=16
            tex.inputs['Detail'].default_value=2
            ramp=nt.nodes.new('ShaderNodeValToRGB')
            ramp.color_ramp.elements[0].position=.15
            ramp.color_ramp.elements[0].color=(col[0]*.75,col[1]*.75,col[2]*.75,1)
            ramp.color_ramp.elements[1].position=.85
            ramp.color_ramp.elements[1].color=(min(col[0]*1.15,1),min(col[1]*1.15,1),min(col[2]*1.15,1),1)
            nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
            nt.links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
            bsdf.inputs['Roughness'].default_value=.36
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.45
