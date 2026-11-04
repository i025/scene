from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(14)
scene = Scene('Historic dormitory')

# Observations: dark iron bunks fill the left half; an open oak locker and
# stone fireplace stand on the yellow rear wall. A very close bunk crops right.
# Estimated landmarks: locker (307,174), hearth (401,192), main post (145,202).
# Camera distance and room depth are uncertain; dimensions use a coherent metre scale.
wood = (.25,.125,.052)
iron = (.085,.105,.102)
linen = (.88,.89,.84)
plaster = (.66,.66,.38)
stone = (.38,.36,.29)

def B(parent, key, size, center, color):
    return parent.include(key, box(size=size, center=center, color=color))

def R(parent, key, start, end, radius=.022, color=iron):
    return parent.include(key, rod(radius=radius, start=start, end=end, color=color))

# Architecture builder: individual boards, plaster surfaces and exposed oak frame.
room = Asset('room')
B(room,'floor foundation',(7.2,9,.12),(2.9,.6,-.075),wood)
for i in range(25):
    x=-.65+i*.285
    for j in range(4):
        y=-3.7+j*2.26+((i%3)*.17)
        c=(.28+random.random()*.075,.155+random.random()*.045,.073+random.random()*.025)
        B(room,f'plank_{i}_{j}',(.279,2.247,.035),(x,y,.003),c)
B(room,'left plaster',(.13,8.7,3.05),(-.14,.65,1.525),(.67,.67,.49))
B(room,'rear plaster',(6.6,.15,3.05),(3.1,4.65,1.525),plaster)
B(room,'ceiling',(6.8,8.8,.13),(3.0,.6,3.09),(.66,.68,.47))
for i,y in enumerate([-3.0,-.8,1.5,3.65,4.52]):
    B(room,f'left stud_{i}',(.17,.16,3.03),(-.025,y,1.51),(.16,.12,.065))
for i,z in enumerate([.14,1.05,2.23,2.95]):
    B(room,f'left horizontal_{i}',(.17,8.7,.13),(-.015,.65,z),(.17,.125,.062))
for i,y in enumerate([-.5,3.4]):
    B(room,f'ceiling beam_{i}',(6.6,.22,.23),(3.0,y,2.98),(.12,.095,.046))
scene.include('architecture',room)

# Bunk builder: all frames, mattresses, pillows and ladders share one asset.
def bunk(name,x,y,length=2.13,width=.94):
    a=Asset(name)
    for i,xx in enumerate([x-length/2,x+length/2]):
        for j,yy in enumerate([y-width/2,y+width/2]):
            R(a,f'post_{i}_{j}',(xx,yy,.06),(xx,yy,2.13),.027)
            a.include(f'cap_{i}_{j}',ball(radius=.033,center=(xx,yy,2.135),color=iron))
            B(a,f'foot_{i}_{j}',(.105,.105,.035),(xx,yy,.045),(.21,.22,.19))
    for k,z in enumerate([.46,1.59]):
        B(a,f'bed base_{k}',(length+.025,width,.075),(x,y,z),iron)
        a.include(f'mattress_{k}',fillet_box(size=(length-.035,width-.055,.16),
                  radius=.065,center=(x,y,z+.115),color=linen))
        # White bedding has an overhanging thin edge and a broad folded blanket.
        B(a,f'sheet edge_{k}',(length-.015,width+.018,.052),(x,y,z+.13),(.91,.92,.88))
        a.include(f'duvet_{k}',fillet_box(size=(length*.68,width-.045,.085),
                  radius=.035,center=(x+.27,y,z+.223),color=(.87,.89,.86)))
        a.include(f'pillow_{k}',fillet_box(size=(.47,width*.77,.13),
                  radius=.055,center=(x-length*.35,y,z+.255),color=(.96,.95,.89)))
        for j,yy in enumerate([y-width/2,y+width/2]):
            for n,zz in enumerate([z+.34,z+.49] if k==1 else [z+.23]):
                R(a,f'side rail_{k}_{j}_{n}',(x-length/2,yy,zz),
                  (x+length/2,yy,zz),.018)
        for j,xx in enumerate([x-length/2,x+length/2]):
            for n,zz in enumerate([z+.31,z+.48]):
                R(a,f'end rail_{k}_{j}_{n}',(xx,y-width/2,zz),
                  (xx,y+width/2,zz),.019)
    # Ladder on the end nearest the aisle.
    lx=x+length/2+.025
    for i,yy in enumerate([y-width*.35,y+width*.35]):
        R(a,f'ladder upright_{i}',(lx,yy,.13),(lx,yy,1.98),.021)
    for i in range(6):
        zz=.32+i*.27
        R(a,f'ladder rung_{i}',(lx,y-width*.35,zz),(lx,y+width*.35,zz),.018)
    # Small black, wall-like bed number plate.
    B(a,'number plaque',(.11,.025,.17),(x+length/2-.08,y-width/2-.022,2.08),(.12,.15,.13))
    return a

