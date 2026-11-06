from sceneact import *
import bpy, math, random
from mathutils import Vector

random.seed(16)
scene = Scene('Quiet timber hall')

ivory = (.73,.74,.69)
wood = (.46,.48,.42)
lightwood = (.66,.68,.61)
floorcolor = (.78,.79,.74)
dark = (.20,.22,.19)

def add(name, obj):
    scene.include(name, obj)
    return obj

add('continuous pale floor', box((32,32,.16), center=(0,2,-.08), color=floorcolor))
add('rear plaster wall', box((27,.22,7.4), center=(0,10,3.7), color=ivory))
add('right plaster wall', box((.22,23,7.4), center=(9,0,3.7), color=ivory))
add('left plaster wall', box((.22,23,7.4), center=(-12,0,3.7), color=ivory))
add('rear skirting', box((27,.065,.12), center=(0,9.84,.06), color=(.28,.29,.23)))
add('right skirting', box((.065,23,.12), center=(8.84,0,.06), color=(.28,.29,.23)))

# A shallow recess beneath the transverse timber lintel.
add('recess right return', box((.16,3.4,3.15), center=(5.5,8.25,1.575), color=ivory))
add('return baseboard', box((.045,3.4,.12), center=(5.39,8.25,.06), color=(.28,.29,.23)))
add('transverse deep timber lintel', box((27,.73,.91), center=(0,6.25,4.18), color=wood))
add('lower pale lintel edge', box((27,.77,.12), center=(0,6.23,3.68), color=lightwood))

# Closely spaced timber boards on the roof.
for j in range(63):
    y = -10 + j*.34
    add('roof plank %02d'%j,
        box((27,.332,.115), center=(0,y,7.04),
            color=(.68+random.uniform(-.035,.035),
                   .69+random.uniform(-.035,.035),
                   .63+random.uniform(-.035,.035))))
    for x in (-10,-6,-2,2,6,10):
        if random.random() < .73:
            add('roof nail %s %s'%(j,x),
                rod(.012, start=(x,y,6.975), end=(x,y,6.965), color=(.29,.30,.26)))

# Slim beams supporting the boarded ceiling.
for x in (-9,3.5,9):
    add('ceiling longitudinal rib %s'%x,
        box((.18,24,.34), center=(x,1,6.81), color=wood))

# The dominant laminated tree support is made of continuous adjacent
# strips, each following the same curved structural profile.
def beam_strip(name, points, width, depth, color):
    part = Asset(name)
    for k,(a,b) in enumerate(zip(points[:-1], points[1:])):
        dx,dy,dz = b[0]-a[0],b[1]-a[1],b[2]-a[2]
        length = math.sqrt(dx*dx+dy*dy+dz*dz)
        node = box((width,depth,length+.018),
                   center=((a[0]+b[0])/2,(a[1]+b[1])/2,(a[2]+b[2])/2),
                   color=color)
        node.turn('y', math.degrees(math.atan2(dx,dz)))
        part.include(str(k),node)
    add(name,part)

base_x=-3.0
for strip in range(11):
    off=(strip-5)*.067
    c=(.40+random.uniform(-.035,.035),
       .43+random.uniform(-.035,.035),
       .37+random.uniform(-.035,.035))
    # Right arm sweeps outward gently at the foot and widely overhead.
    pts=[]
    for k in range(43):
        t=k/42
        z=.11+7.18*t
        x=base_x+off+5.8*(t**3.1)
        pts.append((x,0,z))
    beam_strip('right arch lamination %02d'%strip,pts,.066,.73,c)

    # Left arm rises into the opposing ceiling bay.
    pts=[]
    for k in range(43):
        t=k/42
        z=.11+7.18*t
        x=base_x+off-2.6*(t**2.5)
        pts.append((x,.015,z))
    beam_strip('left arch lamination %02d'%strip,pts,.066,.71,c)

add('dark foot collar', box((.79,.79,.16),center=(base_x,0,.08),color=(.25,.27,.21)))

# Timber-clad jambs frame the broad opening.
for side,x0,x1 in [('left',-4.5,-2.55),('right',6.0,8.0)]:
    count=int((x1-x0)/.14)
    for i in range(count):
        x=x0+(i+.5)*(x1-x0)/count
        v=random.uniform(-.055,.045)
        add('%s vertical wall board %02d'%(side,i),
            box(((x1-x0)/count-.009,.19,3.63),
                center=(x,6.18,1.815),
                color=(.60+v,.62+v,.56+v)))

