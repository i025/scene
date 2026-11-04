from sceneact import *
import bpy, math, random
from mathutils import Vector

# Estimated image anchors: window right edge (.29,.0)-(.30,.74);
# cabinet lower corner (.53,.53); roll (.61,.09)-(.82,.42);
# pitcher (.74,.60)-(.98,.84); jug (.59,.66)-(.79,.89).
# Camera looks slightly downward and sees the cabinet's left side.
CAMERA = (-1.12, -2.70, 1.91)
TARGET = (-.30, .27, 1.60)
LENS = 67
COUNTER_Z = .88
WALL_Y = .64
CABINET_BOTTOM = 1.49

scene = Scene('Kitchen corner')
cream = (.76,.70,.56)
ivory = (.88,.84,.72)
white = (.94,.92,.83)
steel = (.46,.45,.38)
dark = (.035,.040,.034)

def add(parent, key, node):
    return parent.include(key, node)

def tube(parent, key, pts, radius, color):
    pts = [p for i,p in enumerate(pts) if i == 0 or p != pts[i-1]]
    return add(parent,key,sweep_tube(points=pts,radius=radius,color=color))

architecture = Asset('Walls and counter')
add(architecture,'back_wall',box((3,.10,3.4),center=(0,.70,1.6),color=cream))
add(architecture,'counter',box((2.6,1.24,.065),center=(-.20,.02,COUNTER_Z-.0325),color=(.31,.29,.22)))
add(architecture,'backsplash',box((2.6,.035,.16),center=(-.20,.605,.96),color=(.34,.32,.25)))
scene.include('architecture',architecture)

cab = Asset('Painted upper cabinet')
add(cab,'carcass',box((.95,.43,1.55),center=(.22,.415,2.265),color=ivory))
# Door rails sit forward of the inset center panel.
add(cab,'door_panel',box((.84,.033,1.42),center=(.25,.183,2.28),color=(.83,.78,.65)))
for key,x,z,w,h in [
    ('left_stile',-.18,2.265,.055,1.55),
    ('right_stile',.68,2.265,.055,1.55),
    ('bottom_rail',.25,1.525,.87,.070),
    ('top_rail',.25,3.005,.87,.070)]:
    add(cab,key,box((w,.062,h),center=(x,.155,z),color=ivory))
add(cab,'side_bottom_edge',box((.055,.43,.055),center=(-.245,.415,1.515),color=ivory))
add(cab,'knob_stem',rod(.012,start=(.635,.105,1.76),end=(.635,.155,1.76),color=steel))
add(cab,'knob',ball(.024,center=(.635,.09,1.76),color=steel))
scene.include('cabinet',cab)

window = Asset('Window and venetian blind')
add(window,'blue_daylight',box((.97,.018,2.25),center=(-.89,.605,1.83),color=(.66,.79,.78)))
for i,x in enumerate([-1.39,-.40]):
    add(window,f'frame_vertical_{i}',box((.055,.085,2.35),center=(x,.55,1.83),color=white))
for i,z in enumerate([.66,1.53,2.96]):
    add(window,f'frame_horizontal_{i}',box((1.06,.08,.048),center=(-.89,.55,z),color=white))
add(window,'central_mullion',box((.028,.05,2.26),center=(-.95,.53,1.83),color=white))
# Soft outdoor shapes are geometry beyond the glass.
random.seed(12)
for i in range(24):
    x=random.uniform(-1.36,-.44)
    z=random.uniform(.9,2.95)
    add(window,f'outdoor_foliage_{i}',ball(random.uniform(.035,.115),center=(x,.63,z),color=(.38,.53,.42)))
for i in range(36):
    z=.70+i*.063
    slat=box((1.06,.075,.014),center=(-.89,.475,z),color=(.84,.84,.74))
    slat.turn('x',-12,pivot=(-.89,.475,z))
    add(window,f'blind_slat_{i}',slat)
for i,x in enumerate([-1.23,-.53]):
    add(window,f'blind_tape_{i}',box((.012,.012,2.25),center=(x,.431,1.83),color=(.77,.77,.65)))
add(window,'pull_cord',rod(.0024,start=(-.46,.395,2.65),end=(-.46,.395,1.69),color=(.83,.80,.67)))
add(window,'pull_weight',rod(.009,length=.065,center=(-.46,.395,1.66),color=ivory))
scene.include('window',window)

