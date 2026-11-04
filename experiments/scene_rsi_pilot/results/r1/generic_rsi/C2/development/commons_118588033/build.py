from sceneact import *
import bpy
import math

# Visible assemblies: red deck, cream ship interior, ceiling beams and pipes,
# three left bunks, foreground vented cabinets, rear lockers, chair, utility
# cabinet, brown/cream pillar, red wall fixture and cropped right bench.
# Approximate image landmarks (u,v): lamp (.39,.16), heater (.13,.32),
# rear lockers (.51,.48), bunk post (.39,.53), pillar foot (.72,.84),
# red fixture (.81,.55), right bench (.91,.88). Estimates are uncertain.
# Bunks have filled pale mattresses with open spaces between; lockers, wall
# panels and bench seat are solid. Room depth and hidden bunk supports uncertain.

P = dict(camera=(0,-4.65,1.65), target=(0,3.1,1.83), lens=25,
         width=4.0, depth=9.2, height=3.15,
         pillar_x=.87, pillar_y=-1.55,
         ambient=.33, key_power=370)
cream=(.69,.69,.54)
ivory=(.78,.79,.67)
steel=(.37,.41,.39)
dark=(.055,.08,.075)
brown=(.24,.095,.045)
deck=(.34,.125,.073)
white=(.73,.75,.66)

scene=Scene('Ship sleeping compartment')

def B(parent,name,size,center,color):
    parent.include(name,box(size=size,center=center,color=color))
def R(parent,name,a,b,r,color):
    parent.include(name,rod(radius=r,start=a,end=b,color=color))

architecture=Asset('Architecture')
B(architecture,'Deck',(4.2,10,.12),(0,.1,-.06),deck)
B(architecture,'Left wall',(.13,9.5,3.15),(-2.06,.1,1.575),cream)
B(architecture,'Right wall',(.13,9.5,3.15),(2.06,.1,1.575),ivory)
B(architecture,'Rear bulkhead',(4.2,.14,3.15),(0,4.7,1.575),cream)
B(architecture,'Ceiling',(4.2,9.6,.13),(0,.1,3.21),(.50,.47,.33))
for x in (-1.98,1.98):
    B(architecture,'Baseboard'+str(x),(.055,9.5,.18),(x,.1,.09),brown)
for i,y in enumerate((-3.3,-1.2,1.0,3.2)):
    B(architecture,'Ceiling crossbeam'+str(i),(4,.15,.28),(0,y,3.03),(.57,.40,.23))
for i,x in enumerate((-1.55,-.85,.02,.8,1.55)):
    B(architecture,'Ceiling rib'+str(i),(.075,9.3,.12),(x,.1,3.06),(.65,.53,.36))
# Subtle deck plate joints.
for i,y in enumerate((-2.9,-1.5,.05,1.6,3.15)):
    B(architecture,'Deck seam'+str(i),(4,.009,.002),(0,y,.002),(.23,.105,.068))
B(architecture,'Long deck seam',(.009,9,.002),(-.35,.1,.002),(.25,.105,.068))
scene.include('Architecture',architecture)

pillar=Asset('Main support pillar')
R(pillar,'Lower painted column',(.87,-1.55,.04),(.87,-1.55,1.66),.105,brown)
R(pillar,'Upper cream column',(.87,-1.55,1.66),(.87,-1.55,3.17),.105,(.76,.65,.42))
R(pillar,'Foot collar',(.87,-1.55,.015),(.87,-1.55,.065),.139,(.38,.20,.105))
R(pillar,'Ceiling collar',(.87,-1.55,3.05),(.87,-1.55,3.15),.15,(.58,.40,.23))
scene.include('Main support pillar',pillar)

