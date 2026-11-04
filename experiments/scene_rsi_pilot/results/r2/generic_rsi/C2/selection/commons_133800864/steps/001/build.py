from sceneact import *
import bpy, math

# Visual ledger (normalized image bounds, estimated from the photograph):
# Window/blinds: (0,0)-(.30,.83), behind cabinet and countertop; white slats and frame.
# Cabinet: (.29,0)-(1,.53), cream carcass, recessed door and left side.
# Paper roll: (.60,.045)-(.84,.43), mounted on cabinet front; spindle above/below.
# Towel/ring: (.25,.32)-(.48,.83), ring on cabinet side, cloth hanging in front.
# Counter/backsplash: (0,.72)-(1,1), granite slab supporting all small appliances.
# Pitcher: (.73,.60)-(.97,.85), blue vessel, gray lid, clear loop handle, behind jug.
# Water jug: (.59,.65)-(.79,.89), white body, sloped shoulders, neck/cap, handle.
# Blender: (.48,.57)-(.64,.82), black base beneath transparent upright container.
# Green container: (.42,.68)-(.51,.84), partly hidden by towel.
# Sink/faucet: (0,.69)-(.42,1), dark cropped basin, steel rim, slender upright faucet.
# Small sink accessories: (0,.82)-(.33,.94), cropped soap tray and dark strainer.
# Anchors: window right edge (.29,.35), cabinet corner (.52,.49),
# roll top (.72,.09), roll bottom (.71,.41), towel tip (.36,.82),
# jug cap (.69,.66), pitcher rim (.83,.61), faucet foot (.17,.88).
# Perspective: verticals nearly vertical; counter back edge rises toward the right.
# Camera hypothesis: standing close to sink, looking toward cabinet from its left.
# Geometry uses SceneAct throughout. Shader edits target semantic EMPTY descendants.
# Continuous stone/fabric patterns use an explicit shared semantic coordinate reference.

P = {
    'camera': (-1.48,-2.75,1.99),
    'target': (.05,.38,1.58),
    'lens': 74,
    'counter_z': .86,
    'cream': (.72,.665,.52),
    'trim': (.79,.735,.60),
    'wall': (.73,.70,.60),
    'white': (.86,.845,.76),
    'steel': (.48,.48,.42),
}
scene = Scene('Kitchen corner')

def asset(name):
    a = Asset(name)
    scene.include(name,a)
    return scene.members[name]

def add(a,n,node):
    return a.include(n,node)

def ellipsoid(a,n,c,r,scale,color,opacity=1):
    q=ball(r,center=c,color=color,opacity=opacity)
    q.resize(scale,pivot=c)
    return add(a,n,q)

def tube(a,n,pts,r,color,opacity=1):
    return add(a,n,sweep_tube(points=pts,radius=r,color=color,opacity=opacity))

wall=asset('wall')
add(wall,'back',box((3,.08,3.2),center=(0,.91,1.6),color=P['wall']))

window=asset('window')
add(window,'daylight_glass',box((1.25,.025,2.1),center=(-.65,.845,1.91),color=(.66,.81,.82)))
for x in (-1.29,-.015):
    add(window,'vertical_frame_'+str(x),box((.065,.13,2.23),center=(x,.78,1.91),color=(.83,.84,.76)))
for z in (.81,1.67,2.99):
    add(window,'cross_frame_'+str(z),box((1.3,.12,.055),center=(-.65,.77,z),color=(.84,.85,.78)))
for x in (-.96,-.40):
    add(window,'mullion_'+str(x),box((.026,.06,2.1),center=(x,.79,1.91),color=(.80,.83,.78)))
# Subtle outdoor masses seen through gaps.
for i,(x,z,r) in enumerate([(-1.1,2.3,.16),(-.83,2.58,.15),(-.45,2.19,.2),(-1.04,1.68,.18)]):
    ellipsoid(window,'foliage_'+str(i),(x,.82,z),r,(1,.12,1.5),(.43,.59,.48))
blinds=asset('venetian_blinds')
for i in range(32):
    z=.88+i*.067
    slat=box((1.28,.095,.018),center=(-.66,.682,z),color=(.80,.805,.72))
    slat.turn('x',-10,pivot=(-.66,.682,z))
    add(blinds,'slat_%02d'%i,slat)
for i,x in enumerate((-1.09,-.30)):
    add(blinds,'ladder_'+str(i),box((.012,.012,2.17),center=(x,.621,1.93),color=(.70,.70,.61)))