paper = Asset('Wall mounted paper towel roll')
roll_x, roll_y, roll_z = .30,.005,2.055
add(paper,'mount_upper',rod(.049,start=(roll_x,.17,2.40),end=(roll_x,-.015,2.40),color=steel))
add(paper,'mount_lower',rod(.048,start=(roll_x,.17,1.70),end=(roll_x,-.015,1.70),color=steel))
add(paper,'axle',rod(.022,start=(roll_x,roll_y,1.68),end=(roll_x,roll_y,2.43),color=steel))
add(paper,'roll',rod(.155,length=.64,center=(roll_x,roll_y,roll_z),color=(.96,.93,.82)))
add(paper,'finial',ball(.036,center=(roll_x,roll_y,2.425),color=steel))
add(paper,'hanging_paper_edge',box((.255,.007,.60),center=(roll_x,-.15,2.045),color=(.96,.93,.82)))
scene.include('paper_towel',paper)

ring = Asset('Towel ring and mount')
add(ring,'wall_disc',rod(.054,start=(-.30,.205,1.86),end=(-.30,.155,1.86),color=steel))
add(ring,'mount_neck',rod(.018,start=(-.30,.15,1.86),end=(-.30,.075,1.86),color=steel))
ring_pts=[(-.36+.125*math.cos(t),.068,1.705+.155*math.sin(t)) for t in [2*math.pi*i/72 for i in range(73)]]
tube(ring,'ring',ring_pts,.007,steel)
scene.include('towel_ring',ring)

sink=Asset('Sink and faucet')
add(sink,'outer_steel_rim',fillet_box((.74,.57,.025),radius=.012,center=(-.86,-.30,.897),color=(.38,.39,.33)))
add(sink,'dark_basin',fillet_box((.64,.47,.025),radius=.012,center=(-.86,-.32,.909),color=(.025,.035,.030)))
add(sink,'inner_basin',fillet_box((.54,.36,.020),radius=.009,center=(-.86,-.32,.913),color=(.052,.066,.053)))
add(sink,'tap_base',rod(.047,length=.025,center=(-.72,.035,.915),color=steel))
tappts=[(-.72,.035,.92),(-.72,.035,1.22),(-.72,.025,1.30),(-.72,-.015,1.34),(-.72,-.08,1.34),(-.72,-.14,1.30),(-.72,-.15,1.25)]
tube(sink,'curved_faucet',tappts,.012,steel)
add(sink,'lever_base',ball(.027,center=(-.62,.015,.925),color=steel))
add(sink,'lever',rod(.009,start=(-.62,.015,.935),end=(-.58,-.005,1.005),color=steel))
add(sink,'soap_tray',box((.18,.14,.018),center=(-1.18,-.08,.92),color=(.45,.43,.31)))
add(sink,'soap',fillet_box((.13,.085,.035),radius=.015,center=(-1.18,-.08,.946),color=(.78,.75,.55)))
scene.include('sink',sink)

can=Asset('Small countertop canister')
add(can,'body',rod(.065,length=.24,center=(-.34,.24,1.01),color=(.43,.45,.32)))
add(can,'lid',rod(.070,length=.025,center=(-.34,.24,1.14),color=steel))
add(can,'label',box((.065,.008,.12),center=(-.34,.176,1.00),color=(.69,.69,.52)))
scene.include('canister',can)

blender=Asset('Compact blender')
add(blender,'base',fillet_box((.18,.20,.23),radius=.035,center=(-.10,.29,1.005),color=(.025,.027,.022)))
add(blender,'collar',rod(.078,length=.045,center=(-.10,.29,1.135),color=(.055,.057,.043)))
cup=rod(.058,length=.31,center=(-.11,.29,1.31),color=(.48,.47,.36),opacity=.30)
cup.turn('y',-10,pivot=(-.11,.29,1.155))
add(blender,'clear_blending_cup',cup)
add(blender,'cup_lip',rod(.062,length=.012,center=(-.163,.29,1.465),color=(.30,.30,.24)))
scene.include('blender',blender)

jug=Asset('Filtered water gallon jug')
add(jug,'body',fillet_box((.285,.225,.32),radius=.075,center=(.105,-.10,1.055),color=(.75,.77,.69),opacity=.92))
add(jug,'shoulder',ball(.14,center=(.105,-.10,1.198),color=(.75,.77,.69),opacity=.92))
add(jug,'neck',rod(.037,length=.075,center=(.105,-.10,1.325),color=(.79,.80,.71)))
add(jug,'cap',rod(.039,length=.026,center=(.105,-.10,1.363),color=(.89,.88,.77)))
scene.include('water_jug',jug)