bunks=Asset('Left three tier bunks')
# Long bunk edges recede into the compartment. Thin supports remain true openings.
for j,z in enumerate((.43,1.06,1.69)):
    B(bunks,'Bed pan '+str(j),(1.16,3.75,.065),(-1.39,1.12,z),(.23,.28,.25))
    B(bunks,'Mattress '+str(j),(1.10,3.65,.125),(-1.4,1.12,z+.095),white)
    B(bunks,'Folded pillow '+str(j),(.75,.43,.14),(-1.40,2.48,z+.21),(.79,.80,.71))
    R(bunks,'Outer edge rail '+str(j),(-.79,-.76,z+.02),(-.79,3.0,z+.02),.025,dark)
    R(bunks,'Rear end rail '+str(j),(-1.96,3.0,z+.10),(-.79,3.0,z+.10),.022,dark)
    # Two small seams on the pale mattress sides.
    for k,y in enumerate((.2,1.9)):
        B(bunks,'Mattress binding %s %s'%(j,k),(.012,.018,.105),(-.841,y,z+.10),(.56,.59,.52))
for k,y in enumerate((-.78,2.99)):
    for q,x in enumerate((-1.97,-.78)):
        R(bunks,'Bed upright %s %s'%(k,q),(x,y,.03),(x,y,2.48),.027,dark)
R(bunks,'Top outer stretcher',(-.78,-.78,2.36),(-.78,3.0,2.36),.024,dark)
# The low, wide, dark strip on the image's left edge.
B(bunks,'Low side apron',(.12,3.95,.28),(-1.94,1.05,.25),(.055,.115,.105))
scene.include('Left bunks',bunks)

ventcab=Asset('Foreground vented cabinets')
for j,y in enumerate((-1.08,-.34)):
    B(ventcab,'Cabinet body '+str(j),(.39,.65,.85),(-1.80,y,.83),(.075,.12,.12))
    B(ventcab,'Raised door '+str(j),(.028,.57,.75),(-1.588,y,.83),(.16,.22,.21))
    for k in range(12):
        B(ventcab,'Louver %s %s'%(j,k),(.024,.46,.018),(-1.568,y,.51+k*.052),(.045,.08,.08))
    B(ventcab,'Handle '+str(j),(.03,.035,.11),(-1.548,y-.19,.94),(.38,.41,.36))
scene.include('Foreground vented cabinets',ventcab)

lockers=Asset('Rear metal lockers')
for i,x in enumerate((-.58,-.04,.50)):
    B(lockers,'Body '+str(i),(.52,.53,1.75),(x,3.53,.925),steel)
    B(lockers,'Door '+str(i),(.48,.028,1.63),(x,3.247,.94),(.46,.49,.45))
    for k in range(4):
        B(lockers,'Upper slit %s %s'%(i,k),(.25,.009,.014),(x,3.226,1.50-k*.065),(.23,.28,.26))
    B(lockers,'Latch '+str(i),(.035,.035,.13),(x+.15,3.21,1.05),(.16,.20,.18))
    for dx in (-.18,.18):
        B(lockers,'Foot %s %s'%(i,dx),(.045,.35,.10),(x+dx,3.53,.05),dark)
# Rounded silhouettes of bedding and stored objects above the lockers.
for i,x in enumerate((-.68,-.24,.23,.58)):
    lockers.include('Stored roll '+str(i),ball(radius=.13,center=(x,3.55,1.87),color=(.48,.49,.39)))
scene.include('Rear lockers',lockers)

utility=Asset('Rear utility cabinet and pipes')
B(utility,'Dark cabinet',(.90,.62,.86),(.65,2.30,.49),(.25,.27,.22))
B(utility,'Cabinet top',(.97,.69,.06),(.65,2.30,.95),(.35,.36,.28))
B(utility,'Front door',(.73,.025,.70),(.65,1.975,.48),(.29,.31,.26))
B(utility,'Door seam',(.012,.012,.68),(.64,1.954,.48),(.12,.15,.13))
for i,x in enumerate((.31,.82,1.11)):
    R(utility,'Pipe riser '+str(i),(x,2.64,.98),(x,2.64,2.40),.025,(.25,.25,.17))
    R(utility,'Pipe top '+str(i),(x,2.64,2.40),(x,3.02,2.40),.025,(.25,.25,.17))
    R(utility,'Valve stem '+str(i),(x,2.64,1.13),(x,2.48,1.13),.018,dark)
    R(utility,'Valve bar '+str(i),(x-.07,2.47,1.13),(x+.07,2.47,1.13),.014,dark)