# Vent grilles set into the long horizontal timber fascia.
for i,(x,w) in enumerate([(-8.4,1.65),(-.4,1.45),(5.3,1.0)]):
    add('vent pale frame %d'%i, box((w+.09,.035,.35),center=(x,5.865,4.18),color=(.73,.74,.68)))
    add('vent dark inset %d'%i, box((w,.045,.265),center=(x,5.838,4.18),color=(.27,.29,.26)))
    for n in range(int(w/.10)):
        xx=x-w/2+.055+n*.10
        add('grille division %d %d'%(i,n),
            box((.011,.012,.25),center=(xx,5.808,4.18),color=(.50,.52,.46)))

for i,x in enumerate((-8.1,-4.8)):
    add('wall ventilation surround %d'%i,
        box((.90,.035,.29),center=(x,9.865,3.24),color=(.80,.81,.75)))
    add('wall ventilation shadow %d'%i,
        box((.76,.045,.20),center=(x,9.84,3.24),color=(.37,.39,.34)))
    for n in range(9):
        add('wall vent slat %d %d'%(i,n),
            box((.018,.012,.19),center=(x-.34+n*.083,9.809,3.24),color=lightwood))

# Small wall fittings and a narrow door on the right.
add('door inset',box((.83,.045,2.28),center=(5.00,9.855,1.14),color=(.64,.66,.60)))
for x in (4.56,5.44):
    add('door jamb '+str(x),box((.035,.055,2.32),center=(x,9.81,1.16),color=(.48,.51,.45)))
add('door head',box((.91,.055,.035),center=(5,9.81,2.32),color=(.48,.51,.45)))
add('door handle',box((.035,.06,.16),center=(5.31,9.765,1.06),color=(.27,.29,.26)))
add('exit sign',box((.29,.045,.17),center=(5,9.80,2.57),color=(.38,.43,.36)))
for x in (-1.3,3.5):
    add('low wall socket '+str(x),box((.075,.035,.06),center=(x,9.85,.16),color=(.28,.30,.26)))
add('wall utility panel',box((.38,.035,.25),center=(3.55,9.85,.54),color=(.67,.69,.63)))

# Suspended cylindrical pendant shades.
for i,(x,y,z,r) in enumerate([(0.3,2.9,5.25,.34),(7.8,4.2,5.13,.29)]):
    add('pendant suspension %d'%i,
        rod(.017,start=(x,y,z+.60),end=(x,y,6.92),color=(.24,.26,.22)))
    add('pendant ceiling rose %d'%i,
        rod(.075,start=(x,y,6.88),end=(x,y,6.96),color=(.35,.37,.31)))
    add('pendant cylindrical shade %d'%i,
        rod(r,start=(x,y,z-.50),end=(x,y,z+.55),color=(.37,.39,.33)))
    add('pendant bottom diffuser %d'%i,
        rod(r*.94,start=(x,y,z-.515),end=(x,y,z-.50),color=(.94,.95,.87)))

realize(scene)

# Subtle procedural grain gives the timber its washed, archival character.
for mat in bpy.data.materials:
    if not mat.use_nodes:
        mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value=.78

for ob in bpy.data.objects:
    if ob.type!='MESH':
        continue
    name=ob.name.lower()
    if any(s in name for s in ('lamination','plank','timber','board','rib')):
        for slot in ob.material_slots:
            mat=slot.material
            if not mat:
                continue
            mat.use_nodes=True
            nt=mat.node_tree
            bs=nt.nodes.get('Principled BSDF')
            tex=nt.nodes.new('ShaderNodeTexNoise')
            tex.inputs['Scale'].default_value=4
            tex.inputs['Detail'].default_value=3
            coord=nt.nodes.new('ShaderNodeTexCoord')
            mapping=nt.nodes.new('ShaderNodeVectorMath')
            mapping.operation='MULTIPLY'
            mapping.inputs[1].default_value=(26,26,1.4)
            nt.links.new(coord.outputs['Generated'],mapping.inputs[0])
            nt.links.new(mapping.outputs[0],tex.inputs['Vector'])
            bump=nt.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value=.18
            bump.inputs['Distance'].default_value=.025
            nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
            nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

set_view((7.8,-15.0,3.65),(0.0,5.0,3.35),lens=35,sensor=36)
area_emitter((-6,-5,6.4),power=1800,size=8,target=(-1,4,0),color=(1,.99,.94))
area_emitter((5,-3,6.7),power=1300,size=7,target=(2,6,1),color=(.96,.98,1))
area_emitter((-8,6,5.3),power=700,size=5,target=(-3,3,1))
for x,y,z in [(0.3,2.9,4.72),(7.8,4.2,4.60)]:
    area_emitter((x,y,z),power=80,size=.55,target=(x,y,0),color=(1,1,.94))

world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.77,.80,.75,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.65
sc=bpy.context.scene
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=512
sc.render.resolution_y=406
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=.55
sc.view_settings.gamma=1.0
