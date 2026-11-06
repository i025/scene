from sceneact import *
import bpy, math, random

# Reference inventory (normalized image estimates):
# Cream room and ceiling: full frame; yellow wall bases along both sides.
# Beige tiled floor: lower .43-1.0, with visible seams and subtle variation.
# Back stage: (.37,.24)-(.67,.44), dark recess, green curtains, cream scallops.
# Chalkboard: (.48,.33)-(.58,.42); blue display just to its right.
# Desks/benches: (0,.42)-(.93,.89), dark thin tops, slender legs, large open gaps.
# Foreground left desk: (.14,.59)-(.36,.89); right desk: (.51,.56)-(.70,.81).
# Side timber openings: left (0,.16)-(.30,.55), right (.68,.15)-(1,.62).
# Five ceiling fans, ceiling beams/tubes, high wall speakers and small portraits.
# Bags: black (.09,.72)-(.17,.91), horizontal black (.18,.76)-(.30,.84),
# blue (.63,.68)-(.73,.86), turquoise (.76,.58)-(.83,.74),
# dark central (.48,.63)-(.56,.75); small books on scattered desktops.
# Uncertain: concealed door interiors, rear furniture, curtain recess depth.
#
# Feedback comparison: first build was too pale; stage too small and low;
# foreground left desk was too central; board/ceiling shared a vertical error.
# Revision preserves named assets while correcting camera pitch/lens, local desk
# positions, curtain width and illumination/material contrast.
# Expanded primitive estimate: architecture 52, openings 91, stage 37,
# 21 desks*12=252, bags including tube expansions ~103, fixtures/books/fans ~70:
# approximately 605 meshes. No Boolean or fillet-box expansions.

random.seed(6)
scene = Scene('Classroom revision')
cream=(.78,.78,.60)
yellow=(.78,.52,.008)
wood=(.12,.075,.030)
topwood=(.135,.103,.058)
framewood=(.20,.145,.068)
black=(.009,.016,.021)
green=(.018,.115,.042)

def cube(parent,name,size,center,color):
    node=box(size=size,center=center,color=color)
    parent.include(name,node)
    return node

architecture=Asset('Room architecture')
cube(architecture,'Tiled floor',(9.2,20,.16),(0,6,-.08),(.59,.43,.22))
cube(architecture,'Left cream wall',(.18,19,4.8),(-4.55,6,2.4),cream)
cube(architecture,'Right cream wall',(.18,19,4.8),(4.55,6,2.4),cream)
cube(architecture,'Back wall',(9.2,.18,4.8),(0,15.45,2.4),cream)
for side in (-1,1):
    cube(architecture,'Yellow lower wall'+str(side),(.025,19,1.12),
         (side*4.445,6,.56),yellow)
cube(architecture,'Back yellow dado',(9,.025,1.12),(0,15.34,.56),yellow)
cube(architecture,'Ceiling',(9.2,20,.15),(0,6,4.85),(.85,.86,.77))
for j,y in enumerate((-1,4.7,10.5)):
    cube(architecture,'Crossbeam%d'%j,(9,.23,.32),(0,y,4.62),(.79,.80,.70))
for j in range(29):
    cube(architecture,'Transverse grout%d'%j,(9,.012,.003),
         (0,-3+j*.66,.004),(.40,.31,.18))
for j in range(15):
    cube(architecture,'Longitudinal grout%d'%j,(.012,19,.003),
         (-4.5+j*.66,6,.004),(.44,.34,.20))
scene.include('Architecture',architecture)

