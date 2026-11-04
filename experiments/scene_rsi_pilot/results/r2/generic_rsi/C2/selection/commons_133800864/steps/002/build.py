from sceneact import *
import bpy, math

# REVISION LEDGER
# Camera residual: step 1 crops the roll/pitcher at right and the sink below.
# Cabinet front corner is near the correct horizontal anchor, but its side is
# too narrow. Increase the view from the left, widen moderately, aim lower.
# Geometry residual: roll is too far along the cabinet front; towel is rigid
# and ribbed; jug shoulders are too spherical. Correct these complete groups.
# Appearance residual: large cream/stone regions are too pale and cool.
# Priority is camera/framing, with coupled silhouette corrections above.
# Preserve anchors approximately: cabinet front corner (.52,.51), towel
# (.35,.65), blender (.56,.70), jug cap (.69,.66), pitcher rim (.83,.61),
# paper center (.72,.25), faucet foot (.17,.88).
#
# Object inventory, normalized reference bounds and support/occlusion:
# window/blinds (0,0)-(.30,.83): behind cabinet, towel, sink fixtures.
# cabinet (.29,0)-(1,.53): side panel, framed front door, bottom, knob.
# roll (.60,.045)-(.84,.43): cabinet mounted cylinder and spindle.
# ring/towel (.25,.32)-(.48,.83): side mounted ring, broad hanging cloth.
# counter/back splash (0,.72)-(1,1): supports appliances and sink fixtures.
# pitcher (.73,.60)-(.97,.85): behind jug, blue body/lid/loop handle.
# jug (.59,.65)-(.79,.89): shoulders, cap, handle, flattened rounded body.
# blender (.48,.57)-(.64,.82): clear tilted cup above black motor.
# green tin (.42,.68)-(.51,.84): behind towel.
# sink/faucet (0,.69)-(.42,1): cropped dark basin, rim and slender spout.
# soap/strainer (0,.82)-(.33,.94): counter supported foreground accessories.
# Vertical architecture is nearly upright. Counter back edge rises to right.

P = dict(camera=(-2.13,-2.30,1.99), target=(.05,.38,1.50), lens=66,
         cream=(.66,.585,.43), trim=(.73,.655,.50),
         wall=(.66,.61,.49), white=(.83,.80,.70),
         steel=(.46,.45,.38))
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
add(window,'glass',box((1.25,.025,2.1),center=(-.65,.845,1.91),color=(.58,.74,.76)))
for i,x in enumerate((-1.29,-.015)):
    add(window,'vertical_frame_'+str(i),box((.065,.13,2.23),center=(x,.78,1.91),color=(.78,.79,.70)))
for i,z in enumerate((.81,1.67,2.99)):
    add(window,'cross_frame_'+str(i),box((1.3,.12,.055),center=(-.65,.77,z),color=(.81,.82,.73)))
for i,x in enumerate((-.96,-.40)):
    add(window,'mullion_'+str(i),box((.026,.06,2.1),center=(x,.79,1.91),color=(.76,.79,.72)))
for i,(x,z,r) in enumerate([(-1.1,2.3,.16),(-.83,2.58,.15),(-.45,2.19,.2),(-1.04,1.68,.18)]):
    ell(window,'foliage_'+str(i),(x,.82,z),r,(1,.12,1.5),(.32,.49,.39))

blinds=asset('venetian_blinds')
for i in range(32):
    z=.88+i*.067
    q=box((1.28,.095,.018),center=(-.66,.682,z),color=(.77,.775,.68))
    q.turn('x',-10,pivot=(-.66,.682,z))
    add(blinds,'slat_%02d'%i,q)
for i,x in enumerate((-1.09,-.30)):
    add(blinds,'ladder_'+str(i),box((.012,.012,2.17),center=(x,.621,1.93),color=(.68,.68,.58)))
add(blinds,'bottom_rail',box((1.30,.095,.035),center=(-.66,.68,.84),color=(.74,.75,.65)))
add(blinds,'pull_cord',rod(.003,start=(-.22,.59,2.16),end=(-.22,.59,1.76),color=(.75,.72,.61)))
add(blinds,'pull_weight',rod(.009,length=.055,center=(-.22,.59,1.76),color=(.73,.68,.54)))

