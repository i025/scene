from sceneact import *
import bpy, math

# REVISION LEDGER
# Camera: step 2 cabinet side spans about x=.41-.55, versus .29-.52
# in the reference. Its front is too wide; receding edges are too shallow.
# Priority: correct architecture and perspective together, preserving the
# cabinet's lower front corner. Camera moves higher and farther left.
# Geometry: towel is too short and has rigid cylindrical ribs; jug and
# pitcher need independent depth placement. Sink basin was hidden by slab.
# Appearance: cream surfaces and granite are too bright; window light needs
# stronger directionality. Use warmer cabinet finishes and darker stone.
# Preserve reference anchors: cabinet corner (.52,.53), ring (.35,.41),
# towel hem (.39,.82), roll (.72,.25), blender (.56,.70),
# jug cap (.69,.66), pitcher lid (.83,.62), faucet foot (.17,.88).
#
# Object ledger / estimated reference bounds / support and occlusion:
# window and blinds: (0,0)-(.30,.83), behind cabinet and hanging towel.
# upper cabinet: (.29,0)-(1,.53), filled side, framed door, bottom, knob.
# paper roll: (.60,.045)-(.84,.43), spindle mounted to cabinet front.
# towel ring: (.29,.32)-(.46,.51), mounted on cabinet side.
# towel: (.25,.48)-(.48,.83), folded over ring, conceals green tin.
# counter and backsplash: (0,.72)-(1,1), support all small appliances.
# green tin: (.42,.68)-(.51,.84), behind towel.
# blender: (.48,.57)-(.64,.82), tilted clear cup over dark motor.
# filter pitcher: (.73,.60)-(.97,.85), blue body, broad lid, clear handle.
# jug: (.59,.65)-(.79,.89), in front of pitcher, neck, shoulders, handle.
# sink: (0,.85)-(.43,1), cropped open dark basin and metal rim.
# faucet: (.11,.69)-(.24,.90), slender bent spout and valve.
# soap and strainer: (0,.82)-(.33,.94), supported by counter.
# Architecture verticals nearly upright; cabinet side bottom descends right,
# door bottom rises right. Counter foreground and sink are cropped.

P = dict(
    camera=(-2.50,-2.15,2.405), target=(.10,.38,1.525), lens=66,
    cream=(.49,.40,.27), trim=(.59,.49,.33),
    wall=(.59,.51,.38), paper=(.72,.65,.52),
    steel=(.46,.45,.38),
    window_power=145, fill_power=48, ambient=.17
)
scene=Scene('Kitchen corner')

def asset(name):
    scene.include(name,Asset(name))
    return scene.members[name]

def add(a,name,node):
    return a.include(name,node)

def ell(a,name,c,r,scale,color,opacity=1):
    q=ball(r,center=c,color=color,opacity=opacity)
    q.resize(scale,pivot=c)
    return add(a,name,q)

def tube(a,name,pts,r,color,opacity=1):
    return add(a,name,sweep_tube(points=pts,radius=r,color=color,opacity=opacity))

wall=asset('wall')
add(wall,'back',box((3,.08,3.2),center=(0,.91,1.6),color=P['wall']))

window=asset('window')
add(window,'glass',box((1.25,.025,2.1),center=(-.65,.845,1.91),color=(.49,.66,.69)))
for i,x in enumerate((-1.29,-.015)):
    add(window,'vertical_frame_'+str(i),
        box((.065,.13,2.23),center=(x,.78,1.91),color=(.73,.74,.66)))
for i,z in enumerate((.81,1.67,2.99)):
    add(window,'cross_frame_'+str(i),
        box((1.3,.12,.055),center=(-.65,.77,z),color=(.77,.78,.69)))
for i,x in enumerate((-.96,-.40)):
    add(window,'mullion_'+str(i),
        box((.026,.06,2.1),center=(x,.79,1.91),color=(.71,.74,.67)))
for i,(x,z,r) in enumerate([
    (-1.1,2.3,.16),(-.83,2.58,.15),(-.45,2.19,.2),(-1.04,1.68,.18)
]):
    ell(window,'foliage_'+str(i),(x,.82,z),r,(1,.12,1.5),(.25,.41,.32))