scene.include('Utility cabinet',utility)

chair=Asset('Metal chair')
cx,cy=-.22,2.15
B(chair,'Seat',(.46,.46,.055),(cx,cy,.47),(.41,.39,.27))
for i,dx in enumerate((-.20,.20)):
    R(chair,'Front leg '+str(i),(cx+dx,cy-.18,.02),(cx+dx,cy-.18,.48),.018,(.58,.59,.48))
    R(chair,'Back frame '+str(i),(cx+dx,cy+.18,.02),(cx+dx,cy+.23,.99),.018,(.58,.59,.48))
B(chair,'Back cushion',(.40,.065,.30),(cx,cy+.23,.82),(.27,.29,.22))
for i,dx in enumerate((-.25,.25)):
    R(chair,'Arm '+str(i),(cx+dx,cy-.20,.69),(cx+dx,cy+.19,.72),.018,(.57,.58,.47))
    R(chair,'Arm support '+str(i),(cx+dx,cy-.16,.49),(cx+dx,cy-.16,.69),.015,(.57,.58,.47))
scene.include('Chair',chair)

wallfixtures=Asset('Wall equipment')
# White heater housing on the near left wall; black curved-looking louver field.
B(wallfixtures,'Heater casing',(.29,.66,.67),(-1.84,-.12,2.22),(.69,.71,.61))
B(wallfixtures,'Heater inset',(.018,.52,.48),(-1.682,-.12,2.22),(.08,.11,.10))
for k in range(6):
    B(wallfixtures,'Heater horizontal slat '+str(k),(.035,.51,.028),(-1.66,-.12,2.02+k*.075),(.64,.67,.58))
B(wallfixtures,'Right dark notice board',(.035,1.13,.79),(1.973,1.66,1.84),(.23,.28,.26))
for y in (1.08,2.24):
    B(wallfixtures,'Notice frame '+str(y),(.045,.035,.84),(1.943,y,1.84),(.47,.45,.32))
# Red emergency fixture, mounted on the right bulkhead.
B(wallfixtures,'Red backing',(.11,.40,.65),(1.91,.10,1.10),(.68,.045,.025))
wallfixtures.include('Red rounded head',ball(radius=.195,center=(1.86,.10,1.38),color=(.80,.065,.035)))
B(wallfixtures,'Red front case',(.16,.34,.47),(1.82,.10,1.09),(.75,.065,.035))
R(wallfixtures,'White fixture handle',(1.72,.05,1.30),(1.72,.05,1.43),.035,(.85,.82,.67))
B(wallfixtures,'Black fixture slot',(.015,.15,.045),(1.727,.10,1.03),(.21,.075,.04))
B(wallfixtures,'Small wall label',(.015,.27,.34),(1.975,1.00,1.24),(.82,.82,.69))
scene.include('Wall equipment',wallfixtures)

bench=Asset('Cropped right bench')
B(bench,'Seat',(.58,2.30,.085),(1.68,-2.65,.49),(.035,.115,.10))
for j,y in enumerate((-3.53,-1.80)):
    for i,x in enumerate((1.46,1.91)):
        R(bench,'Leg %s %s'%(j,i),(x,y,.02),(x,y,.47),.025,(.09,.14,.12))
    R(bench,'Cross support '+str(j),(1.43,y,.20),(1.95,y,.20),.018,dark)
scene.include('Right bench',bench)

pipes=Asset('Ceiling plumbing')
for i,x in enumerate((-1.56,-1.04,.46)):
    R(pipes,'Long pipe '+str(i),(x,-3.7,2.76),(x,4.45,2.76),.035,(.62,.66,.58))
