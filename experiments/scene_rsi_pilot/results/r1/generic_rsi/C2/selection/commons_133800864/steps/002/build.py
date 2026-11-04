from sceneact import *
import bpy, math

# Reference/render visual estimates, not calibration:
# window right edge: (.29,.50)/(.48,.50); roll top: (.72,.08)/(.84,.20);
# cabinet bottom: (.51,.52)/(.64,.49); jug bottom: (.69,.88)/(.79,.74).
# Largest error is insufficient scene occupancy and framing too far left.
# Primary correction: lens 47 -> 63, horizontal camera shift .23.
# Expected: window boundary moves left, roll grows upward, counter fills foreground.
# Preserve the window's filled slats/gaps and cabinet's solid framed door.
# Dependent local corrections keep appliances on the counter and towel on its ring.
# Broad tone: reference countertop and blue pitcher are substantially darker.
# Assemblies: architecture, blinds, cabinet, paper holder, towel fixture, sink,
# granite counter, blender, canister, gallon bottle and blue filter pitcher.
# Uncertain: hidden sink depth, cabinet depth and pitcher handle cross-section.

scene = Scene('Kitchen')
cream=(.66,.59,.45)
trim=(.76,.69,.55)
white=(.86,.83,.73)
metal=(.40,.38,.30)
dark=(.018,.022,.019)
blue=(.018,.038,.095)

COUNTER_Z=.91
CAB_BOTTOM=1.66
CAB_TOP=2.88
CAMERA=(-1.48,-3.55,2.22)
TARGET=(-.22,.34,1.65)
LENS=63
SHIFT=(.23,.015)

def put(parent,name,node):
    parent.include(name,node)
    return node

def bx(parent,name,size,center,color):
    return put(parent,name,box(size,center=center,color=color))

def tube(parent,name,pts,r,color):
    return put(parent,name,sweep_tube(points=pts,radius=r,color=color))

arch=Asset('Architecture')
bx(arch,'rear_wall',(4,.10,3.4),(0,.79,1.7),(.68,.61,.48))
bx(arch,'right_wall',(.10,2.6,3.4),(1.42,-.45,1.7),cream)
scene.include('architecture',arch)

cab=Asset('Wall_cabinet')
bx(cab,'case',(.98,.49,CAB_TOP-CAB_BOTTOM),(.40,.47,2.27),cream)
bx(cab,'left_side',(.055,.55,1.22),(-.115,.44,2.27),trim)
bx(cab,'door_panel',(.86,.035,1.10),(.43,.198,2.29),(.69,.62,.48))
for name,size,center in [
    ('left_stile',(.055,.048,1.16),(.015,.165,2.29)),
    ('right_stile',(.055,.048,1.16),(.855,.165,2.29)),
    ('top_rail',(.84,.048,.065),(.435,.165,2.84)),
    ('bottom_rail',(.84,.048,.065),(.435,.165,1.74))
]:
    bx(cab,name,size,center,trim)
put(cab,'door_knob',ball(.023,center=(.82,.111,1.91),color=(.39,.31,.16)))
scene.include('cabinet',cab)

window=Asset('Window_and_blinds')
bx(window,'daylight_glass',(1.10,.025,2.22),(-.82,.70,1.91),(.57,.73,.77))
for i,x in enumerate((-1.40,-.25)):
    bx(window,'jamb_'+str(i),(.065,.11,2.4),(x,.62,1.91),trim)
for i,z in enumerate((.72,3.08)):
    bx(window,'frame_'+str(i),(1.22,.11,.075),(-.825,.62,z),trim)
bx(window,'sash_vertical',(.035,.065,2.25),(-.97,.59,1.91),white)
bx(window,'sash_horizontal',(1.10,.065,.055),(-.82,.58,2.17),white)
for i in range(32):
    slat=box((1.14,.105,.022),center=(-.82,.535,.82+i*.070),
             color=(.76,.76,.67))
    slat.turn(axis='+x',degrees=-12)
    put(window,'blind_slat_%02d'%i,slat)
for i,x in enumerate((-1.20,-.47)):
    bx(window,'blind_ladder_'+str(i),(.009,.012,2.22),(x,.466,1.92),(.72,.69,.58))
bx(window,'sill',(1.25,.22,.07),(-.82,.56,.755),trim)
for i,(x,z,r) in enumerate([
    (-1.2,2.8,.13),(-.65,2.70,.19),(-1.1,2.45,.15),(-.4,2.95,.16)
]):
    put(window,'foliage_'+str(i),ball(r,center=(x,.735,z),color=(.28,.46,.33)))
scene.include('window',window)

counter=Asset('Countertop')
stone=(.24,.21,.15)
bx(counter,'stone_slab',(3.5,1.45,.085),(-.18,.02,.867),stone).name='GraniteSlab'
bx(counter,'backsplash',(3.5,.055,.145),(-.18,.705,.98),stone).name='GraniteBacksplash'
bx(counter,'lower_cabinet',(3.5,1.35,.84),(-.18,.04,.405),(.36,.29,.18)).name='LowerCabinet'
scene.include('counter',counter)