openings=Asset('Side windows and doors')
for side in (-1,1):
    x=side*4.43
    for j,y in enumerate((-.2,3.25,6.65,10.1,13.0)):
        a=Asset(('Left' if side<0 else 'Right')+' opening '+str(j))
        cube(a,'Timber surround',(.09,1.72,2.85),(x,y,1.88),wood)
        cube(a,'Daylit window',(.025,1.43,1.26),
             (x-side*.065,y,2.57),(.78,.87,.85))
        cube(a,'Horizontal window bar',(.055,1.5,.075),
             (x-side*.09,y,2.54),framewood)
        cube(a,'Vertical window bar',(.055,.065,1.28),
             (x-side*.09,y,2.57),framewood)
        cube(a,'Lower door',(.06,1.42,1.48),
             (x-side*.07,y,1.16),(.24,.15,.06))
        for dy in (-.48,0,.48):
            cube(a,'Door stile'+str(dy),(.035,.035,1.32),
                 (x-side*.115,y+dy,1.15),(.38,.27,.12))
        for z in (.58,1.7):
            cube(a,'Door rail'+str(z),(.035,1.4,.07),
                 (x-side*.115,y,z),framewood)
        openings.include(a.name,a)
shutter=box((.09,1.25,2.5),center=(4.05,10.8,1.55),color=(.25,.17,.085))
shutter.turn('z',-27)
openings.include('Open right shutter',shutter)
scene.include('Openings',openings)

stage=Asset('Rear teaching stage')
cube(stage,'Raised platform',(6.6,2.35,.23),(0,14.15,.115),(.28,.20,.08))
cube(stage,'Dark curtain recess',(6.25,.1,2.85),(0,15.18,2.3),(.022,.013,.008))
for x in (-3.0,3.0):
    cube(stage,'Green side curtain'+str(x),(.47,.18,2.98),
         (x,14.84,2.65),green)
    for dx in (-.15,.02,.16):
        cube(stage,'Curtain fold'+str((x,dx)),(.07,.055,2.96),
             (x+dx,14.72,2.65),(.025,.16,.055))
cube(stage,'Cream valance header',(6.25,.22,.30),
     (0,14.73,3.98),(.74,.70,.48))
for j in range(14):
    n=ball(.24,center=(-2.93+j*.45,14.70,3.77),color=(.77,.72,.52))
    n.resize((1,.42,.65))
    stage.include('Valance scallop%d'%j,n)
board=Asset('Central chalkboard and stand')
cube(board,'Wood frame',(2.65,.12,1.40),(.12,13.79,1.72),(.20,.22,.13))
cube(board,'Green writing surface',(2.49,.025,1.25),
     (.12,13.71,1.73),(.045,.15,.105))
cube(board,'Chalk tray',(2.7,.20,.055),(.12,13.60,1.04),(.32,.28,.13))
for x in (-.95,1.18):
    cube(board,'Stand leg'+str(x),(.055,.09,1.07),(x,13.86,.65),framewood)
    board.include('Stand foot'+str(x),rod(.025,start=(x,13.35,.1),
                  end=(x,14.25,.1),color=framewood))
board.include('Diagonal chalk mark',rod(.008,start=(-.85,13.69,1.1),
              end=(-.52,13.69,2.25),color=(.42,.51,.36)))
stage.include('Chalkboard',board)
cube(stage,'Blue display board',(.65,.09,1.48),(2.65,14.05,1.45),(.22,.54,.61))
scene.include('Stage',stage)

DESK_W=1.68
DESK_D=.64
DESK_H=1.02
BENCH_D=.28
def school_desk(name,x,y):
    a=Asset(name)
    cube(a,'Desktop',(DESK_W,DESK_D,.085),(x,y,DESK_H),topwood)
    cube(a,'Front apron',(DESK_W-.10,.055,.14),(x,y-.25,.895),wood)
    for sx in (-1,1):
        for sy in (-1,1):
            cube(a,'Desk leg%d%d'%(sx,sy),(.065,.065,.96),
                 (x+sx*(DESK_W/2-.10),y+sy*.24,.49),framewood)
    cube(a,'Bench seat',(DESK_W-.08,BENCH_D,.065),
         (x,y-.72,.57),(.18,.125,.055))
    for sx in (-1,1):
        for sy in (-1,1):
            cube(a,'Bench leg%d%d'%(sx,sy),(.058,.055,.55),
                 (x+sx*.67,y-.72+sy*.085,.28),framewood)
    cube(a,'Bench stretcher',(1.38,.045,.055),(x,y-.72,.23),framewood)
    return a