blinds=asset('venetian_blinds')
for i in range(32):
    z=.88+i*.067
    q=box((1.28,.095,.018),center=(-.66,.682,z),color=(.72,.73,.65))
    q.turn('x',-10,pivot=(-.66,.682,z))
    add(blinds,'slat_%02d'%i,q)
for i,x in enumerate((-1.09,-.30)):
    add(blinds,'ladder_'+str(i),
        box((.012,.012,2.17),center=(x,.621,1.93),color=(.64,.64,.55)))
add(blinds,'bottom_rail',
    box((1.30,.095,.035),center=(-.66,.68,.84),color=(.70,.71,.62)))
add(blinds,'pull_cord',
    rod(.003,start=(-.22,.59,2.16),end=(-.22,.59,1.76),color=(.73,.70,.59)))
add(blinds,'pull_weight',
    rod(.009,length=.055,center=(-.22,.59,1.76),color=(.70,.65,.51)))

cab=asset('upper_cabinet')
add(cab,'carcass',
    box((.76,.61,1.55),center=(.37,.555,2.245),color=P['cream']))
add(cab,'door_field',
    box((.65,.035,1.43),center=(.37,.2325,2.27),color=(.52,.43,.29)))
for i,x in enumerate((.018,.722)):
    add(cab,'door_stile_'+str(i),
        box((.062,.055,1.52),center=(x,.205,2.245),color=P['trim']))
for i,z in enumerate((1.515,2.975)):
    add(cab,'door_rail_'+str(i),
        box((.765,.055,.075),center=(.37,.205,z),color=P['trim']))
for i,x in enumerate((.073,.667)):
    add(cab,'panel_bead_'+str(i),
        box((.014,.015,1.31),center=(x,.213,2.25),color=(.43,.35,.22)))
add(cab,'bottom_edge',
    box((.79,.64,.045),center=(.37,.55,1.475),color=(.53,.44,.29)))
add(cab,'knob_stem',
    rod(.013,start=(.68,.175,1.71),end=(.68,.145,1.71),color=(.30,.25,.15)))
ell(cab,'door_knob',(.68,.135,1.71),.024,(1,.65,1),(.39,.32,.19))

roll=asset('paper_towel_roll')
rc=(.365,.075,1.985)
add(roll,'paper',rod(.153,length=.60,center=rc,color=P['paper']))
add(roll,'bottom_core',
    rod(.033,length=.012,center=(rc[0],rc[1],1.679),color=(.34,.28,.18)))
add(roll,'spindle_top',
    rod(.022,length=.075,center=(rc[0],rc[1],2.317),color=P['steel']))
ell(roll,'finial',(rc[0],rc[1],2.364),.031,(.8,.8,1.2),(.36,.35,.27))
add(roll,'under_bracket',
    rod(.018,start=(rc[0],.23,1.69),end=(rc[0],.075,1.69),color=(.20,.19,.13)))
add(roll,'paper_edge',
    box((.007,.11,.555),center=(rc[0]+.141,.075,1.985),color=(.75,.68,.55)))
# Keep the complete roll aligned to the revised, shallower cabinet front.
roll.move((-.035,.115,0))

ring=asset('towel_ring')
add(ring,'wall_plate',
    rod(.046,start=(-.025,.45,1.85),end=(-.065,.45,1.85),color=P['steel']))
add(ring,'mount',
    rod(.019,start=(-.06,.45,1.85),end=(-.11,.45,1.85),color=(.48,.47,.39)))
tube(ring,'ring',[
    (-.12,.45+.108*math.cos(t),1.72+.133*math.sin(t))
    for t in [2*math.pi*i/24 for i in range(25)]
],.006,(.48,.49,.42))

towel=asset('hanging_towel')
# Broad filled folds, with uneven hems and changing fold depth.
# Small rotations and flat, overlapping surfaces avoid the previous ribbed look.
for i,(x,y,z,w,h,angle,col) in enumerate([
    (-.158,.466,1.247,.145,.675,-5,(.75,.70,.60)),
    (-.229,.459,1.275,.087,.588,7,(.70,.65,.55)),
    (-.081,.474,1.280,.087,.630,-10,(.78,.73,.63)),
    (-.135,.445,1.488,.155,.190,3,(.79,.74,.64)),
    (-.182,.441,1.275,.055,.535,-3,(.78,.73,.63)),
    (-.105,.447,1.195,.048,.480,-8,(.73,.68,.58))
]):
    q=box((w,.014,h),center=(x,y,z),color=col)
    q.turn('y',angle,pivot=(x,y,z))
    add(towel,'cloth_fold_'+str(i),q)
