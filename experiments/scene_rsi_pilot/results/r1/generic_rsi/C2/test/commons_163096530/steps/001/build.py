from sceneact import *
import bpy, math, random
from mathutils import Vector
random.seed(9)

# Visible assemblies: timber/plaster room, worn plank floor, three left bunks,
# cropped right foreground bunk, oak wardrobe, stone fireplace and fire tools.
# Approximate reference landmarks (uncertain by .03-.06):
# back-left ceiling corner (.45,.19), wardrobe (.60,.51),
# fireplace opening (.79,.56), main outer bedpost (.28,.88),
# foreground right post (.94,.50). Filled white bedding contrasts with open rails.
# Bed depths and camera distance are ambiguous; preserve the open central floor.
ROOM_W, ROOM_D, ROOM_H = 6.5, 8.5, 3.25
CAMERA = (2.65,-5.5,1.65)
TARGET = (-.10,3.25,1.48)
LENS = 30
BACK = 4.5

scene=Scene('Historic dormitory')
plaster=(.69,.70,.43)
ceiling=(.66,.68,.49)
timber=(.15,.105,.055)
metal=(.115,.14,.135)
white=(.89,.89,.79)
wood=(.31,.17,.065)
stone=(.41,.39,.30)

room=Asset('Room architecture')
room.include('back plaster',box((6.6,.17,3.3),center=(.05,BACK+.085,1.65),color=plaster))
room.include('left plaster',box((.16,9.1,3.3),center=(-3.24,.05,1.65),color=(.73,.73,.56)))
room.include('ceiling',box((6.6,9.1,.13),center=(.05,.05,3.315),color=ceiling))
for z in (1.18,2.48,3.18):
    room.include('left longitudinal beam '+str(z),box((.16,9.1,.13),center=(-3.12,.05,z),color=timber))
for i,y in enumerate((-3.5,-1.7,.2,2.2,4.37)):
    room.include('wall upright '+str(i),box((.19,.14,3.23),center=(-3.11,y,1.615),color=timber))
for i,x in enumerate((-3.1,.55)):
    room.include('ceiling beam '+str(i),box((.20,9,.22),center=(x,.05,3.20),color=timber))
scene.include('Room',room)

floor=Asset('Individual floorboards')
for i in range(23):
    x=-3.25+(i+.5)*.29
    for j in range(4):
        y=-4.9+j*2.4+(i%3)*.32
        c=random.uniform(.82,1.12)
        floor.include(f'board {i} {j}',box((.282,2.386,.075),center=(x,y,.005),
                      color=(.29*c,.205*c,.115*c)))
scene.include('Floor',floor)

def bunk(name,x,y,length=2.2,width=1.0,top=1.82):
    a=Asset(name)
    low=.49
    for i,xx in enumerate((x-width/2,x+width/2)):
        for j,yy in enumerate((y-length/2,y+length/2)):
            a.include(f'post {i} {j}',rod(.029,start=(xx,yy,.06),end=(xx,yy,top+.43),color=metal))
            a.include(f'post cap {i} {j}',ball(.035,center=(xx,yy,top+.43),color=metal))
    for k,z in enumerate((low,top)):
        a.include(f'mattress support {k}',box((width+.035,length+.03,.085),center=(x,y,z-.065),color=metal))
        a.include(f'white mattress {k}',box((width-.035,length-.025,.145),center=(x,y,z+.045),color=white))
        # Broad, slightly uneven folded bedcover and a distinct pillow.
        a.include(f'cover {k}',box((width-.018,length*.72,.045),center=(x,y-length*.12,z+.135),color=(.94,.94,.85)))
        a.include(f'pillow {k}',box((width*.77,.43,.115),center=(x,y+length*.34,z+.17),color=(.97,.965,.87)))
        for side,xx in enumerate((x-width/2,x+width/2)):
            a.include(f'long frame {k} {side}',rod(.022,start=(xx,y-length/2,z-.02),end=(xx,y+length/2,z-.02),color=metal))
        for end,yy in enumerate((y-length/2,y+length/2)):
            for r,h in enumerate((.22,.37)):
                a.include(f'end rail {k} {end} {r}',rod(.019,start=(x-width/2,yy,z+h),end=(x+width/2,yy,z+h),color=metal))
    # Upper side guard rails leave the central volume visibly open.
    for side,xx in enumerate((x-width/2,x+width/2)):
        for r,h in enumerate((.24,.39)):
            a.include(f'upper side rail {side} {r}',rod(.018,start=(xx,y-length/2,top+h),end=(xx,y+length/2,top+h),color=metal))
    lx=x+width/2+.035
    ly=y-length*.13
    for j,yy in enumerate((ly-.20,ly+.20)):
        a.include(f'ladder upright {j}',rod(.022,start=(lx,yy,.08),end=(lx,yy,top+.35),color=metal))
    for j,z in enumerate((.38,.70,1.02,1.34,1.66)):
        a.include(f'ladder rung {j}',rod(.017,start=(lx,ly-.2,z),end=(lx,ly+.2,z),color=metal))
    return a