desks=[]
# Irregular stagger leaves the center aisle and foreground spaces visible.
columns=((-3.65,3.6,5),(-1.92,2.15,6),(1.10,3.15,6),(3.35,5.35,4))
for col,(x,start,count) in enumerate(columns):
    for row in range(count):
        y=start+row*1.65
        dx=(.08 if row%2 else 0)
        a=school_desk('Desk column%d row%d'%(col,row),x+dx,y)
        scene.include(a.name,a)
        desks.append((x+dx,y,col,row))
books=Asset('Books and supplies')
for i,(x,y,c,r) in enumerate(desks):
    if i%3==0 or (c==1 and r==0):
        cube(books,'Book pages%d'%i,(.42,.27,.035),
             (x-.22,y,1.084),(.72,.71,.62))
        cube(books,'Book cover%d'%i,(.44,.28,.012),(x-.22,y,1.108),
             (.055,.12,.19) if i%2 else (.26,.055,.075))
    if i in (2,10,15):
        cube(books,'Notebook%d'%i,(.28,.22,.018),
             (x+.35,y+.04,1.077),(.80,.79,.69))
scene.include('Desktop supplies',books)

def backpack(name,x,y,h,color,tilt=0):
    a=Asset(name)
    # Box core and rounded crown create a fuller, less egg-shaped schoolbag.
    cube(a,'Fabric lower body',(h*.53,h*.32,h*.57),
         (x,y,h*.36),color)
    body=ball(1,center=(x,y,h*.65),color=color)
    body.resize((h*.275,h*.165,h*.32))
    a.include('Rounded upper body',body)
    pocket=ball(1,center=(x,y-h*.175,h*.32),
                color=tuple(v*.72 for v in color))
    pocket.resize((h*.235,h*.060,h*.22))
    a.include('Front pocket',pocket)
    a.include('Carry loop',sweep_tube(
        points=[(x-h*.09,y,h*.91),(x-h*.075,y,h*1.02),
                (x+h*.07,y,h*1.02),(x+h*.10,y,h*.91)],
        radius=.015,color=black))
    for s in (-1,1):
        a.include('Shoulder strap'+str(s),sweep_tube(
            points=[(x+s*h*.21,y+.04,h*.8),
                    (x+s*h*.34,y+.11,h*.34),
                    (x+s*h*.39,y-.03,.055)],
            radius=.024,color=black))
    a.include('Pocket zipper',rod(.009,
        start=(x-h*.20,y-h*.23,h*.48),
        end=(x+h*.20,y-h*.23,h*.48),color=(.26,.31,.30)))
    if tilt:
        a.turn('y',tilt,pivot=(x,y,0))
    scene.include(name,a)

backpack('Foreground left black backpack',-2.55,1.65,.77,(.010,.023,.037),-7)
backpack('Foreground blue backpack',1.26,2.0,.84,(.006,.115,.30),-5)
backpack('Right turquoise backpack',2.80,5.15,.76,(.005,.19,.29),10)
backpack('Central dark backpack',.15,5.0,.66,(.008,.016,.026),8)
backpack('Left middle blue backpack',-2.56,6.5,.58,(.006,.12,.31))
bag=Asset('Horizontal black school bag')
n=ball(1,center=(-1.85,1.95,.15),color=(.008,.015,.019))
n.resize((.45,.19,.13))
bag.include('Soft bag body',n)
bag.include('Handle',sweep_tube(
    points=[(-2.13,1.94,.20),(-1.98,1.93,.34),
            (-1.69,1.93,.33),(-1.48,1.93,.17)],
    radius=.022,color=black))