q=box((.13,.018,.36),center=(-.065,.535,1.36),color=(.69,.64,.54))
q.turn('y',-23,pivot=(-.065,.535,1.36))
add(towel,'short_rear_tail',q)
ell(towel,'fold_over_ring',(-.14,.46,1.578),.047,(1.55,.65,.55),(.77,.72,.62))

counter=asset('granite_counter')
# Open the slab so the basin is visible through it.
sink_center=(-.56,.02)
slab=box((2.65,1.22,.075),center=(.03,.155,.8225),color=(.22,.19,.14))
opening=box((.665,.575,.32),center=(sink_center[0],sink_center[1],.82))
add(counter,'slab',subtract(slab,opening))
add(counter,'backsplash',
    box((2.65,.055,.125),center=(.03,.82,.91),color=(.22,.19,.14)))
add(counter,'left_return',
    box((.055,1.17,.115),center=(-1.27,.17,.90),color=(.22,.19,.14)))

base=asset('lower_cabinet')
add(base,'front',
    box((2.6,.08,.8),center=(.03,-.395,.4),color=(.25,.20,.12)))

sink=asset('sink')
sx,sy=sink_center
add(sink,'basin_bottom',
    box((.66,.57,.022),center=(sx,sy,.652),color=(.018,.024,.020)))
for i,(c,s) in enumerate([
    ((sx,sy+.283,.754),(.66,.018,.20)),
    ((sx,sy-.283,.754),(.66,.018,.20)),
    ((sx-.323,sy,.754),(.018,.57,.20)),
    ((sx+.323,sy,.754),(.018,.57,.20))
]):
    add(sink,'basin_wall_'+str(i),box(s,center=c,color=(.027,.033,.027)))
for i,(c,s) in enumerate([
    ((sx,sy+.302,.866),(.75,.035,.018)),
    ((sx,sy-.302,.866),(.75,.035,.018)),
    ((sx-.365,sy,.866),(.028,.60,.018)),
    ((sx+.365,sy,.866),(.028,.60,.018))
]):
    add(sink,'steel_rim_'+str(i),box(s,center=c,color=(.32,.33,.27)))

faucet=asset('faucet')
add(faucet,'foot',
    rod(.045,length=.025,center=(-.76,.17,.876),color=P['steel']))
tube(faucet,'spout',[
    (-.76,.17,.89),(-.76,.17,1.18),(-.76,.16,1.25),
    (-.76,.12,1.28),(-.76,.075,1.26),(-.76,.045,1.22)
],.011,(.49,.50,.43))
add(faucet,'valve_base',
    rod(.025,length=.055,center=(-.86,.16,.90),color=(.38,.39,.32)))
add(faucet,'lever',
    rod(.009,start=(-.86,.16,.92),end=(-.90,.10,.98),color=(.55,.55,.47)))
faucet.move((.20,.20,0))

accessories=asset('sink_accessories')
add(accessories,'soap_tray',
    box((.19,.12,.023),center=(-1.09,-.02,.879),color=(.42,.39,.26)))
add(accessories,'soap',
    box((.13,.075,.026),center=(-1.09,-.025,.902),color=(.71,.66,.47)))
add(accessories,'strainer_outer',
    rod(.051,length=.025,center=(-.47,.10,.878),color=(.12,.12,.075)))
add(accessories,'strainer_inside',
    rod(.040,length=.008,center=(-.47,.10,.894),color=(.045,.042,.025)))
accessories.move((.20,.20,0))

tin=asset('green_container')
add(tin,'body',
    rod(.064,length=.225,center=(.015,.53,.975),color=(.24,.27,.095)))
add(tin,'lid',
    rod(.068,length=.018,center=(.015,.53,1.095),color=(.42,.40,.22)))