sink=Asset('Sink')
# Dark filled basin sits above the slab: a visible opening rather than a pale panel.
bx(sink,'basin_dark',(.85,.77,.035),(-.87,-.58,.917),(.006,.011,.008))
for name,sz,ctr in [
    ('back_rim',(.93,.035,.025),(-.87,-.195,.935)),
    ('front_rim',(.93,.035,.025),(-.87,-.965,.935)),
    ('left_rim',(.035,.77,.025),(-1.32,-.58,.935)),
    ('right_rim',(.035,.77,.025),(-.42,-.58,.935))
]:
    bx(sink,name,sz,ctr,metal)
tube(sink,'faucet',[
    (-.93,-.15,.94),(-.93,-.15,1.08),(-.93,-.15,1.32),
    (-.93,-.12,1.40),(-.93,-.04,1.41),(-.93,.005,1.37)
],.012,metal)
put(sink,'tap_base',rod(.043,length=.035,center=(-.93,-.15,.95),color=metal))
tube(sink,'tap_handle',[
    (-1.01,-.15,.96),(-1.065,-.16,1.02),(-1.08,-.16,1.06)
],.012,metal)
bx(sink,'sponge',(.16,.10,.028),(-1.24,-.30,.954),(.65,.59,.33))
scene.include('sink',sink)

paper=Asset('Paper_towel_holder')
put(paper,'roll',rod(.143,length=.66,center=(.44,-.045,2.21),color=(.88,.84,.73)))
put(paper,'top_finial',ball(.037,center=(.44,-.045,2.58),color=metal))
put(paper,'bottom_finial',ball(.029,center=(.44,-.045,1.855),color=dark))
tube(paper,'support',[
    (.44,.17,1.84),(.44,-.045,1.84),(.44,-.045,2.59)
],.012,metal)
scene.include('paper_roll',paper)

ring=Asset('Towel_ring_and_cloth')
put(ring,'mount',rod(.052,start=(-.15,.40,2.04),end=(-.24,.40,2.04),color=metal))
pts=[]
for i in range(13):
    a=2*math.pi*i/12
    pts.append((-.25,.34+.105*math.cos(a),1.91+.153*math.sin(a)))
tube(ring,'ring',pts,.008,metal)
# Cloth surfaces added after realization, with a concealed fold in this assembly.
bx(ring,'cloth_fold_core',(.16,.065,.53),(-.21,-.015,1.40),(.76,.71,.60))
scene.include('towel_fixture',ring)

blender=Asset('Blender')
put(blender,'base',rod(.105,length=.235,center=(.27,.28,1.03),color=dark))
put(blender,'base_top',rod(.09,length=.045,center=(.27,.28,1.16),color=dark))
cup=rod(.063,length=.29,center=(.275,.28,1.325),
        color=(.38,.43,.39),opacity=.30)
cup.turn(axis='+y',degrees=-11)
put(blender,'clear_cup',cup)
put(blender,'cup_rim',rod(.065,length=.010,center=(.245,.28,1.471),color=metal))
scene.include('blender',blender)

tin=Asset('Small_counter_items')
put(tin,'canister',rod(.069,length=.235,center=(-.09,.22,1.03),color=(.26,.27,.13)))
put(tin,'canister_lid',rod(.075,length=.018,center=(-.09,.22,1.154),color=(.47,.42,.24)))
put(tin,'small_cap',rod(.042,length=.035,center=(-.66,-.13,.94),color=(.10,.09,.055)))
scene.include('small_items',tin)

jug=Asset('Filter_water_jug')
JX,JY=.40,-.20
put(jug,'body',ball(.17,center=(JX,JY,1.10),color=(.61,.64,.55)))
put(jug,'lower_body',fillet_box((.30,.235,.23),radius=.035,
    center=(JX,JY,1.035),color=(.65,.67,.59)))
shoulder=ball(.14,center=(JX,JY,1.235),color=(.66,.69,.60))
shoulder.resize((.88,.80,1.03))
put(jug,'shoulder',shoulder)
put(jug,'neck',rod(.047,length=.065,center=(JX,JY,1.36),color=white))
put(jug,'cap',rod(.049,length=.025,center=(JX,JY,1.397),color=white))
tube(jug,'molded_handle',[
    (.47,JY-.04,1.29),(.52,JY-.04,1.24),
    (.53,JY-.04,1.15),(.48,JY-.04,1.13)
],.019,(.59,.63,.54))
scene.include('water_jug',jug)

