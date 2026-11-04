from sceneact import *
import bpy, math
from mathutils import Vector

# Visible assemblies: window and blinds, cream wall cabinet, hanging paper roll,
# towel ring and cloth, granite counter, cropped sink/faucet, blender and pitchers.
# Approximate image landmarks (uncertain by .03-.06):
# cabinet bottom (.51,.52), roll bounds (.60,.08)-(.84,.42),
# towel (.27,.48)-(.48,.83), jug (.59,.65)-(.79,.89),
# blue pitcher (.74,.60)-(.96,.85), sink opening (0,.87)-(.48,1).
# Cabinet, counter and blind slats are filled surfaces; sink and handles are openings.
# Camera distance, cabinet depth, and hidden appliance bases are uncertain.

scene = Scene('Kitchen')
cream=(.76,.71,.58)
trim=(.85,.81,.69)
white=(.90,.88,.79)
metal=(.49,.48,.40)
dark=(.025,.030,.026)
blue=(.045,.085,.16)

def put(parent,name,node):
    parent.include(name,node)
    return node

def bx(parent,name,size,center,color):
    return put(parent,name,box(size,center=center,color=color))

def tube(parent,name,pts,r,color):
    return put(parent,name,sweep_tube(points=pts,radius=r,color=color))

# Explicit major dimensions and placement.
COUNTER_Z=.91
CAB_BOTTOM=1.66
CAB_TOP=2.88
BACK_Y=.68
CAMERA=(-1.48,-3.55,2.22)
TARGET=(-.22,.34,1.65)
LENS=47

arch=Asset('Architecture')
bx(arch,'rear_wall',(4,.10,3.4),(0,.79,1.7),(.74,.70,.59))
bx(arch,'right_wall',( .10,2.6,3.4),(1.42,-.45,1.7),cream)
scene.include('architecture',arch)

cab=Asset('Wall_cabinet')
bx(cab,'case',(.98,.49,CAB_TOP-CAB_BOTTOM),(.40,.47,(CAB_TOP+CAB_BOTTOM)/2),cream)
# Broad side and front, raised door frame, inset central panel.
bx(cab,'left_side',(.055,.55,1.22),(-.115,.44,2.27),trim)
bx(cab,'door_panel',(.86,.035,1.10),(.43,.198,2.29),(.79,.75,.63))
for name,size,center in [
    ('left_stile',(.055,.048,1.16),(.015,.165,2.29)),
    ('right_stile',(.055,.048,1.16),(.855,.165,2.29)),
    ('top_rail',(.84,.048,.065),(.435,.165,2.84)),
    ('bottom_rail',(.84,.048,.065),(.435,.165,1.74))]:
    bx(cab,name,size,center,trim)
put(cab,'door_knob',ball(.023,center=(.82,.111,1.91),color=(.47,.40,.24)))
scene.include('cabinet',cab)

window=Asset('Window_and_blinds')
bx(window,'daylight_glass',(1.10,.025,2.22),(-.82,.70,1.91),(.63,.80,.85))
for x in (-1.40,-.25):
    bx(window,'jamb_'+str(x),(.065,.11,2.4),(x,.62,1.91),trim)
for z in (.72,3.08):
    bx(window,'frame_'+str(z),(1.22,.11,.075),(-.825,.62,z),trim)
bx(window,'sash_vertical',(.035,.065,2.25),(-.97,.59,1.91),white)
bx(window,'sash_horizontal',(1.10,.065,.055),(-.82,.58,2.17),white)
# Economical opaque horizontal slats, with real gaps.
for i in range(32):
    z=.82+i*.070
    slat=box((1.14,.105,.022),center=(-.82,.535,z),color=(.80,.80,.72))
    slat.turn(axis='+x',degrees=-12)
    put(window,'blind_slat_%02d'%i,slat)
for i,x in enumerate((-1.20,-.47)):
    bx(window,'blind_ladder_'+str(i),(.009,.012,2.22),(x,.466,1.92),(.78,.76,.66))
bx(window,'sill',(1.25,.22,.07),(-.82,.56,.755),trim)
# Faint outdoor masses behind the blinds.
for i,(x,z,r) in enumerate([(-1.2,2.8,.13),(-.65,2.70,.19),(-1.1,2.45,.15),(-.4,2.95,.16)]):
    put(window,'foliage_'+str(i),ball(r,center=(x,.735,z),color=(.36,.55,.41)))
scene.include('window',window)

counter=Asset('Countertop')
bx(counter,'stone_slab',(3.5,1.45,.085),(-.18,.02,.867),(.36,.34,.28))
bx(counter,'backsplash',(3.5,.055,.145),(-.18,.705,.98),(.36,.34,.28))
bx(counter,'lower_cabinet',(3.5,1.35,.84),(-.18,.04,.405),(.43,.36,.25))
scene.include('counter',counter)

