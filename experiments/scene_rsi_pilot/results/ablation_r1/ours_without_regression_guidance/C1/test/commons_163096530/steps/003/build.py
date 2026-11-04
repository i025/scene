from sceneact import *
import bpy, random

random.seed(14)
scene = Scene('Historic dormitory')

# Observations: step 2 places the locker and cropped right bunk near the
# reference landmarks. Its floor, ironwork and timbers remain much too pale.
# Architectural edges and foreground perspective are imperfect but coherent.
# Hypothesis: excessive fill light and light wood finishes flatten the scene.
# Main correction family: materials and illumination. Expected effect:
# dark worn floorboards, black iron silhouettes, yellow plaster and stronger
# contact shadows. Camera, dimensions, placements and semantic groups remain.
# Inventory: two left bunks, cropped right bunk, locker, fireplace, radiator,
# bin, circular wall fitting, timber framing, plaster, ceiling and board floor.
# Estimated landmarks: locker (307,174), hearth (401,192), aisle post (145,200).
# Camera scale and distance remain uncertain monocular assumptions.

iron = (.035,.045,.041)
linen = (.88,.89,.84)
wood = (.14,.067,.026)

def B(parent,key,size,center,color):
    return parent.include(key,box(size=size,center=center,color=color))

def R(parent,key,start,end,radius=.022,color=iron):
    return parent.include(key,rod(radius=radius,start=start,end=end,color=color))

# Architecture builder: individual supported boards and exposed timber frame.
room=Asset('room')
B(room,'floor foundation',(7.2,9,.12),(2.9,.6,-.075),wood)
for i in range(25):
    x=-.65+i*.285
    for j in range(4):
        y=-3.7+j*2.26+(i%3)*.17
        c=(.115+random.random()*.065,
           .052+random.random()*.033,
           .020+random.random()*.016)
        B(room,f'plank_{i}_{j}',(.279,2.247,.035),(x,y,.003),c)
B(room,'left plaster',(.13,8.7,3.05),(-.14,.65,1.525),(.58,.58,.36))
B(room,'rear plaster',(6.6,.15,3.05),(3.1,4.65,1.525),(.61,.62,.30))
B(room,'ceiling',(6.8,8.8,.13),(3,.6,3.09),(.52,.56,.33))
for i,y in enumerate([-3,-.8,1.5,3.65,4.52]):
    B(room,f'left stud_{i}',(.17,.16,3.03),(-.025,y,1.51),(.075,.047,.017))
for i,z in enumerate([.14,1.05,2.23,2.95]):
    B(room,f'left horizontal_{i}',(.17,8.7,.13),(-.015,.65,z),(.080,.050,.019))
for i,y in enumerate([-.5,3.4]):
    B(room,f'ceiling beam_{i}',(6.6,.22,.23),(3,y,2.98),(.055,.035,.012))
scene.include('architecture',room)

# Bunk builder: frame, bedding, ladder and plaque share a movable hierarchy.
def bunk(name,x,y,length=2.13,width=.94):
    a=Asset(name)
    for i,xx in enumerate([x-length/2,x+length/2]):
        for j,yy in enumerate([y-width/2,y+width/2]):
            R(a,f'post_{i}_{j}',(xx,yy,.06),(xx,yy,2.13),.027)
            a.include(f'cap_{i}_{j}',ball(radius=.033,center=(xx,yy,2.135),color=iron))
            B(a,f'foot_{i}_{j}',(.105,.105,.035),(xx,yy,.045),(.12,.13,.11))
    for k,z in enumerate([.46,1.59]):
        B(a,f'bed base_{k}',(length+.025,width,.075),(x,y,z),iron)
        a.include(f'mattress_{k}',fillet_box(
            size=(length-.035,width-.055,.16),radius=.065,
            center=(x,y,z+.115),color=linen))
        B(a,f'sheet edge_{k}',(length-.015,width+.018,.052),
          (x,y,z+.13),(.91,.92,.88))
        a.include(f'duvet_{k}',fillet_box(
            size=(length*.68,width-.045,.085),radius=.035,
            center=(x+.27,y,z+.223),color=(.87,.89,.86)))
        a.include(f'pillow_{k}',fillet_box(
            size=(.47,width*.77,.13),radius=.055,
            center=(x-length*.35,y,z+.255),color=(.96,.95,.89)))
        for j,yy in enumerate([y-width/2,y+width/2]):
            for n,zz in enumerate([z+.34,z+.49] if k==1 else [z+.23]):
                R(a,f'side rail_{k}_{j}_{n}',
                  (x-length/2,yy,zz),(x+length/2,yy,zz),.018)
        for j,xx in enumerate([x-length/2,x+length/2]):
            for n,zz in enumerate([z+.31,z+.48]):
                R(a,f'end rail_{k}_{j}_{n}',
                  (xx,y-width/2,zz),(xx,y+width/2,zz),.019)
    lx=x+length/2+.025
    for i,yy in enumerate([y-width*.35,y+width*.35]):
        R(a,f'ladder upright_{i}',(lx,yy,.13),(lx,yy,1.98),.021)
    for i in range(6):
        zz=.32+i*.27
        R(a,f'ladder rung_{i}',(lx,y-width*.35,zz),(lx,y+width*.35,zz),.018)
    B(a,'number plaque',(.11,.025,.17),
      (x+length/2-.08,y-width/2-.022,2.08),(.065,.085,.068))
    return a