cab=asset('upper_cabinet')
add(cab,'carcass',box((1.10,.51,1.55),center=(.54,.635,2.245),color=P['cream']))
add(cab,'door_field',box((.91,.035,1.43),center=(.57,.359,2.27),color=(.69,.615,.46)))
for i,x in enumerate((.075,1.065)):
    add(cab,'door_stile_'+str(i),box((.065,.055,1.52),center=(x,.327,2.245),color=P['trim']))
for i,z in enumerate((1.515,2.975)):
    add(cab,'door_rail_'+str(i),box((1.02,.055,.075),center=(.57,.327,z),color=P['trim']))
for i,x in enumerate((.135,1.005)):
    add(cab,'panel_bead_'+str(i),box((.018,.016,1.31),center=(x,.332,2.25),color=(.60,.53,.38)))
add(cab,'bottom_edge',box((1.13,.55,.045),center=(.54,.623,1.475),color=(.67,.60,.45)))
add(cab,'knob_stem',rod(.013,start=(.96,.30,1.71),end=(.96,.27,1.71),color=(.36,.30,.19)))
ell(cab,'door_knob',(.96,.26,1.71),.024,(1,.65,1),(.43,.36,.22))

roll=asset('paper_towel_roll')
add(roll,'paper',rod(.143,length=.565,center=(.47,.173,2.105),color=(.83,.79,.68)))
add(roll,'bottom_core',rod(.033,length=.012,center=(.47,.173,1.817),color=(.42,.35,.24)))
add(roll,'spindle_top',rod(.022,length=.08,center=(.47,.173,2.425),color=P['steel']))
ell(roll,'finial',(.47,.173,2.475),.031,(.8,.8,1.2),(.40,.39,.31))
add(roll,'under_bracket',rod(.018,start=(.47,.34,1.825),end=(.47,.17,1.825),color=(.23,.22,.16)))
add(roll,'paper_edge',box((.008,.11,.52),center=(.593,.17,2.10),color=(.85,.81,.71)))

ring=asset('towel_ring')
add(ring,'wall_plate',rod(.046,start=(-.025,.57,1.85),end=(-.065,.57,1.85),color=P['steel']))
add(ring,'mount',rod(.019,start=(-.06,.57,1.85),end=(-.11,.57,1.85),color=(.52,.51,.44)))
tube(ring,'ring',[(-.12,.57+.108*math.cos(t),1.72+.133*math.sin(t))
    for t in [2*math.pi*i/28 for i in range(29)]],.006,(.53,.54,.48))

towel=asset('hanging_towel')
# Overlapping thin filled panels with small, uneven folds.
for i,(x,y,z,w,h,ang) in enumerate([
    (-.14,.47,1.315,.175,.55,-7),
    (-.205,.458,1.325,.085,.46,9),
    (-.064,.482,1.35,.075,.49,-14),
    (-.115,.50,1.55,.15,.15,0)]):
    q=box((w,.026,h),center=(x,y,z),color=(.79+i*.012,.75+i*.012,.64+i*.013))
    q.turn('y',ang,pivot=(x,y,z))
    add(towel,'cloth_panel_'+str(i),q)
for i in range(4):
    x=-.205+i*.041
    ell(towel,'fold_'+str(i),(x,.449,1.32),.025,(.43,.40,9.5),(.82,.78,.68))
# A shorter rear tail lies behind the main drape.
q=box((.13,.025,.31),center=(-.075,.545,1.39),color=(.75,.71,.60))
q.turn('y',-22,pivot=(-.075,.545,1.39))
add(towel,'rear_tail',q)

counter=asset('granite_counter')
add(counter,'slab',box((2.65,1.22,.075),center=(.03,.155,.8225),color=(.28,.25,.19)))
add(counter,'backsplash',box((2.65,.055,.125),center=(.03,.82,.91),color=(.28,.25,.19)))
add(counter,'left_return',box((.055,1.17,.115),center=(-1.27,.17,.90),color=(.28,.25,.19)))
base=asset('lower_cabinet')
add(base,'front',box((2.6,.08,.8),center=(.03,-.395,.4),color=(.28,.23,.14)))

sink=asset('sink')
add(sink,'dark_basin',box((.66,.57,.20),center=(-.78,-.20,.745),color=(.018,.024,.020)))
add(sink,'basin_bottom',box((.55,.46,.01),center=(-.78,-.20,.655),color=(.04,.052,.044)))
for i,(c,s) in enumerate([
    ((-.78,.102,.86),(.75,.035,.02)),((-.78,-.502,.86),(.75,.035,.02)),
    ((-1.145,-.20,.86),(.028,.60,.02)),((-.415,-.20,.86),(.028,.60,.02))]):
    add(sink,'steel_rim_'+str(i),box(s,center=c,color=(.34,.35,.29)))