add(tin,'label',
    box((.063,.004,.13),center=(.015,.465,.98),color=(.45,.45,.27)))
tin.move((-.13,-.23,0))

blender=asset('blender')
add(blender,'base',
    rod(.098,length=.20,center=(.23,.52,.96),color=(.012,.016,.012)))
ell(blender,'base_shoulders',(.23,.52,1.055),.096,(1,1,.46),(.016,.018,.013))
add(blender,'clear_jar',
    rod(.060,start=(.23,.52,1.065),end=(.195,.52,1.36),
        color=(.38,.41,.36),opacity=.19))
add(blender,'jar_bottom',
    rod(.063,length=.015,center=(.23,.52,1.073),color=(.11,.13,.10)))
q=rod(.062,length=.013,center=(.195,.52,1.36),color=(.37,.37,.29))
q.turn('y',-7)
add(blender,'jar_rim',q)
add(blender,'control',
    ball(.014,center=(.20,.425,.96),color=(.18,.19,.14)))
blender.move((-.16,-.29,0))

pitcher=asset('blue_filter_pitcher')
ell(pitcher,'reservoir',(.73,.43,1.075),.18,(1,.75,1.06),(.013,.031,.093),.88)
add(pitcher,'middle_body',
    rod(.165,length=.20,center=(.73,.43,1.065),
        color=(.013,.030,.090),opacity=.90))
ell(pitcher,'base',(.73,.43,.898),.149,(1,.80,.20),(.018,.031,.055))
q=ball(.185,center=(.73,.43,1.257),color=(.31,.31,.25))
q.resize((1,.79,.17),pivot=(.73,.43,1.257))
q.turn('y',12,pivot=(.73,.43,1.257))
add(pitcher,'lid',q)
q=box((.09,.09,.04),center=(.575,.425,1.278),color=(.25,.26,.20))
q.turn('y',12)
add(pitcher,'pouring_spout',q)
tube(pitcher,'clear_handle',[
    (.87,.45,1.235),(.965,.45,1.20),(1.005,.45,1.10),
    (.99,.45,.99),(.94,.45,.94),(.86,.45,.95)
],.021,(.37,.38,.31),.48)
pitcher.resize((.90,.90,1.15),pivot=(.73,.43,.86))
pitcher.move((-.43,-.57,0))

jug=asset('water_jug')
add(jug,'body',
    fillet_box((.292,.235,.245),radius=.045,
               center=(.435,.17,.986),color=(.59,.61,.54)))
ell(jug,'shoulders',(.435,.17,1.102),.134,(1,.82,.82),(.62,.64,.56))
add(jug,'neck',
    rod(.039,length=.06,center=(.435,.17,1.215),color=(.66,.67,.59)))
add(jug,'cap',
    rod(.042,length=.027,center=(.435,.17,1.248),color=(.74,.74,.66)))
tube(jug,'handle',[
    (.50,.17,1.198),(.566,.17,1.16),(.568,.17,1.09),(.535,.17,1.055)
],.017,(.65,.67,.59))
letters={
    'F':[[(0,0),(0,1)],[(0,1),(.6,1)],[(0,.55),(.48,.55)]],
    'I':[[ (.25,0),(.25,1)]],
    'L':[[(0,1),(0,0),(.6,0)]],
    'T':[[(0,1),(.7,1)],[(.35,1),(.35,0)]],
    'E':[[ (.6,1),(0,1),(0,0),(.6,0)],[(0,.5),(.5,.5)]],
    'R':[[(0,0),(0,1),(.55,1),(.6,.6),(0,.5)],[(.15,.5),(.65,0)]]
}
for i,ch in enumerate('FILTER'):
    for j,line in enumerate(letters[ch]):
        tube(jug,'label_%d_%d'%(i,j),[
            (.348+i*.026+u*.023,.049,.969+v*.030) for u,v in line
        ],.0011,(.24,.26,.20))
jug.move((-.36,-.20,0))