pitcher=Asset('Blue_filter_pitcher')
PX,PY=.84,.08
put(pitcher,'reservoir',rod(.145,length=.43,center=(PX,PY,1.14),color=blue))
put(pitcher,'bottom',rod(.136,length=.025,center=(PX,PY,.936),color=(.035,.055,.065)))
lid=ball(.155,center=(PX,PY,1.365),color=(.34,.34,.28))
lid.resize((1.08,1,.27))
put(pitcher,'lid',lid)
tube(pitcher,'clear_handle',[
    (.96,PY,1.345),(1.065,PY,1.29),(1.105,PY,1.16),
    (1.09,PY,1.015),(1.03,PY,.97),(.98,PY,1.00)
],.023,(.35,.39,.35))
put(pitcher,'spout',box((.09,.13,.055),center=(.71,PY,1.36),color=(.31,.33,.28)))
scene.include('blue_pitcher',pitcher)

realize(scene)

def meshes_under(name):
    root=bpy.data.objects.get(name)
    return [o for o in root.children_recursive if o.type=='MESH'] if root else []

# Granite is a dark, finely mottled filled region in the reference.
for ob in meshes_under('counter'):
    if not ob.name.startswith(('GraniteSlab','GraniteBacksplash')):
        continue
    mat=bpy.data.materials.new('Granite_'+ob.name)
    mat.use_nodes=True
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    nt=mat.node_tree
    bs=nt.nodes.get('Principled BSDF')
    noise=nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=190
    noise.inputs['Detail'].default_value=2
    ramp=nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.25
    ramp.color_ramp.elements[0].color=(.035,.029,.020,1)
    ramp.color_ramp.elements[1].position=.77
    ramp.color_ramp.elements[1].color=(.36,.30,.21,1)
    nt.links.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value=.63

clothmat=bpy.data.materials.new('Ivory terrycloth')
clothmat.use_nodes=True
nt=clothmat.node_tree
bs=nt.nodes.get('Principled BSDF')
bs.inputs['Base Color'].default_value=(.78,.73,.62,1)
bs.inputs['Roughness'].default_value=.95
noise=nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=210
bump=nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.20
bump.inputs['Distance'].default_value=.004
nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

def cloth_mesh(name,width,height,origin,phase):
    verts=[]
    faces=[]
    nx,nz=12,17
    for j in range(nz):
        t=j/(nz-1)
        for i in range(nx):
            u=i/(nx-1)
            x=origin[0]+(u-.5)*width*(.65+.35*t)
            y=origin[1]+.032*math.cos(u*math.pi*6+phase)+.035*math.sin(t*3)
            z=origin[2]-height*t+.025*math.sin(u*9+phase)*t**5
            verts.append((x,y,z))
    for j in range(nz-1):
        for i in range(nx-1):
            a=j*nx+i
            faces.append((a,a+1,a+nx+1,a+nx))
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(clothmat)
    ob.parent=bpy.data.objects.get('towel_fixture')
    mod=ob.modifiers.new('Cloth thickness','SOLIDIFY')
    mod.thickness=.006
    for poly in mesh.polygons:
        poly.use_smooth=True

cloth_mesh('Towel_front',.30,.63,(-.21,-.07,1.78),0)
cloth_mesh('Towel_back',.27,.47,(-.14,.01,1.78),1.2)

textcurve=bpy.data.curves.new('Filter_label','FONT')
textcurve.body='FILTER'
textcurve.size=.038
textcurve.extrude=.0001
label=bpy.data.objects.new('Filter_label',textcurve)
bpy.context.collection.objects.link(label)
label.location=(.319,JY-.123,1.01)
label.rotation_euler=(math.pi/2,0,0)
ink=bpy.data.materials.new('Faded_marker')
ink.diffuse_color=(.20,.22,.18,1)
label.data.materials.append(ink)
label.parent=bpy.data.objects.get('water_jug')

# Give metallic components a subdued satin reflection.
for group in ('sink','paper_roll','towel_fixture'):
    for ob in meshes_under(group):
        for slot in ob.material_slots:
            mat=slot.material
            if mat is None:
                continue
            rgb=mat.diffuse_color
            if abs(rgb[0]-metal[0])<.025 and abs(rgb[1]-metal[1])<.025:
                mat=mat.copy()
                slot.material=mat
                mat.use_nodes=True
                bs=mat.node_tree.nodes.get('Principled BSDF')
                if bs:
                    bs.inputs['Metallic'].default_value=.72
                    bs.inputs['Roughness'].default_value=.30

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.66,.70,.73,1)
sc.world.node_tree.nodes['Background'].inputs[1].default_value=.22
set_view(CAMERA,TARGET,lens=LENS,sensor=36,shift=SHIFT)
area_emitter((-1.5,-.20,2.55),power=190,size=1.8,
             target=(.25,.35,1.45),color=(.83,.91,1))
area_emitter((-.25,-2,2.8),power=70,size=2.6,
             target=(.15,.35,1.5),color=(1,.82,.57))
sc.view_settings.view_transform='AgX'