scene.include('Main left bunk',bunk('Main left bunk',-2.35,.15,2.35,1.16,1.84))
scene.include('Rear left bunk',bunk('Rear left bunk',-2.40,2.88,2.15,1.06,1.76))
# A further narrow bunk is visible beyond the main bed near the back corner.
scene.include('Back narrow bunk',bunk('Back narrow bunk',-1.11,3.20,1.82,.80,1.73))

# Near-camera bed: the majority lies outside the frame.
scene.include('Cropped foreground bunk',bunk('Cropped foreground bunk',3.18,-1.72,2.25,1.15,1.92))
fg=Asset('Foreground wooden end panel')
fg.include('warm wood panel',box((.065,.94,2.28),center=(2.60,-1.68,1.15),color=(.43,.23,.075)))
scene.include('Foreground panel',fg)

cab=Asset('Oak wardrobe')
cx,cy=.02,4.20
cw,ch,cd=.93,1.91,.43
cab.include('back',box((cw,.045,ch),center=(cx,cy+.20,ch/2+.06),color=(.20,.12,.045)))
for side in (-1,1):
    cab.include('side '+str(side),box((.065,cd,ch),center=(cx+side*(cw/2-.032),cy,ch/2+.06),color=wood))
cab.include('base',box((1.00,.49,.095),center=(cx,cy,.12),color=wood))
cab.include('cornice',box((1.06,.52,.075),center=(cx,cy,2.015),color=(.35,.205,.075)))
cab.include('top',box((.96,.46,.06),center=(cx,cy,1.955),color=wood))
cab.include('middle shelf',box((.87,.42,.045),center=(cx,cy,.94),color=(.37,.22,.085)))
# Left full-height door; right side has a dark open upper compartment.
cab.include('closed left door',box((.405,.045,1.74),center=(cx-.235,cy-.232,1.04),color=(.38,.215,.073)))
cab.include('lower right door',box((.39,.045,.72),center=(cx+.225,cy-.232,.53),color=(.33,.18,.059)))
for n,z in enumerate((.53,1.46)):
    cab.include('left raised panel '+str(n),box((.30,.018,.66),center=(cx-.235,cy-.264,z),color=(.34,.185,.06)))
for n,z in enumerate((.52,1.08)):
    cab.include('small handle '+str(n),ball(.018,center=(cx-.075,cy-.28,z),color=(.12,.11,.065)))
cab.include('hanging rail',rod(.012,start=(cx+.04,cy-.03,1.82),end=(cx+.40,cy-.03,1.82),color=metal))
for i in range(3):
    xx=cx+.12+i*.095
    cab.include('hanging dark garment '+str(i),box((.065,.07,.42),center=(xx,cy+.02,1.57),color=(.13,.12,.08)))
for x in (cx-.37,cx+.37):
    cab.include('foot '+str(x),box((.09,.32,.12),center=(x,cy,.06),color=wood))
scene.include('Wardrobe',cab)

fire=Asset('Stone fireplace')
fx=1.99
fire.include('dark firebox back',box((1.34,.045,1.12),center=(fx,4.395,.61),color=(.105,.105,.083)))
fire.include('hearth slab',box((1.94,.81,.075),center=(fx,4.15,.06),color=(.30,.29,.24)))
# Broad masonry piers and lintel create a substantial surround, not an outline.
for side in (-1,1):
    for j in range(3):
        fire.include(f'jamb {side} {j}',box((.27,.38,.39),center=(fx+side*.80,4.30,.27+j*.385),
                     color=(.43+j*.018,.42+j*.015,.34+j*.014)))
for i in range(5):
    fire.include('lintel '+str(i),box((.385,.41,.31),center=(fx+(i-2)*.38,4.29,1.365+(.025 if i in (1,2,3) else 0)),color=(.47,.46,.37)))
# Inner arch stones soften the squared masonry opening.
for side in (-1,1):
    q=box((.17,.33,.24),center=(fx+side*.62,4.28,1.115),color=(.43,.42,.34))
    q.turn('y',side*23)
    fire.include('arch shoulder '+str(side),q)
