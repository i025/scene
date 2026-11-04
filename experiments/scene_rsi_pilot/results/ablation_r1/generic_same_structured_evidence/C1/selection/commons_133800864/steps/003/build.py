from sceneact import *
import bpy, math, random

# Reference anchors: cabinet side/front corner (.53,.52), window edge (.29,.74),
# roll (.61,.09)-(.82,.42), towel (.26,.48)-(.46,.83), jug (.59,.65)-(.79,.89).
# Review 2: cabinet bottom was nearly horizontal and its side too narrow.
# Increase camera elevation and lateral angle; deepen the cabinet behind its front.
# Foreground sink was a small flat plate and the counter edge entered the frame:
# enlarge and recess the basin, extending the counter toward the camera.
# Towel started too high and was too straight; lower its gathered top and vary its hem.
CAMERA = (-1.48, -2.70, 2.48)
TARGET = (-.06, .27, 1.64)
LENS = 48
COUNTER_Z = .88
CABINET_DEPTH = .72
KEY_POWER = 115
FILL_POWER = 35

scene = Scene('Kitchen corner')
cream=(.70,.62,.47)
ivory=(.80,.74,.60)
white=(.89,.88,.77)
steel=(.46,.45,.38)

def add(parent,key,node):
    return parent.include(key,node)

def tube(parent,key,pts,radius,color):
    clean=[p for i,p in enumerate(pts) if i==0 or p!=pts[i-1]]
    return add(parent,key,sweep_tube(points=clean,radius=radius,color=color))

architecture=Asset('Walls and counter')
add(architecture,'back_wall',box((3,.10,3.4),center=(0,1.0,1.6),color=cream))
counter=box((3.2,2.4,.065),center=(-.20,-.30,.8475),color=(.31,.29,.22))
cut=box((.81,.68,.24),center=(-.97,-.43,.87))
add(architecture,'counter',subtract(counter,cut))
add(architecture,'backsplash',box((3.2,.035,.16),center=(-.20,.875,.96),color=(.34,.32,.25)))
scene.include('architecture',architecture)

cab=Asset('Painted upper cabinet')
add(cab,'carcass',box((.95,CABINET_DEPTH,1.55),
    center=(.28,.19+CABINET_DEPTH/2,2.395),color=ivory))
add(cab,'door_panel',box((.84,.033,1.42),center=(.31,.173,2.41),color=(.77,.70,.55)))
for key,x,z,w,h in [
    ('left_stile',-.12,2.395,.055,1.55),
    ('right_stile',.74,2.395,.055,1.55),
    ('bottom_rail',.31,1.655,.87,.070),
    ('top_rail',.31,3.135,.87,.070)]:
    add(cab,key,box((w,.062,h),center=(x,.145,z),color=ivory))
add(cab,'side_bottom_edge',box((.045,CABINET_DEPTH,.045),
    center=(-.1725,.19+CABINET_DEPTH/2,1.6425),color=ivory))
add(cab,'knob_stem',rod(.012,start=(.695,.095,1.89),end=(.695,.15,1.89),color=steel))
add(cab,'knob',ball(.024,center=(.695,.08,1.89),color=steel))
scene.include('cabinet',cab)

window=Asset('Window and venetian blind')
add(window,'blue_daylight',box((1.12,.018,2.5),center=(-1.02,.89,1.95),color=(.59,.74,.76)))
for i,x in enumerate([-1.59,-.45]):
    add(window,f'frame_vertical_{i}',box((.055,.085,2.55),center=(x,.84,1.95),color=white))
for i,z in enumerate([.69,1.58,3.20]):
    add(window,f'frame_horizontal_{i}',box((1.20,.08,.048),center=(-1.02,.84,z),color=white))
add(window,'central_mullion',box((.028,.05,2.50),center=(-1.13,.82,1.95),color=white))
random.seed(12)
for i in range(24):
    add(window,f'outdoor_foliage_{i}',ball(random.uniform(.035,.115),
        center=(random.uniform(-1.53,-.50),.92,random.uniform(.9,3.15)),color=(.32,.46,.37)))