add(blinds,'bottom_rail',box((1.30,.095,.035),center=(-.66,.68,.84),color=(.77,.78,.69)))
add(blinds,'pull_cord',rod(.003,start=(-.22,.59,2.16),end=(-.22,.59,1.76),color=(.79,.76,.65)))
add(blinds,'pull_weight',rod(.009,length=.055,center=(-.22,.59,1.76),color=(.76,.71,.57)))

cab=asset('upper_cabinet')
add(cab,'carcass',box((1.10,.51,1.55),center=(.54,.635,2.245),color=P['cream']))
# Raised perimeter and inset panel on the front face.
add(cab,'door_field',box((.91,.035,1.43),center=(.57,.359,2.27),color=(.75,.695,.56)))
for x in (.075,1.065):
    add(cab,'door_stile_'+str(x),box((.065,.055,1.52),center=(x,.327,2.245),color=P['trim']))
for z in (1.515,2.975):
    add(cab,'door_rail_'+str(z),box((1.02,.055,.075),center=(.57,.327,z),color=P['trim']))
for x in (.135,1.005):
    add(cab,'panel_bead_'+str(x),box((.018,.016,1.31),center=(x,.332,2.25),color=(.66,.60,.46)))
add(cab,'bottom_edge',box((1.13,.55,.045),center=(.54,.623,1.475),color=(.72,.66,.52)))
add(cab,'knob_stem',rod(.013,start=(.96,.30,1.71),end=(.96,.27,1.71),color=(.39,.34,.23)))
ellipsoid(cab,'door_knob',(.96,.26,1.71),.024,(1,.65,1),(.47,.40,.26))

roll=asset('paper_towel_roll')
add(roll,'paper',rod(.143,length=.565,center=(.61,.173,2.105),color=(.87,.845,.75)))
add(roll,'bottom_core',rod(.033,length=.012,center=(.61,.173,1.817),color=(.47,.40,.29)))
add(roll,'spindle_top',rod(.022,length=.08,center=(.61,.173,2.425),color=P['steel']))
ellipsoid(roll,'finial',(.61,.173,2.475),.031,(.8,.8,1.2),(.43,.43,.36))
add(roll,'under_bracket',rod(.018,start=(.61,.34,1.825),end=(.61,.17,1.825),color=(.26,.25,.20)))
add(roll,'loose_paper_edge',box((.009,.11,.52),center=(.733,.17,2.10),color=(.89,.865,.78)))

ring=asset('towel_ring')
add(ring,'wall_plate',rod(.046,start=(-.025,.57,1.85),end=(-.065,.57,1.85),color=P['steel']))
add(ring,'mount',rod(.019,start=(-.06,.57,1.85),end=(-.11,.57,1.85),color=(.56,.56,.50)))
pts=[(-.12,.57+.108*math.cos(t),1.72+.133*math.sin(t))
     for t in [2*math.pi*i/32 for i in range(33)]]
tube(ring,'ring',pts,.006,(.57,.58,.54))

towel=asset('hanging_towel')
# Filled overlapping cloth folds preserve a broad irregular towel silhouette.
for i,(x,y,z,w,h,ang) in enumerate([
    (-.14,.47,1.315,.21,.55,-8),
    (-.205,.458,1.30,.10,.49,7),
    (-.066,.475,1.33,.085,.52,-13),
    (-.12,.50,1.54,.15,.17,0)]):
    q=box((w,.036,h),center=(x,y,z),color=(.83+i*.009,.80+i*.009,.70+i*.012))
    q.turn('y',ang,pivot=(x,y,z))
    add(towel,'cloth_panel_'+str(i),q)
for i in range(5):
    x=-.224+i*.039
    add(towel,'soft_fold_'+str(i),rod(.013,start=(x,.437,1.07+.015*(i%2)),
         end=(x+.025,.437,1.55),color=(.87,.84,.75)))

counter=asset('granite_counter')
add(counter,'slab',box((2.65,1.22,.075),center=(.03,.155,.8225),color=(.32,.29,.23)))
add(counter,'backsplash',box((2.65,.055,.125),center=(.03,.82,.91),color=(.32,.29,.23)))
add(counter,'left_return',box((.055,1.17,.115),center=(-1.27,.17,.90),color=(.32,.29,.23)))
base=asset('lower_cabinet')
add(base,'front',box((2.6,.08,.8),center=(.03,-.395,.4),color=(.30,.26,.17)))