faucet=asset('faucet')
add(faucet,'foot',rod(.045,length=.025,center=(-.76,.17,.876),color=P['steel']))
tube(faucet,'spout',[(-.76,.17,.89),(-.76,.17,1.18),(-.76,.16,1.25),
    (-.76,.12,1.28),(-.76,.075,1.26),(-.76,.045,1.22)],.011,(.51,.52,.46))
add(faucet,'valve_base',rod(.025,length=.055,center=(-.86,.16,.90),color=(.41,.42,.35)))
add(faucet,'lever',rod(.009,start=(-.86,.16,.92),end=(-.90,.10,.98),color=(.58,.58,.50)))

accessories=asset('sink_accessories')
add(accessories,'soap_tray',box((.19,.12,.023),center=(-1.09,-.02,.879),color=(.47,.44,.31)))
add(accessories,'soap',box((.13,.075,.026),center=(-1.09,-.025,.902),color=(.72,.68,.49)))
add(accessories,'strainer_outer',rod(.051,length=.025,center=(-.47,.10,.878),color=(.14,.14,.09)))
add(accessories,'strainer_inside',rod(.040,length=.008,center=(-.47,.10,.894),color=(.055,.052,.032)))

tin=asset('green_container')
add(tin,'body',rod(.064,length=.225,center=(.015,.53,.975),color=(.25,.29,.11)))
add(tin,'lid',rod(.068,length=.018,center=(.015,.53,1.095),color=(.46,.44,.26)))
add(tin,'label',box((.063,.004,.13),center=(.015,.465,.98),color=(.50,.50,.31)))

blender=asset('blender')
add(blender,'base',rod(.098,length=.17,center=(.23,.52,.945),color=(.014,.018,.014)))
ell(blender,'base_shoulders',(.23,.52,1.025),.096,(1,1,.55),(.018,.020,.015))
add(blender,'clear_jar',rod(.060,start=(.23,.52,1.04),end=(.195,.52,1.34),color=(.49,.52,.47),opacity=.20))
add(blender,'jar_bottom',rod(.063,length=.015,center=(.23,.52,1.055),color=(.14,.16,.13)))
q=rod(.062,length=.013,center=(.195,.52,1.34),color=(.44,.44,.36))
q.turn('y',-7)
add(blender,'jar_rim',q)
add(blender,'control',ball(.014,center=(.20,.425,.947),color=(.23,.24,.18)))

pitcher=asset('blue_filter_pitcher')
ell(pitcher,'reservoir',(.73,.43,1.075),.18,(1,.75,1.06),(.018,.045,.12),.88)
add(pitcher,'middle_body',rod(.165,length=.20,center=(.73,.43,1.065),color=(.018,.042,.115),opacity=.90))
ell(pitcher,'base',(.73,.43,.898),.149,(1,.80,.20),(.025,.045,.075))
q=ball(.185,center=(.73,.43,1.257),color=(.35,.35,.29))
q.resize((1,.79,.17),pivot=(.73,.43,1.257))
q.turn('y',12,pivot=(.73,.43,1.257))
add(pitcher,'lid',q)
q=box((.09,.09,.04),center=(.575,.425,1.278),color=(.29,.30,.24))
q.turn('y',12)
add(pitcher,'pouring_spout',q)
tube(pitcher,'clear_handle',[(.87,.45,1.235),(.965,.45,1.20),(1.005,.45,1.10),
    (.99,.45,.99),(.94,.45,.94),(.86,.45,.95)],.021,(.41,.42,.35),.5)

jug=asset('water_jug')
add(jug,'body',fillet_box((.292,.235,.245),radius=.045,center=(.435,.17,.986),color=(.64,.66,.59)))
# Narrower upper shoulder blends into the main body's top instead of a ball bulge.
ell(jug,'shoulders',(.435,.17,1.102),.134,(1,.82,.82),(.67,.69,.61))
add(jug,'neck',rod(.039,length=.06,center=(.435,.17,1.215),color=(.71,.72,.64)))
add(jug,'cap',rod(.042,length=.027,center=(.435,.17,1.248),color=(.79,.79,.71)))
tube(jug,'handle',[(.50,.17,1.198),(.566,.17,1.16),(.568,.17,1.09),
    (.535,.17,1.055)],.017,(.70,.72,.64))