# Sink foreground: dark filled basin and metallic rim strips, cropped by framing.
sink=Asset('Sink')
bx(sink,'basin_dark',(.73,.62,.035),(-.87,-.52,.917),(.016,.023,.020))
for name,sz,ctr in [
    ('back_rim',(.82,.045,.025),(-.87,-.195,.935)),
    ('front_rim',(.82,.045,.025),(-.87,-.845,.935)),
    ('left_rim',(.045,.65,.025),(-1.27,-.52,.935)),
    ('right_rim',(.045,.65,.025),(-.47,-.52,.935))]:
    bx(sink,name,sz,ctr,metal)
tube(sink,'faucet',[
    (-.93,-.15,.94),(-.93,-.15,1.06),(-.93,-.15,1.32),
    (-.93,-.12,1.40),(-.93,-.04,1.41),(-.93,.005,1.37)
],.014,metal)
put(sink,'tap_base',rod(.043,length=.035,center=(-.93,-.15,.95),color=metal))
tube(sink,'tap_handle',[(-1.01,-.15,.96),(-1.065,-.16,1.02),(-1.08,-.16,1.06)],.012,metal)
bx(sink,'sponge',(.16,.10,.028),(-1.24,-.30,.954),(.73,.69,.43))
scene.include('sink',sink)

# Roll supported vertically in front of the cabinet.
paper=Asset('Paper_towel_holder')
put(paper,'roll',rod(.143,length=.66,center=(.44,-.045,2.21),color=(.94,.91,.81)))
put(paper,'top_finial',ball(.037,center=(.44,-.045,2.58),color=metal))
put(paper,'bottom_finial',ball(.029,center=(.44,-.045,1.855),color=dark))
tube(paper,'support',[ (.44,.17,1.84),(.44,-.045,1.84),(.44,-.045,2.59)],.012,metal)
scene.include('paper_roll',paper)

ring=Asset('Towel_ring_and_cloth')
put(ring,'mount',rod(.052,start=(-.15,.40,2.04),end=(-.24,.40,2.04),color=metal))
# Ring on exposed side of cabinet.
pts=[]
for i in range(13):
    a=2*math.pi*i/12
    pts.append((-.25,.34+.105*math.cos(a),1.91+.153*math.sin(a)))
tube(ring,'ring',pts,.009,metal)

# A cloth surface with irregular hem and overlapping folded panels.
def cloth_mesh(name, width, height, origin, fold=0):
    verts=[]; faces=[]
    nx,nz=12,17
    for j in range(nz):
        t=j/(nz-1)
        for i in range(nx):
            u=i/(nx-1)
            x=origin[0]+(u-.5)*width*(.70+.30*t)
            y=origin[1]+.027*math.cos(u*math.pi*6+fold)+.035*math.sin(t*3)
            z=origin[2]-height*t+.025*math.sin(u*9+fold)*t**5
            verts.append((x,y,z))
    for j in range(nz-1):
        for i in range(nx-1):
            a=j*nx+i
            faces.append((a,a+1,a+nx+1,a+nx))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces); mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    return ob

# SceneAct cloth masses preserve assembly membership; custom cloth added after realize.
bx(ring,'cloth_fold_core',(.16,.065,.53),(-.29,.12,1.40),(.82,.79,.68))
scene.include('towel_fixture',ring)

# Blender with black base and narrow clear mixing vessel.
blender=Asset('Blender')
put(blender,'base',rod(.105,length=.235,center=(.05,.39,1.03),color=(.022,.027,.025)))
put(blender,'base_top',rod(.09,length=.045,center=(.05,.39,1.16),color=dark))
vessel=rod(.063,length=.29,center=(.055,.39,1.325),color=(.51,.56,.53),opacity=.30)
vessel.turn(axis='+y',degrees=-11)
put(blender,'clear_cup',vessel)
put(blender,'cup_rim',rod(.065,length=.012,center=(.025,.39,1.471),color=metal))
scene.include('blender',blender)

tin=Asset('Small_counter_items')
put(tin,'canister',rod(.069,length=.235,center=(-.20,.34,1.03),color=(.33,.33,.19)))
put(tin,'canister_lid',rod(.075,length=.018,center=(-.20,.34,1.154),color=(.57,.53,.33)))
put(tin,'small_cap',rod(.042,length=.035,center=(-.66,-.13,.94),color=(.14,.13,.09)))
scene.include('small_items',tin)