sink=asset('sink')
# A dark inset and four thick metal edge pieces give a cropped basin with negative space.
add(sink,'dark_basin',box((.66,.57,.20),center=(-.78,-.20,.745),color=(.027,.032,.027)))
add(sink,'basin_bottom',box((.55,.46,.01),center=(-.78,-.20,.655),color=(.055,.067,.059)))
for i,(c,s) in enumerate([
    ((-.78,.102,.86),(.75,.035,.02)),((-.78,-.502,.86),(.75,.035,.02)),
    ((-1.145,-.20,.86),(.028,.60,.02)),((-.415,-.20,.86),(.028,.60,.02))]):
    add(sink,'steel_rim_'+str(i),box(s,center=c,color=(.38,.39,.34)))

faucet=asset('faucet')
add(faucet,'foot',rod(.045,length=.025,center=(-.76,.17,.876),color=P['steel']))
tube(faucet,'spout',[(-.76,.17,.89),(-.76,.17,1.18),(-.76,.16,1.25),
     (-.76,.12,1.28),(-.76,.075,1.26),(-.76,.045,1.22)],.011,(.55,.56,.51))
add(faucet,'valve_base',rod(.025,length=.055,center=(-.86,.16,.90),color=(.45,.46,.40)))
add(faucet,'lever',rod(.009,start=(-.86,.16,.92),end=(-.90,.10,.98),color=(.62,.62,.55)))
accessories=asset('sink_accessories')
add(accessories,'soap_tray',box((.19,.12,.023),center=(-1.09,-.02,.879),color=(.51,.48,.35)))
add(accessories,'soap',box((.13,.075,.026),center=(-1.09,-.025,.902),color=(.76,.72,.54)))
add(accessories,'strainer_outer',rod(.051,length=.025,center=(-.47,.10,.878),color=(.17,.17,.12)))
add(accessories,'strainer_inside',rod(.040,length=.008,center=(-.47,.10,.894),color=(.075,.072,.049)))

tin=asset('green_container')
add(tin,'body',rod(.064,length=.225,center=(.015,.53,.975),color=(.30,.34,.15)))
add(tin,'lid',rod(.068,length=.018,center=(.015,.53,1.095),color=(.52,.50,.32)))
add(tin,'label',box((.063,.004,.13),center=(.015,.465,.98),color=(.56,.56,.37)))

blender=asset('blender')
add(blender,'base',rod(.098,length=.17,center=(.23,.52,.945),color=(.022,.026,.022)))
ellipsoid(blender,'base_shoulders',(.23,.52,1.025),.096,(1,1,.55),(.025,.027,.022))
jar=rod(.060,start=(.23,.52,1.04),end=(.195,.52,1.34),color=(.56,.59,.54),opacity=.24)
add(blender,'clear_jar',jar)
add(blender,'jar_bottom',rod(.063,length=.015,center=(.23,.52,1.055),color=(.18,.20,.17)))
rim=rod(.062,length=.013,center=(.195,.52,1.34),color=(.49,.49,.41))
rim.turn('y',-7)
add(blender,'jar_rim',rim)
add(blender,'control',ball(.014,center=(.20,.425,.947),color=(.27,.28,.22)))

pitcher=asset('blue_filter_pitcher')
# Rounded reservoir, broad lid, spout, and complete side handle.
ellipsoid(pitcher,'reservoir',(.73,.43,1.075),.18,(1,.75,1.06),(.025,.065,.16),.82)
add(pitcher,'middle_body',rod(.165,length=.20,center=(.73,.43,1.065),color=(.025,.06,.145),opacity=.86))
ellipsoid(pitcher,'base',(.73,.43,.898),.149,(1,.80,.20),(.04,.065,.10))
lid=ball(.185,center=(.73,.43,1.257),color=(.40,.40,.34))
lid.resize((1,.79,.17),pivot=(.73,.43,1.257))
lid.turn('y',12,pivot=(.73,.43,1.257))
add(pitcher,'lid',lid)
spout=box((.09,.09,.04),center=(.575,.425,1.278),color=(.33,.34,.29))
spout.turn('y',12)
add(pitcher,'pouring_spout',spout)
tube(pitcher,'clear_handle',[(.87,.45,1.235),(.965,.45,1.20),(1.005,.45,1.10),
     (.99,.45,.99),(.94,.45,.94),(.86,.45,.95)],.021,(.46,.47,.41),.5)

jug=asset('water_jug')
add(jug,'body',fillet_box((.292,.235,.245),radius=.045,center=(.435,.17,.986),color=(.69,.71,.65),opacity=.94))
ellipsoid(jug,'shoulders',(.435,.17,1.102),.145,(1,.80,.88),(.72,.735,.67),.94)
add(jug,'neck',rod(.042,length=.06,center=(.435,.17,1.225),color=(.75,.76,.69)))
add(jug,'cap',rod(.045,length=.027,center=(.435,.17,1.258),color=(.84,.84,.77)))
tube(jug,'handle',[(.50,.17,1.208),(.566,.17,1.17),(.568,.17,1.10),
     (.535,.17,1.065)],.018,(.76,.77,.70))