letters={
'F':[[(0,0),(0,1)],[(0,1),(.6,1)],[(0,.55),(.48,.55)]],
'I':[[ (.25,0),(.25,1)]],
'L':[[(0,1),(0,0),(.6,0)]],
'T':[[(0,1),(.7,1)],[(.35,1),(.35,0)]],
'E':[[ (.6,1),(0,1),(0,0),(.6,0)],[(0,.5),(.5,.5)]],
'R':[[(0,0),(0,1),(.55,1),(.6,.6),(0,.5)],[(.15,.5),(.65,0)]]}
for i,ch in enumerate('FILTER'):
    for j,line in enumerate(letters[ch]):
        tube(jug,'label_%d_%d'%(i,j),
             [(.348+i*.026+u*.023,.049,.969+v*.030) for u,v in line],
             .0011,(.27,.29,.23))

# Semantic audit: all ledger objects retained, complete assemblies attached.
expected={'wall','window','venetian_blinds','upper_cabinet','paper_towel_roll',
'towel_ring','hanging_towel','granite_counter','lower_cabinet','sink','faucet',
'sink_accessories','green_container','blender','blue_filter_pitcher','water_jug'}
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
    if root.type=='MESH': obs.append(root)
    assert obs,name
    return root,obs

root,obs=meshes('granite_counter')
stone=bpy.data.materials.new('warm fine granite')
stone.use_nodes=True
for o in obs:
    o.data.materials.clear()
    o.data.materials.append(stone)
nd=stone.node_tree.nodes
lk=stone.node_tree.links
bs=nd.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.64
tc=nd.new('ShaderNodeTexCoord'); tc.object=root
noise=nd.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=185
noise.inputs['Detail'].default_value=2.5
noise.inputs['Roughness'].default_value=.76
lk.new(tc.outputs['Object'],noise.inputs['Vector'])
ramp=nd.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.25
ramp.color_ramp.elements[0].color=(.045,.039,.026,1)
ramp.color_ramp.elements[1].position=.76
ramp.color_ramp.elements[1].color=(.40,.34,.23,1)
e=ramp.color_ramp.elements.new(.51); e.color=(.18,.16,.11,1)
lk.new(noise.outputs['Fac'],ramp.inputs[0])
lk.new(ramp.outputs['Color'],bs.inputs['Base Color'])
b=nd.new('ShaderNodeBump')
b.inputs['Strength'].default_value=.20
b.inputs['Distance'].default_value=.0012
lk.new(noise.outputs['Fac'],b.inputs['Height'])
lk.new(b.outputs['Normal'],bs.inputs['Normal'])

for name in ('paper_towel_roll','hanging_towel'):
    root,obs=meshes(name)
    for o in obs:
        if not o.data.materials: continue
        m=o.data.materials[0].copy()
        o.data.materials[0]=m
        m.use_nodes=True
        nd=m.node_tree.nodes; lk=m.node_tree.links
        p=nd.get('Principled BSDF')
        p.inputs['Roughness'].default_value=.94
        tc=nd.new('ShaderNodeTexCoord'); tc.object=root
        n=nd.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=220
        b=nd.new('ShaderNodeBump')
        b.inputs['Strength'].default_value=.13
        b.inputs['Distance'].default_value=.0007
        lk.new(tc.outputs['Object'],n.inputs['Vector'])
        lk.new(n.outputs['Fac'],b.inputs['Height'])
        lk.new(b.outputs['Normal'],p.inputs['Normal'])

for name in ('towel_ring','faucet'):
    _,obs=meshes(name)
    for o in obs:
        for slot in o.material_slots:
            if slot.material:
                m=slot.material.copy(); slot.material=m
                m.use_nodes=True
                p=m.node_tree.nodes.get('Principled BSDF')
                p.inputs['Metallic'].default_value=.78
                p.inputs['Roughness'].default_value=.24

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.69,.66,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.24
set_view(P['camera'],P['target'],lens=P['lens'],sensor=36)
area_emitter((-1.7,.05,2.3),power=170,size=1.7,
             target=(.4,.4,1.2),color=(.88,.94,1.0))
area_emitter((-.3,-1.6,2.65),power=75,size=2.1,
             target=(.4,.4,1.6),color=(1.0,.83,.61))
sc.view_settings.view_transform='AgX'