for i,y in enumerate((-.7,1.60,3.35)):
    R(pipes,'Cross pipe '+str(i),(-1.95,y,2.65),(.60,y,2.65),.026,(.60,.64,.57))
    R(pipes,'Left elbow drop '+str(i),(-1.95,y,2.25),(-1.95,y,2.65),.028,(.60,.64,.57))
# Dark service pipes on the far wall.
for i,x in enumerate((-.30,.20,.73)):
    R(pipes,'Rear vertical '+str(i),(x,4.53,1.84),(x,4.53,2.90),.043,(.16,.19,.15))
    R(pipes,'Rear top bend '+str(i),(x,4.53,2.90),(x-.24,4.53,2.90),.043,(.16,.19,.15))
scene.include('Overhead and rear pipes',pipes)

lamps=Asset('Pendant lamps')
lamp_positions=[(-.62,-1.12,2.75),(-.17,1.22,2.73),(.10,3.32,2.72)]
for i,(x,y,z) in enumerate(lamp_positions):
    R(lamps,'Suspension '+str(i),(x,y,z+.13),(x,y,3.12),.022,(.16,.18,.16))
    # Separate shallow dome, rim and luminous underside.
    lamps.include('Shade dome '+str(i),ball(radius=.19,center=(x,y,z+.035),color=(.38,.42,.39)).resize((1,1,.39)))
    R(lamps,'Shade rim '+str(i),(x,y,z-.005),(x,y,z+.018),.222,(.67,.69,.62))
    R(lamps,'Light face '+str(i),(x,y,z-.014),(x,y,z-.006),.199,(1,.98,.85))
scene.include('Pendant lamps',lamps)

realize(scene)
set_view(P['camera'],P['target'],lens=P['lens'],sensor=36)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.63,.66,.57,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=P['ambient']
area_emitter((-.55,-1.08,2.64),power=P['key_power'],size=1.35,target=(0,.2,0),color=(1,.88,.66))
area_emitter((-.15,1.25,2.62),power=190,size=1.1,target=(0,2.0,.4),color=(.88,.94,1))
area_emitter((.1,3.3,2.61),power=140,size=.9,target=(0,3.4,.7),color=(1,.95,.78))
area_emitter((.3,-4.2,2.1),power=95,size=2.5,target=(0,1.5,1.0),color=(1,.90,.76))

# Material finish and economical procedural deck wear; no image textures.
for mat in bpy.data.materials:
    mat.use_nodes=True
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if bs:
        bs.inputs['Roughness'].default_value=.72
for ob in bpy.data.objects:
    if ob.type=='MESH' and ob.parent:
        ancestor=ob.parent
        under_lamp=False
        while ancestor:
            if 'Light face' in ancestor.name:
                under_lamp=True
            ancestor=ancestor.parent
        if under_lamp:
            for slot in ob.material_slots:
                if slot.material:
                    slot.material=slot.material.copy()
                    bs=slot.material.node_tree.nodes.get('Principled BSDF')
                    if bs:
                        bs.inputs['Emission Color'].default_value=(1,.95,.78,1)
                        bs.inputs['Emission Strength'].default_value=3.5
# Subtle rough surface variation across the red painted deck.
for ob in bpy.data.objects:
    if ob.type=='MESH' and ob.parent and ob.parent.name=='Deck':
        for slot in ob.material_slots:
            if slot.material:
                m=slot.material.copy()
                slot.material=m
                nt=m.node_tree
                bs=nt.nodes.get('Principled BSDF')
                tex=nt.nodes.new('ShaderNodeTexNoise')
                tex.inputs['Scale'].default_value=38
                tex.inputs['Detail'].default_value=2
                bump=nt.nodes.new('ShaderNodeBump')
                bump.inputs['Strength'].default_value=.13
                bump.inputs['Distance'].default_value=.018
                nt.links.new(tex.outputs['Fac'],bump.inputs['Height'])
                nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
                bs.inputs['Roughness'].default_value=.39
sc.view_settings.view_transform='AgX'