scene.include('front left bunk',bunk('front left bunk',1.00,.15))
scene.include('rear left bunk',bunk('rear left bunk',1.00,2.28))
# The right-hand foreground object intentionally extends beyond the image.
right=bunk('cropped right bunk',5.05,-1.52,length=2.15,width=.97)
right.turn('z',90,pivot=(5.05,-1.52,0))
scene.include('cropped right bunk',right)

# Locker builder: open right compartment, closed paneled left door, visible hooks.
cab=Asset('oak locker')
cx=2.87
cy=4.34
B(cab,'dark interior',(.92,.09,1.78),(cx,cy+.19,.99),(.105,.063,.025))
for i,x in enumerate([cx-.47,cx+.47]):
    B(cab,f'side_{i}',(.065,.48,1.83),(x,cy,.99),(.30,.16,.059))
B(cab,'divider',(.045,.43,1.76),(cx+.005,cy,.99),(.33,.18,.063))
for i,z in enumerate([.11,.83,1.88]):
    B(cab,f'shelf_{i}',(.97,.52,.065),(cx,cy,z),(.31,.16,.049))
B(cab,'cornice',(1.08,.59,.075),(cx,cy,1.94),(.37,.21,.085))
B(cab,'cornice lip',(1.13,.62,.035),(cx,cy,1.987),(.28,.15,.052))
B(cab,'closed door',(.43,.055,1.70),(cx-.235,cy-.26,.99),(.38,.21,.078))
for i,z in enumerate([.50,1.34]):
    B(cab,f'recessed panel_{i}',(.33,.013,.64),(cx-.235,cy-.294,z),(.31,.155,.047))
    for j,xx in enumerate([cx-.416,cx-.055]):
        B(cab,f'panel stile_{i}_{j}',(.025,.025,.70),(xx,cy-.309,z),(.42,.24,.091))
    for j,zz in enumerate([z-.35,z+.35]):
        B(cab,f'panel rail_{i}_{j}',(.38,.025,.026),(cx-.235,cy-.309,zz),(.42,.24,.091))
for i,x in enumerate([cx-.37,cx+.37]):
    B(cab,f'foot_{i}',(.12,.38,.13),(x,cy,.065),(.24,.12,.036))
for i,z in enumerate([.52,1.30]):
    cab.include(f'door knob_{i}',ball(radius=.018,center=(cx-.08,cy-.335,z),color=(.12,.11,.06)))
for i,x in enumerate([cx+.10,cx+.23,cx+.36]):
    R(cab,f'hook_{i}',(x,cy+.09,1.74),(x,cy-.015,1.69),.012, color=(.12,.11,.08))
scene.include('locker',cab)

# Fireplace builder: a shallow dark recess, individually jointed stone surround.
fire=Asset('stone fireplace')
fx=4.49
fy=4.505
B(fire,'black opening',(1.36,.055,1.17),(fx,fy-.045,.59),(.075,.066,.049))
B(fire,'hearth slab',(1.97,.90,.07),(fx,4.22,.047),(.30,.28,.22))
# Irregular block faces remain economical separate meshes.
for side in [-1,1]:
    for j in range(4):
        B(fire,f'jamb_{side}_{j}',(.24,.31,.30),(fx+side*.79,fy-.13,.18+j*.30),
          (.40+random.uniform(-.035,.035),.385,.31))
B(fire,'lintel',(1.86,.34,.25),(fx,fy-.13,1.36),(.43,.415,.345))
B(fire,'mantel top',(1.98,.38,.075),(fx,fy-.145,1.515),(.45,.435,.36))
# Shaped inner lip, around the dark firebox.
for side in [-1,1]:
    R(fire,f'inner upright_{side}',(fx+side*.64,fy-.315,.10),
      (fx+side*.64,fy-.315,1.08),.045,color=(.32,.30,.24))
    R(fire,f'arch shoulder_{side}',(fx+side*.64,fy-.315,1.08),
      (fx+side*.51,fy-.315,1.18),.045,color=(.32,.30,.24))