pitcher=Asset('Blue water filter pitcher')
add(pitcher,'body',fillet_box((.30,.24,.38),radius=.07,center=(.52,.23,1.095),color=(.035,.080,.16),opacity=.79))
add(pitcher,'upper_reservoir',fillet_box((.28,.23,.14),radius=.045,center=(.51,.23,1.295),color=(.045,.075,.12),opacity=.85))
lid=fillet_box((.34,.26,.045),radius=.02,center=(.51,.225,1.382),color=(.36,.38,.32))
lid.turn('y',12,pivot=(.51,.225,1.382))
add(pitcher,'lid',lid)
handlepts=[(.65,.24,1.31),(.76,.24,1.29),(.81,.24,1.22),(.82,.24,1.10),(.79,.24,.99),(.69,.24,.94)]
tube(pitcher,'clear_handle',handlepts,.022,(.43,.47,.43))
add(pitcher,'spout',box((.065,.10,.055),center=(.345,.23,1.36),color=(.34,.37,.32)))
scene.include('filter_pitcher',pitcher)

# Primitive audit: all sizes positive; fillets <= half the smallest dimension.
# Repeated parts use indexed unique keys; all finishes are assigned to attached trees.
realize(scene)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('Ambient world')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.72,.73,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.32

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

# Grain is procedural, never sampled from the photograph.
stone=material('Fine mottled brown granite',(.31,.29,.23),.62)
nt=stone.node_tree
p=nt.nodes.get('Principled BSDF')
noise=nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=170
noise.inputs['Detail'].default_value=3
ramp=nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.22
ramp.color_ramp.elements[0].color=(.075,.066,.045,1)
ramp.color_ramp.elements[1].position=.78
ramp.color_ramp.elements[1].color=(.65,.59,.45,1)
nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
nt.links.new(ramp.outputs[0],p.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.22
bump.inputs['Distance'].default_value=.006
nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
nt.links.new(bump.outputs[0],p.inputs['Normal'])
for groupname in ['counter','backsplash']:
    group=bpy.data.objects.get(groupname)
    if group:
        for ob in descendants(group):
            ob.data.materials.clear()
            ob.data.materials.append(stone)

# A single editable cloth surface gives the towel a folded, irregular silhouette.
clothmat=material('Warm ivory terrycloth',(.85,.80,.67),.98)
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
rows,cols=36,24
for j in range(rows):
    t=j/(rows-1)
    width=.15+.065*t
    for i in range(cols):
        u=i/(cols-1)
        x=-.365+(u-.5)*width
        z=1.62-.64*t+.028*math.sin(u*8+1.1)*t
        y=.015-.045*math.sin(math.pi*u)-.020*math.cos(u*math.pi*7)*(0.3+.7*t)
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
ob.data.materials.append(clothmat)
for poly in mesh.polygons:
    poly.use_smooth=True
solid=ob.modifiers.new('Fabric thickness','SOLIDIFY')
solid.thickness=.008
sub=ob.modifiers.new('Soft folds','SUBSURF')
sub.levels=1
sub.render_levels=1

# Reflective hardware materials are copied before edits.
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
                            p.inputs['Roughness'].default_value=.26

# Small handwritten marking on the front of the gallon.
ink=material('Faded marker',(.29,.31,.26),.9)
curve=bpy.data.curves.new('Filter label lettering','FONT')
curve.body='FILTER'
curve.size=.032
curve.space_character=1.05
curve.extrude=0
text=bpy.data.objects.new('Handwritten FILTER label',curve)
sc.collection.objects.link(text)
text.location=(.015,-.216,1.015)
text.rotation_euler=(math.pi/2,0,0)
text.data.materials.append(ink)

set_view(CAMERA,TARGET,lens=LENS,sensor=36)
area_emitter(position=(-1.6,-.05,2.30),power=220,size=1.25,target=(.0,.25,1.15),color=(.82,.91,1))
area_emitter(position=(-.6,-2.0,2.65),power=75,size=2.3,target=(.0,.35,1.45),color=(1,.84,.63))
sc.render.engine='CYCLES'
sc.cycles.samples=48
sc.cycles.use_denoising=True
sc.render.resolution_x=384
sc.render.resolution_y=512
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
sc.view_settings.exposure=0
sc.render.image_settings.file_format='PNG'