jug=Asset('Filter_water_jug')
# Broad milky gallon bottle silhouette, tapered shoulders and short neck.
put(jug,'body',ball(.17,center=(.40,.03,1.10),color=(.74,.76,.68)))
put(jug,'lower_body',fillet_box((.30,.235,.23),radius=.035,center=(.40,.03,1.035),color=(.76,.78,.70)))
shoulder=ball(.14,center=(.40,.03,1.235),color=(.77,.79,.71))
shoulder.resize((.88,.80,1.03))
put(jug,'shoulder',shoulder)
put(jug,'neck',rod(.047,length=.065,center=(.40,.03,1.36),color=white))
put(jug,'cap',rod(.049,length=.025,center=(.40,.03,1.397),color=white))
# A raised molded handle on the upper right.
tube(jug,'molded_handle',[(.47,-.01,1.29),(.52,-.01,1.24),(.53,-.01,1.15),(.48,-.01,1.13)],.019,(.69,.72,.64))
scene.include('water_jug',jug)

pitcher=Asset('Blue_filter_pitcher')
body=rod(.145,length=.36,center=(.84,.34,1.105),color=blue,opacity=.87)
put(pitcher,'reservoir',body)
put(pitcher,'bottom',rod(.136,length=.025,center=(.84,.34,.936),color=(.09,.12,.15)))
lid=ball(.155,center=(.84,.34,1.30),color=(.45,.46,.42))
lid.resize((1.08,1,.27))
put(pitcher,'lid',lid)
tube(pitcher,'clear_handle',[
    (.96,.34,1.28),(1.065,.34,1.24),(1.105,.34,1.13),
    (1.09,.34,1.015),(1.03,.34,.97),(.98,.34,1.00)
],.025,(.47,.51,.49))
put(pitcher,'spout',box((.09,.13,.055),center=(.71,.34,1.295),color=(.40,.43,.40)))
scene.include('blue_pitcher',pitcher)

realize(scene)

# Materials: fine granite aggregate and subtle paper/cloth texture.
def meshes_under(name):
    root=bpy.data.objects.get(name)
    return [o for o in root.children_recursive if o.type=='MESH'] if root else []

for ob in meshes_under('counter'):
    if 'lower' in ob.name.lower():
        continue
    if not ob.data.materials: continue
    mat=ob.data.materials[0].copy()
    ob.data.materials[0]=mat
    mat.use_nodes=True
    nt=mat.node_tree
    bs=nt.nodes.get('Principled BSDF')
    noise=nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=155
    noise.inputs['Detail'].default_value=2
    ramp=nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.23
    ramp.color_ramp.elements[0].color=(.065,.057,.042,1)
    ramp.color_ramp.elements[1].position=.77
    ramp.color_ramp.elements[1].color=(.62,.57,.44,1)
    nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value=.65

clothmat=bpy.data.materials.new('Ivory terrycloth')
clothmat.diffuse_color=(.82,.79,.69,1)
clothmat.use_nodes=True
nt=clothmat.node_tree
bs=nt.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.82,.79,.69,1)
bs.inputs['Roughness'].default_value=.95
noise=nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=210
bump=nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.22
bump.inputs['Distance'].default_value=.006
nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
for name,w,h,org,phase in [
    ('Towel_front',.27,.63,(-.30,.065,1.78),0),
    ('Towel_back',.24,.47,(-.23,.14,1.78),1.2)]:
    ob=cloth_mesh(name,w,h,org,phase)
    ob.data.materials.append(clothmat)
    solid=ob.modifiers.new('Cloth thickness','SOLIDIFY')
    solid.thickness=.006
    for p in ob.data.polygons: p.use_smooth=True
    ob.parent=bpy.data.objects.get('towel_fixture')

# Handwritten label is a small but recognizable visible feature.
textcurve=bpy.data.curves.new('Filter_label','FONT')
textcurve.body='FILTER'
textcurve.size=.038
textcurve.extrude=.0001
label=bpy.data.objects.new('Filter_label',textcurve)
bpy.context.collection.objects.link(label)
label.location=(.319,-.093,1.01)
label.rotation_euler=(math.pi/2,0,0)
ink=bpy.data.materials.new('Faded_marker')
ink.diffuse_color=(.25,.27,.24,1)
label.data.materials.append(ink)
label.parent=bpy.data.objects.get('water_jug')

# A soft, warm kitchen illuminated primarily by the window to the left.
sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.68,.72,.75,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.32
set_view(CAMERA,TARGET,lens=LENS,sensor=36)
area_emitter((-1.5,-.20,2.55),power=380,size=1.8,target=(.25,.35,1.45),color=(.82,.91,1))
area_emitter((-.25,-2,2.8),power=135,size=2.6,target=(.15,.35,1.5),color=(1,.84,.62))
sc.view_settings.view_transform='AgX'