# Small handwritten FILTER strokes on front, represented as editable rods.
letters={
'F': [[(0,0),(0,1)],[(0,1),(.6,1)],[(0,.55),(.48,.55)]],
'I': [[(.25,0),(.25,1)]],
'L': [[(0,1),(0,0),(.6,0)]],
'T': [[(0,1),(.7,1)],[(.35,1),(.35,0)]],
'E': [[(.6,1),(0,1),(0,0),(.6,0)],[(0,.5),(.5,.5)]],
'R': [[(0,0),(0,1),(.55,1),(.6,.6),(0,.5)],[(.15,.5),(.65,0)]]
}
for i,ch in enumerate('FILTER'):
    for j,line in enumerate(letters[ch]):
        pts=[(.348+i*.026+u*.023,.049,.969+v*.030) for u,v in line]
        tube(jug,'label_%s_%s'%(i,j),pts,.0011,(.31,.33,.28))

# Audit actual expanded source hierarchy.
for name,node in scene.members.items():
    count=sum(n.solid is not None for n in node.traverse())
    print(name,count)
print('whole_scene',sum(n.solid is not None for n in scene.traverse()))
realize(scene)

def meshes(name):
    root=bpy.data.objects.get(name)
    assert root is not None, 'Missing semantic marker '+name
    result=[o for o in root.children_recursive if o.type=='MESH']
    if root.type=='MESH': result.append(root)
    assert result, 'No meshes beneath '+name
    return root,result

def material_for(name,label):
    root,objects=meshes(name)
    m=bpy.data.materials.new(label)
    m.use_nodes=True
    for obj in objects:
        obj.data.materials.clear()
        obj.data.materials.append(m)
    return root,m

root,stone=material_for('granite_counter','fine mottled granite')
nodes=stone.node_tree.nodes
links=stone.node_tree.links
bs=nodes.get('Principled BSDF')
bs.inputs['Roughness'].default_value=.68
tex=nodes.new('ShaderNodeTexCoord'); tex.object=root
noise=nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=155
noise.inputs['Detail'].default_value=2.5
noise.inputs['Roughness'].default_value=.76
links.new(tex.outputs['Object'],noise.inputs['Vector'])
ramp=nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.25
ramp.color_ramp.elements[0].color=(.07,.065,.045,1)
ramp.color_ramp.elements[1].position=.76
ramp.color_ramp.elements[1].color=(.55,.49,.36,1)
e=ramp.color_ramp.elements.new(.51); e.color=(.25,.235,.18,1)
links.new(noise.outputs['Fac'],ramp.inputs[0])
links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
bump=nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.22
bump.inputs['Distance'].default_value=.0015
links.new(noise.outputs['Fac'],bump.inputs['Height'])
links.new(bump.outputs['Normal'],bs.inputs['Normal'])

for name in ('paper_towel_roll','hanging_towel'):
    root,objects=meshes(name)
    for obj in objects:
        if not obj.data.materials: continue
        mat=obj.data.materials[0].copy()
        obj.data.materials[0]=mat
        mat.use_nodes=True
        nd=mat.node_tree.nodes; lk=mat.node_tree.links
        p=nd.get('Principled BSDF')
        p.inputs['Roughness'].default_value=.92
        tc=nd.new('ShaderNodeTexCoord'); tc.object=root
        n=nd.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value=220
        b=nd.new('ShaderNodeBump')
        b.inputs['Strength'].default_value=.14
        b.inputs['Distance'].default_value=.0007
        lk.new(tc.outputs['Object'],n.inputs['Vector'])
        lk.new(n.outputs['Fac'],b.inputs['Height'])
        lk.new(b.outputs['Normal'],p.inputs['Normal'])

for name in ('towel_ring','faucet'):
    _,objects=meshes(name)
    for obj in objects:
        for slot in obj.material_slots:
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
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.72,.75,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.30
set_view(P['camera'],P['target'],lens=P['lens'],sensor=36)
area_emitter((-1.7,.05,2.3),power=190,size=1.7,target=(.4,.4,1.2),color=(.83,.91,1.0))
area_emitter((-.3,-1.6,2.65),power=100,size=2.1,target=(.4,.4,1.6),color=(1.0,.83,.61))
sc.view_settings.view_transform='AgX'