for i in range(40):
    z=.70+i*.063
    slat=box((1.20,.075,.014),center=(-1.02,.765,z),color=(.81,.81,.70))
    slat.turn('x',-12,pivot=(-1.02,.765,z))
    add(window,f'blind_slat_{i}',slat)
for i,x in enumerate([-1.39,-.59]):
    add(window,f'blind_tape_{i}',box((.012,.012,2.50),center=(x,.721,1.95),color=(.75,.75,.63)))
add(window,'pull_cord',rod(.0024,start=(-.52,.685,2.85),end=(-.52,.685,1.70),color=(.83,.80,.67)))
add(window,'pull_weight',rod(.009,length=.065,center=(-.52,.685,1.67),color=ivory))
scene.include('window',window)

paper=Asset('Wall mounted paper towel roll')
rx,ry,rz=.36,-.005,2.275
add(paper,'mount_upper',rod(.049,start=(rx,.16,2.66),end=(rx,-.025,2.66),color=steel))
add(paper,'mount_lower',rod(.048,start=(rx,.16,1.88),end=(rx,-.025,1.88),color=steel))
add(paper,'axle',rod(.022,start=(rx,ry,1.86),end=(rx,ry,2.69),color=steel))
add(paper,'roll',rod(.155,length=.72,center=(rx,ry,rz),color=(.92,.87,.73)))
add(paper,'finial',ball(.036,center=(rx,ry,2.685),color=steel))
add(paper,'hanging_paper_edge',box((.255,.007,.68),center=(rx,-.16,2.265),color=(.92,.87,.73)))
scene.include('paper_towel',paper)

ring=Asset('Towel ring and mount')
add(ring,'wall_disc',rod(.054,start=(-.24,.26,2.02),end=(-.24,.21,2.02),color=steel))
add(ring,'mount_neck',rod(.018,start=(-.24,.21,2.02),end=(-.24,.10,2.02),color=steel))
pts=[(-.30+.115*math.cos(2*math.pi*i/64),.09,
      1.83+.19*math.sin(2*math.pi*i/64)) for i in range(65)]
tube(ring,'ring',pts,.007,steel)
scene.include('towel_ring',ring)

sink=Asset('Sink and faucet')
rim=fillet_box((.89,.76,.028),radius=.013,center=(-.97,-.43,.893),color=steel)
hole=box((.80,.67,.10),center=(-.97,-.43,.893))
add(sink,'outer_steel_rim',subtract(rim,hole))
add(sink,'basin_floor',fillet_box((.76,.63,.025),radius=.012,
    center=(-.97,-.43,.685),color=(.018,.027,.022)))
for i,x in enumerate([-1.365,-.575]):
    add(sink,f'basin_side_{i}',box((.015,.67,.20),center=(x,-.43,.785),color=(.045,.054,.043)))
for i,y in enumerate([-.76,-.10]):
    add(sink,f'basin_end_{i}',box((.80,.015,.20),center=(-.97,y,.785),color=(.045,.054,.043)))
add(sink,'tap_base',rod(.047,length=.025,center=(-.72,.035,.915),color=steel))
tube(sink,'curved_faucet',[
    (-.72,.035,.92),(-.72,.035,1.22),(-.72,.025,1.30),
    (-.72,-.015,1.34),(-.72,-.08,1.34),(-.72,-.14,1.30),
    (-.72,-.15,1.25)],.012,steel)
add(sink,'lever_base',ball(.027,center=(-.62,.015,.925),color=steel))
add(sink,'lever',rod(.009,start=(-.62,.015,.935),end=(-.58,-.005,1.005),color=steel))
add(sink,'soap_tray',box((.18,.14,.018),center=(-1.25,.015,.91),color=(.45,.43,.31)))
add(sink,'soap',fillet_box((.13,.085,.035),radius=.015,center=(-1.25,.015,.936),color=(.78,.75,.55)))
scene.include('sink',sink)