# Soot-dark exposed rear brickwork.
for row in range(6):
    for col in range(5):
        xx=fx-.50+col*.23+(row%2)*.10
        if xx<fx+.61:
            fire.include(f'fire brick {row} {col}',box((.213,.025,.105),center=(xx,4.36,.18+row*.118),
                         color=random.choice([(.19,.18,.14),(.26,.24,.18),(.14,.15,.12)])))
scene.include('Fireplace',fire)

tools=Asset('Hearth objects')
# Small pale ribbed heater leaning inside the right of the fireplace.
heater=Asset('Leaning fire grate')
for i in range(8):
    heater.include('pale rib '+str(i),rod(.012,start=(2.34+i*.037,4.02,.12),end=(2.34+i*.037,4.02,.65),color=(.65,.67,.58)))
for z in (.15,.62):
    heater.include('crossbar '+str(z),rod(.018,start=(2.32,4.02,z),end=(2.63,4.02,z),color=(.55,.57,.50)))
heater.turn('y',-10)
tools.include('heater',heater)
tools.include('black coal bucket',rod(.092,length=.23,center=(2.94,4.05,.17),color=(.055,.065,.058)))
tools.include('poker',rod(.012,start=(2.88,4.27,.08),end=(2.87,4.27,1.47),color=metal))
tools.include('poker handle',rod(.02,length=.09,center=(2.87,4.27,1.50),color=metal))
scene.include('Hearth accessories',tools)

clock=Asset('Small round wall clock')
clock.include('rim',rod(.116,length=.028,center=(.13,4.375,2.44),axis='+y',color=(.45,.51,.43)))
clock.include('face',rod(.101,length=.032,center=(.13,4.353,2.44),axis='+y',color=(.66,.69,.59)))
clock.include('hand one',rod(.004,start=(.13,4.328,2.44),end=(.13,4.328,2.50),color=(.30,.34,.28)))
clock.include('hand two',rod(.004,start=(.13,4.327,2.44),end=(.17,4.327,2.42),color=(.30,.34,.28)))
scene.include('Wall clock',clock)

realize(scene)

# Procedural surface finish only; no external images.
def descendants(name):
    ob=bpy.data.objects.get(name)
    return list(ob.children_recursive) if ob else []
def textured_material(name,base,scale,rough=.85,grain=False):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    n=m.node_tree.nodes
    l=m.node_tree.links
    bs=n.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=rough
    tex=n.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value=scale
    tex.inputs['Detail'].default_value=3
    coord=n.new('ShaderNodeTexCoord')
    if grain:
        mapping=n.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(5,.24,3)
        l.new(coord.outputs['Generated'],mapping.inputs[0])
        l.new(mapping.outputs[0],tex.inputs['Vector'])
    else:
        l.new(coord.outputs['Generated'],tex.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.18
    ramp.color_ramp.elements[0].color=tuple(v*.64 for v in base)+(1,)
    ramp.color_ramp.elements[1].position=.82
    ramp.color_ramp.elements[1].color=tuple(min(1,v*1.28) for v in base)+(1,)
    l.new(tex.outputs['Fac'],ramp.inputs[0])
    l.new(ramp.outputs[0],bs.inputs['Base Color'])
    bump=n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.19
    bump.inputs['Distance'].default_value=.035 if not grain else .012
    l.new(tex.outputs['Fac'],bump.inputs['Height'])
    l.new(bump.outputs[0],bs.inputs['Normal'])
    return m

floor_mat=textured_material('Worn brown oak grain',(.31,.215,.12),7,grain=True)
for ob in descendants('Floor'):
    if ob.type=='MESH':
        ob.data.materials.clear()
        ob.data.materials.append(floor_mat)
stone_mat=textured_material('Weathered limestone',(.44,.43,.35),9)
for ob in descendants('Fireplace'):
    if ob.type=='MESH' and ob.location.z>1.1:
        ob.data.materials.clear()
        ob.data.materials.append(stone_mat)
for ob in bpy.data.objects:
    if ob.type=='MESH':
        for mat in ob.data.materials:
            if mat and mat.use_nodes:
                bs=mat.node_tree.nodes.get('Principled BSDF')
                if bs:
                    bs.inputs['Roughness'].default_value=.78

set_view(CAMERA,TARGET,lens=LENS)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.68,.56,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.40
area_emitter((-.8,-2.3,2.8),power=650,size=4.3,target=(-1,1.5,.8),color=(1,.96,.82))
area_emitter((2.6,.7,3.0),power=190,size=3,target=(.5,4,1.2),color=(1,.97,.80))
sc.view_settings.view_transform='AgX'