scene.include('front left bunk',bunk('front left bunk',1,.15))
scene.include('rear left bunk',bunk('rear left bunk',1,2.28))
right=bunk('cropped right bunk',5.05,-1.52,length=2.15,width=.97)
right.turn('z',90,pivot=(5.05,-1.52,0))
scene.include('cropped right bunk',right)

# Locker builder: closed paneled left door and open right compartment.
cab=Asset('oak locker')
cx,cy=2.87,4.34
B(cab,'dark interior',(.92,.09,1.78),(cx,cy+.19,.99),(.052,.026,.009))
for i,x in enumerate([cx-.47,cx+.47]):
    B(cab,f'side_{i}',(.065,.48,1.83),(x,cy,.99),(.23,.105,.028))
B(cab,'divider',(.045,.43,1.76),(cx+.005,cy,.99),(.26,.125,.035))
for i,z in enumerate([.11,.83,1.88]):
    B(cab,f'shelf_{i}',(.97,.52,.065),(cx,cy,z),(.24,.105,.025))
B(cab,'cornice',(1.08,.59,.075),(cx,cy,1.94),(.30,.145,.045))
B(cab,'cornice lip',(1.13,.62,.035),(cx,cy,1.987),(.22,.095,.022))
B(cab,'closed door',(.43,.055,1.70),(cx-.235,cy-.26,.99),(.30,.135,.035))
for i,z in enumerate([.50,1.34]):
    B(cab,f'recessed panel_{i}',(.33,.013,.64),
      (cx-.235,cy-.294,z),(.23,.092,.020))
    for j,xx in enumerate([cx-.416,cx-.055]):
        B(cab,f'panel stile_{i}_{j}',(.025,.025,.70),
          (xx,cy-.309,z),(.34,.16,.045))
    for j,zz in enumerate([z-.35,z+.35]):
        B(cab,f'panel rail_{i}_{j}',(.38,.025,.026),
          (cx-.235,cy-.309,zz),(.34,.16,.045))
for i,x in enumerate([cx-.37,cx+.37]):
    B(cab,f'foot_{i}',(.12,.38,.13),(x,cy,.065),(.16,.065,.012))
for i,z in enumerate([.52,1.30]):
    cab.include(f'door knob_{i}',ball(
        radius=.018,center=(cx-.08,cy-.335,z),color=(.085,.07,.028)))
for i,x in enumerate([cx+.10,cx+.23,cx+.36]):
    R(cab,f'hook_{i}',(x,cy+.09,1.74),(x,cy-.015,1.69),.012,(.07,.06,.035))
scene.include('locker',cab)

# Fireplace builder: stone surround, hearth, inner lip and brick firebox.
fire=Asset('stone fireplace')
fx,fy=4.49,4.505
B(fire,'black opening',(1.36,.055,1.17),(fx,fy-.045,.59),(.035,.028,.017))
B(fire,'hearth slab',(1.97,.90,.07),(fx,4.22,.047),(.19,.17,.12))
for side in [-1,1]:
    for j in range(4):
        B(fire,f'jamb_{side}_{j}',(.24,.31,.30),
          (fx+side*.79,fy-.13,.18+j*.30),
          (.30+random.uniform(-.035,.035),.285,.215))
B(fire,'lintel',(1.86,.34,.25),(fx,fy-.13,1.36),(.34,.32,.245))
B(fire,'mantel top',(1.98,.38,.075),(fx,fy-.145,1.515),(.36,.34,.26))
for side in [-1,1]:
    R(fire,f'inner upright_{side}',
      (fx+side*.64,fy-.315,.10),(fx+side*.64,fy-.315,1.08),
      .045,(.22,.20,.14))
    R(fire,f'arch shoulder_{side}',
      (fx+side*.64,fy-.315,1.08),(fx+side*.51,fy-.315,1.18),
      .045,(.22,.20,.14))