can=Asset('Small countertop canister')
add(can,'body',rod(.065,length=.24,center=(-.27,.24,1.01),color=(.36,.38,.24)))
add(can,'lid',rod(.070,length=.025,center=(-.27,.24,1.14),color=steel))
add(can,'label',box((.065,.008,.12),center=(-.27,.176,1.00),color=(.63,.63,.43)))
scene.include('canister',can)

blender=Asset('Compact blender')
add(blender,'base',fillet_box((.18,.20,.23),radius=.035,center=(0,.29,1.005),color=(.018,.020,.016)))
add(blender,'collar',rod(.078,length=.045,center=(0,.29,1.135),color=(.035,.037,.028)))
cup=rod(.058,length=.35,center=(-.01,.29,1.33),color=(.40,.40,.32),opacity=.22)
cup.turn('y',-10,pivot=(-.01,.29,1.155))
add(blender,'clear_blending_cup',cup)
add(blender,'cup_lip',rod(.062,length=.009,center=(-.071,.29,1.50),color=(.39,.39,.32)))
tube(blender,'cup_edge_highlight',[(-.12,.245,1.17),(-.18,.245,1.49)],.003,(.64,.61,.49))
scene.include('blender',blender)

jug=Asset('Filtered water gallon jug')
add(jug,'body',fillet_box((.285,.225,.32),radius=.075,center=(.165,-.10,1.055),color=(.65,.68,.59)))
add(jug,'shoulder',ball(.14,center=(.165,-.10,1.198),color=(.65,.68,.59)))
add(jug,'neck',rod(.037,length=.075,center=(.165,-.10,1.325),color=(.73,.74,.64)))
add(jug,'cap',rod(.039,length=.026,center=(.165,-.10,1.363),color=(.83,.82,.70)))
tube(jug,'molded_handle',[
    (.22,-.216,1.26),(.26,-.221,1.23),(.27,-.223,1.16),
    (.24,-.223,1.13),(.205,-.219,1.16)],.012,(.59,.62,.54))
scene.include('water_jug',jug)

pitcher=Asset('Blue water filter pitcher')
add(pitcher,'body',fillet_box((.30,.24,.38),radius=.07,center=(.58,.23,1.095),color=(.018,.040,.105)))
add(pitcher,'upper_reservoir',fillet_box((.28,.23,.14),radius=.045,center=(.57,.23,1.295),color=(.024,.045,.10)))
lid=fillet_box((.34,.26,.045),radius=.02,center=(.57,.225,1.382),color=(.30,.31,.25))
lid.turn('y',12,pivot=(.57,.225,1.382))
add(pitcher,'lid',lid)
tube(pitcher,'clear_handle',[
    (.71,.24,1.31),(.82,.24,1.29),(.87,.24,1.22),
    (.88,.24,1.10),(.85,.24,.99),(.75,.24,.94)],.022,(.37,.40,.36))
add(pitcher,'spout',box((.065,.10,.055),center=(.405,.23,1.36),color=(.30,.32,.26)))
scene.include('filter_pitcher',pitcher)

# Audit: all fillet radii fit the thinnest dimension; all dimensions positive.
# Repeated include keys are indexed. All sweep endpoints differ.
realize(scene)
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient world')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.68,.56,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.17

def descendants(group):
    return [o for o in group.children_recursive if o.type=='MESH']