# Audit complete semantic objects, including all supports and cropped objects.
expected={
    'wall','window','venetian_blinds','upper_cabinet','paper_towel_roll',
    'towel_ring','hanging_towel','granite_counter','lower_cabinet','sink',
    'faucet','sink_accessories','green_container','blender',
    'blue_filter_pitcher','water_jug'
}
assert expected==set(scene.members)
for name,node in scene.members.items():
    count=sum(n.solid is not None for n in node.traverse())
    assert count>0
    print(name,count)
print('whole_scene',sum(n.solid is not None for n in scene.traverse()))

realize(scene)

def meshes(name):
    root=bpy.data.objects.get(name)
    assert root is not None,name
    obs=[o for o in root.children_recursive if o.type=='MESH']
    if root.type=='MESH':
        obs.append(root)
    assert obs,name
    return root,obs

root,obs=meshes('granite_counter')
stone=bpy.data.materials.new('fine brown speckled granite')
stone.use_nodes=True
for o in obs:
    o.data.materials.clear()
    o.data.materials.append(stone)
nd=stone.node_tree.nodes
lk=stone.node_tree.links
bs=nd.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.58
tc=nd.new('ShaderNodeTexCoord')
tc.object=root
noise=nd.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=205
noise.inputs['Detail'].default_value=2.5
noise.inputs['Roughness'].default_value=.78
lk.new(tc.outputs['Object'],noise.inputs['Vector'])
ramp=nd.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.27
ramp.color_ramp.elements[0].color=(.025,.022,.016,1)
ramp.color_ramp.elements[1].position=.75
ramp.color_ramp.elements[1].color=(.29,.24,.16,1)
e=ramp.color_ramp.elements.new(.51)
e.color=(.105,.088,.060,1)
lk.new(noise.outputs['Fac'],ramp.inputs[0])
lk.new(ramp.outputs['Color'],bs.inputs['Base Color'])
b=nd.new('ShaderNodeBump')
b.inputs['Strength'].default_value=.18
b.inputs['Distance'].default_value=.001
lk.new(noise.outputs['Fac'],b.inputs['Height'])
lk.new(b.outputs['Normal'],bs.inputs['Normal'])

for name in ('paper_towel_roll','hanging_towel'):
    root,obs=meshes(name)
    for o in obs:
        if not o.data.materials:
            continue
        m=o.data.materials[0].copy()
        o.data.materials[0]=m
        m.use_nodes=True
        nd=m.node_tree.nodes
        lk=m.node_tree.links
        p=nd.get('Principled BSDF')
        p.inputs['Roughness'].default_value=.94
        tc=nd.new('ShaderNodeTexCoord')
        tc.object=root
        n=nd.new('ShaderNodeTexNoise')
        n.inputs['Scale'].default_value=240
        bump=nd.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value=.15
        bump.inputs['Distance'].default_value=.0007
        lk.new(tc.outputs['Object'],n.inputs['Vector'])
        lk.new(n.outputs['Fac'],bump.inputs['Height'])
        lk.new(bump.outputs['Normal'],p.inputs['Normal'])

for name in ('towel_ring','faucet','sink'):
    _,obs=meshes(name)
    for o in obs:
        for slot in o.material_slots:
            if slot.material:
                m=slot.material.copy()
                slot.material=m
                m.use_nodes=True
                p=m.node_tree.nodes.get('Principled BSDF')
                p.inputs['Metallic'].default_value=.78
                p.inputs['Roughness'].default_value=.26

# Local plastic finishes are copied so shared colors remain independent.
for name in ('water_jug','blue_filter_pitcher','blender'):
    _,obs=meshes(name)
    for o in obs:
        for slot in o.material_slots:
            if slot.material:
                m=slot.material.copy()
                slot.material=m
                m.use_nodes=True
                p=m.node_tree.nodes.get('Principled BSDF')
                p.inputs['Roughness'].default_value=.36 if name!='water_jug' else .55

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.66,.65,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=P['ambient']
set_view(P['camera'],P['target'],lens=P['lens'],sensor=36)
area_emitter((-1.45,.48,2.35),power=P['window_power'],size=1.25,
             target=(.25,.20,1.25),color=(.90,.95,1.0))
area_emitter((-.3,-1.6,2.65),power=P['fill_power'],size=2.1,
             target=(.35,.35,1.6),color=(1.0,.82,.59))
sc.view_settings.view_transform='AgX'