scene.include('Horizontal bag',bag)

fixtures=Asset('Wall speakers and portraits')
for side,y,z in ((-1,1.2,3.55),(-1,11.8,3.35),(1,7.9,3.4)):
    speaker=box((.32,.48,.67),center=(side*4.22,y,z),
                color=(.009,.025,.027))
    speaker.turn('y',side*12)
    fixtures.include('Speaker'+str((side,y)),speaker)
for side,ys in ((-1,(2.2,8.9)),(1,(3.2,6.2,11.9))):
    for j,y in enumerate(ys):
        cube(fixtures,'Portrait frame'+str((side,j)),(.07,.47,.63),
             (side*4.40,y,3.93),(.24,.18,.075))
        cube(fixtures,'Portrait paper'+str((side,j)),(.025,.38,.53),
             (side*4.35,y,3.93),(.68,.70,.57))
        cube(fixtures,'Portrait figure'+str((side,j)),(.015,.14,.29),
             (side*4.33,y,3.94),(.12,.22,.20))
scene.include('Fixtures',fixtures)

fans=Asset('Ceiling equipment')
for j,(x,y) in enumerate(((-2.2,1.0),(2.25,1.3),(-2.25,7.2),
                         (2.20,7.6),(0,13.0))):
    a=Asset('Ceiling fan%d'%j)
    a.include('Downrod',rod(.027,start=(x,y,4.77),
                           end=(x,y,4.27),color=(.12,.105,.075)))
    n=ball(.115,center=(x,y,4.25),color=(.10,.085,.060))
    n.resize((1,1,.55))
    a.include('Motor',n)
    for k in range(3):
        theta=math.radians(k*120+18+j*22)
        blade=box((.98,.16,.026),
                  center=(x+math.cos(theta)*.56,y+math.sin(theta)*.56,4.25),
                  color=(.13,.11,.08))
        blade.turn('z',math.degrees(theta))
        a.include('Blade%d'%k,blade)
    fans.include(a.name,a)
for j,y in enumerate((2.2,8.6,13.3)):
    cube(fans,'Tube housing%d'%j,(2.5,.12,.065),(0,y,4.55),(.59,.60,.52))
    cube(fans,'Fluorescent tube%d'%j,(2.3,.065,.04),
         (0,y,4.50),(.91,.94,.87))
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
background.inputs['Color'].default_value=(.77,.84,.86,1)
background.inputs['Strength'].default_value=.24

# Increased downward pitch lifts the distant stage within the frame.
set_view((.05,-4.6,2.42),(0,10.8,.82),lens=30.5,sensor=36)
area_emitter((-3.6,2.0,3.2),power=470,size=3.4,
             target=(0,4,0),color=(1,.96,.84))
area_emitter((-3.5,9.6,3.2),power=420,size=3.3,
             target=(0,9,1),color=(1,.98,.91))
area_emitter((3.3,5.0,3.6),power=290,size=3.5,
             target=(0,5,0),color=(1,.97,.87))
area_emitter((0,-1,4.3),power=170,size=4,
             target=(0,6,.4),color=(1,.98,.91))

# Shared procedural floor finish; explicit grout meshes preserve the tile grid.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bsdf=mat.node_tree.nodes.get('Principled BSDF')
    if bsdf is None:
        continue
    bsdf.inputs['Roughness'].default_value=.65
    col=tuple(bsdf.inputs['Base Color'].default_value)
    if abs(col[0]-.59)<.025 and abs(col[1]-.43)<.025:
        nt=mat.node_tree
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=19
        tex.inputs['Detail'].default_value=2
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.15
        ramp.color_ramp.elements[0].color=(.43,.30,.14,1)
        ramp.color_ramp.elements[1].position=.85
        ramp.color_ramp.elements[1].color=(.68,.53,.31,1)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs['Color'],bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value=.32
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.30