R(fire,'arch top',(fx-.51,fy-.315,1.18),(fx+.51,fy-.315,1.18),.043,color=(.32,.30,.24))
# Soot-darkened brick backing with staggered mortar lines.
for row in range(8):
    for col in range(5):
        xx=fx-.56+col*.255+(row%2)*.10
        if xx<fx+.61:
            c=random.choice([(.19,.18,.14),(.23,.21,.16),(.14,.135,.105)])
            B(fire,f'firebrick_{row}_{col}',(.235,.018,.102),(xx,fy-.083,.13+row*.119),c)
scene.include('fireplace',fire)

# Narrow white electric heater leaning inside the fireplace's right edge.
heater=Asset('portable radiator')
for i in range(9):
    xx=4.93+i*.035
    B(heater,f'fin_{i}',(.022,.10,.48),(xx,4.16,.34),(.72,.73,.66))
for i,z in enumerate([.12,.57]):
    B(heater,f'crossbar_{i}',(.33,.12,.025),(5.07,4.16,z),(.68,.69,.61))
heater.turn('y',-10)
scene.include('heater',heater)
bin=Asset('small black waste bin')
bin.include('body',rod(radius=.095,length=.29,center=(5.50,4.18,.18),color=(.065,.073,.065)))
scene.include('bin',bin)

# Small circular rear-wall fitting above the locker.
clock=Asset('wall disc')
clock.include('rim',rod(radius=.105,length=.023,center=(3.00,4.545,2.36),
                        axis='+y',color=(.47,.51,.43)))
clock.include('face',rod(radius=.089,length=.027,center=(3.00,4.528,2.36),
                         axis='+y',color=(.60,.65,.57)))
scene.include('wall fitting',clock)

# All primitive dimensions are positive; fillet radii are <= half the minimum
# dimension. Indexed keys are unique. Supports are constructed at floor height;
# no bind dependencies are needed, and each movable object has its own hierarchy.
realize(scene)

# Subtle procedural grain supplies worn boards without image textures.
for obj in bpy.data.objects:
    if obj.type!='MESH':
        continue
    ancestry=[]
    p=obj
    while p:
        ancestry.append(p.name.lower())
        p=p.parent
    labels=' '.join(ancestry)
    if 'plank_' in labels or 'oak locker' in labels or 'left stud' in labels or 'ceiling beam' in labels:
        if not obj.data.materials:
            continue
        mat=obj.data.materials[0].copy()
        obj.data.materials[0]=mat
        mat.use_nodes=True
        nt=mat.node_tree
        bs=nt.nodes.get('Principled BSDF')
        base=bs.inputs['Base Color'].default_value[:]
        tex=nt.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value=4
        tex.inputs['Detail'].default_value=3
        coord=nt.nodes.new('ShaderNodeTexCoord')
        mapping=nt.nodes.new('ShaderNodeVectorMath')
        mapping.operation='MULTIPLY'
        mapping.inputs[1].default_value=(35,1.4,7)
        nt.links.new(coord.outputs['Generated'],mapping.inputs[0])
        nt.links.new(mapping.outputs[0],tex.inputs['Vector'])
        ramp=nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.20
        ramp.color_ramp.elements[0].color=tuple(v*.56 for v in base[:3])+(1,)
        ramp.color_ramp.elements[1].position=.78
        ramp.color_ramp.elements[1].color=tuple(min(v*1.4,1) for v in base[:3])+(1,)
        nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
        bump=nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.19
        bump.inputs['Distance'].default_value=.018
        nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs[0],bs.inputs['Normal'])
        bs.inputs['Roughness'].default_value=.72
    elif 'bunk' in labels:
        for mat in obj.data.materials:
            mat.use_nodes=True
            bs=mat.node_tree.nodes.get('Principled BSDF')
            rgba=bs.inputs['Base Color'].default_value
            if sum(rgba[:3])<.65:
                bs.inputs['Metallic'].default_value=.68
                bs.inputs['Roughness'].default_value=.33

set_view(position=(4.15,-5.7,1.73), target=(2.55,3.05,1.48),
         lens=33, sensor=36, shift=(0,0))
world=bpy.context.scene.world
if world is None:
    world=bpy.data.worlds.new('World')
    bpy.context.scene.world=world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.58,.62,.49,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.33
area_emitter(position=(2.7,-3.2,3.0),power=1150,size=4.2,
             target=(1.8,1.6,.6),color=(.93,.96,1.0))
area_emitter(position=(4.4,1.8,2.7),power=220,size=3.0,
             target=(2.7,4.4,1.0),color=(1.0,.91,.68))
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=32
sc.render.resolution_x=512
sc.render.resolution_y=341
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.look='AgX - Medium High Contrast'