R(fire,'arch top',(fx-.51,fy-.315,1.18),(fx+.51,fy-.315,1.18),
  .043,(.22,.20,.14))
for row in range(8):
    for col in range(5):
        xx=fx-.56+col*.255+(row%2)*.10
        if xx<fx+.61:
            c=random.choice([(.090,.078,.049),(.13,.105,.065),(.048,.043,.029)])
            B(fire,f'firebrick_{row}_{col}',(.235,.018,.102),
              (xx,fy-.083,.13+row*.119),c)
scene.include('fireplace',fire)

heater=Asset('portable radiator')
for i in range(9):
    B(heater,f'fin_{i}',(.022,.10,.48),(4.93+i*.035,4.16,.34),(.72,.73,.66))
for i,z in enumerate([.12,.57]):
    B(heater,f'crossbar_{i}',(.33,.12,.025),(5.07,4.16,z),(.68,.69,.61))
heater.turn('y',-10)
scene.include('heater',heater)

bin_asset=Asset('small black waste bin')
bin_asset.include('body',rod(radius=.095,length=.29,
    center=(5.5,4.18,.18),color=(.028,.033,.025)))
scene.include('bin',bin_asset)

disc=Asset('wall disc')
disc.include('rim',rod(radius=.105,length=.023,center=(3,4.545,2.36),
    axis='+y',color=(.34,.40,.32)))
disc.include('face',rod(radius=.089,length=.027,center=(3,4.528,2.36),
    axis='+y',color=(.47,.54,.44)))
scene.include('wall fitting',disc)

# API audit: all sizes and radii positive; every rod has distinct endpoints.
# Fillet radii .065/.035/.055 <= half minimum sizes .080/.0425/.065.
# All loop inclusion keys are unique. No support dependencies or bind cycles.
# Furniture and its support geometry retain the successful build's placement.
realize(scene)

for obj in bpy.data.objects:
    if obj.type!='MESH' or not obj.data.materials:
        continue
    ancestry=[]
    p=obj
    while p:
        ancestry.append(p.name.lower())
        p=p.parent
    labels=' '.join(ancestry)
    # Copy materials before per-object procedural customization.
    mat=obj.data.materials[0].copy()
    obj.data.materials[0]=mat
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get('Principled BSDF')
    base=tuple(bs.inputs['Base Color'].default_value)

    iswood=any(s in labels for s in [
        'plank_','oak locker','left stud','left horizontal','ceiling beam'])
    if iswood:
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=4
        tex.inputs['Detail'].default_value=3
        coord=nt.nodes.new('ShaderNodeTexCoord')
        mapping=nt.nodes.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(45,1.3,8)
        nt.links.new(coord.outputs['Generated'],mapping.inputs[0])
        nt.links.new(mapping.outputs[0],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.20
        ramp.color_ramp.elements[0].color=tuple(v*.48 for v in base[:3])+(1,)
        ramp.color_ramp.elements[1].position=.78
        ramp.color_ramp.elements[1].color=tuple(min(v*1.45,1) for v in base[:3])+(1,)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.24
        bump.inputs['Distance'].default_value=.014
        nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs[0],bs.inputs['Normal'])
        bs.inputs['Roughness'].default_value=.48 if 'plank_' in labels else .66
    elif 'bunk' in labels:
        if sum(base[:3])<.65:
            bs.inputs['Metallic'].default_value=.40
            bs.inputs['Roughness'].default_value=.35
        else:
            bs.inputs['Roughness'].default_value=.88
    elif 'stone fireplace' in labels or 'plaster' in labels or 'ceiling' in labels:
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=16
        tex.inputs['Detail'].default_value=3
        coord=nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(coord.outputs['Generated'],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color=tuple(v*.73 for v in base[:3])+(1,)
        ramp.color_ramp.elements[1].color=tuple(min(v*1.12,1) for v in base[:3])+(1,)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.19
        bump.inputs['Distance'].default_value=.013
        nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs[0],bs.inputs['Normal'])
        bs.inputs['Roughness'].default_value=.90

# Pose, lens and shift preserved from step 2, independently of object dimensions.
set_view(position=(3.86,-4.10,1.60),target=(1.84,4.30,1.36),
         lens=33,sensor=36,shift=(0,-.028))

world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new('World')
    bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.58,.62,.49,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.17
# Broad cool daylight from the unseen front-left opening, with subdued rear fill.
area_emitter(position=(1.0,-2.5,2.65),power=740,size=3.1,
             target=(1.8,1.6,.6),color=(.91,.95,1))
area_emitter(position=(4.4,1.8,2.7),power=100,size=3,
             target=(2.7,4.4,1),color=(1,.91,.68))

sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