def material(name,color,roughness=.5,metallic=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    p.inputs['Metallic'].default_value=metallic
    return m

stone=material('Mottled brown granite',(.30,.26,.18),.65)
nt=stone.node_tree
p=nt.nodes.get('Principled BSDF')
coord=nt.nodes.new('ShaderNodeTexCoord')
noise=nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=190
noise.inputs['Detail'].default_value=2
nt.links.new(coord.outputs['Object'],noise.inputs['Vector'])
ramp=nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.28
ramp.color_ramp.elements[0].color=(.055,.043,.027,1)
ramp.color_ramp.elements[1].position=.73
ramp.color_ramp.elements[1].color=(.48,.39,.26,1)
e=ramp.color_ramp.elements.new(.50)
e.color=(.22,.18,.12,1)
nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.19
bump.inputs['Distance'].default_value=.003
nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
nt.links.new(bump.outputs[0],p.inputs['Normal'])
for name in ['counter','backsplash']:
    group=bpy.data.objects.get(name)
    if group:
        for ob in descendants(group):
            ob.data.materials.clear()
            ob.data.materials.append(stone)

clothmat=material('Warm ivory terrycloth',(.82,.75,.60),.98)
nt=clothmat.node_tree
n=nt.nodes.new('ShaderNodeTexNoise')
n.inputs['Scale'].default_value=230
n.inputs['Detail'].default_value=2
b=nt.nodes.new('ShaderNodeBump')
b.inputs['Strength'].default_value=.30
b.inputs['Distance'].default_value=.003
nt.links.new(n.outputs['Fac'],b.inputs['Height'])
nt.links.new(b.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])

verts=[]
faces=[]
rows,cols=40,28
for j in range(rows):
    t=j/(rows-1)
    width=.21+.16*math.sin(t*math.pi*.75)
    for i in range(cols):
        u=i/(cols-1)
        x=-.31+(u-.5)*width+.025*math.sin(t*4)
        z=1.67-.66*t+.065*math.sin(u*7+1.1)*t
        y=.055-.075*math.sin(math.pi*u)-.034*math.cos(u*math.pi*6)*(.3+.7*t)
        verts.append((x,y,z))
for j in range(rows-1):
    for i in range(cols-1):
        a=j*cols+i
        faces.append((a,a+1,a+1+cols,a+cols))
mesh=bpy.data.meshes.new('Draped towel editable mesh')
mesh.from_pydata(verts,[],faces)
mesh.update()
ob=bpy.data.objects.new('Hanging hand towel',mesh)
sc.collection.objects.link(ob)
group=bpy.data.objects.new('Hand towel assembly',None)
sc.collection.objects.link(group)
ob.parent=group
ob.data.materials.append(clothmat)
for poly in mesh.polygons:
    poly.use_smooth=True
solid=ob.modifiers.new('Fabric thickness','SOLIDIFY')
solid.thickness=.007
sub=ob.modifiers.new('Soft folds','SUBSURF')
sub.levels=1
sub.render_levels=1

# Traverse semantic groups; copy shared finishes before changing hardware.
for groupname in ['towel_ring','sink','paper_towel']:
    group=bpy.data.objects.get(groupname)
    if group:
        for ob in descendants(group):
            if ob.data.materials:
                old=ob.data.materials[0]
                c=old.diffuse_color
                if max(c[:3])-min(c[:3])<.15 and .2<c[0]<.65:
                    m=old.copy()
                    ob.data.materials[0]=m
                    if m.use_nodes:
                        p=m.node_tree.nodes.get('Principled BSDF')
                        if p:
                            p.inputs['Metallic'].default_value=.78
                            p.inputs['Roughness'].default_value=.27

ink=material('Faded marker',(.23,.25,.19),.9)
curve=bpy.data.curves.new('Filter label lettering','FONT')
curve.body='FILTER'
curve.size=.032
curve.space_character=1.05
text=bpy.data.objects.new('Handwritten FILTER label',curve)
sc.collection.objects.link(text)
text.location=(.075,-.216,1.015)
text.rotation_euler=(math.pi/2,0,0)
text.data.materials.append(ink)
parent=bpy.data.objects.get('water_jug')
if parent:
    matrix=text.matrix_world.copy()
    text.parent=parent
    text.matrix_world=matrix

set_view(CAMERA,TARGET,lens=LENS,sensor=36)
area_emitter(position=(-1.6,-.05,2.70),power=KEY_POWER,size=1.25,
             target=(0,.25,1.15),color=(.86,.92,1))
area_emitter(position=(-.6,-2.0,2.85),power=FILL_POWER,size=2.3,
             target=(0,.35,1.45),color=(1,.79,.52))
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=-.15
sc.render.image_settings.file_format='PNG'
