from sceneact import *
import bpy, math

# Reference landmarks: roll (.61,.09)-(.83,.42), towel (.26,.48)-(.46,.83),
# cabinet lower edge (.40,.52)-(.83,.47), jug (.59,.65)-(.78,.89).
# Three largest discrepancies in step 1:
# 1. Opaque return wall hid the window: replace it with an open framed window.
# 2. Counter objects sat too high and sink extended too far right:
#    lower countertop/appliance assembly .12m, move sink .22m left.
# 3. Broad tones were washed out; reduce lights and use explicitly named stone meshes.
# Also enlarge paper roll and pitcher, and broaden/lengthen the hanging towel.
# Preserve camera and cabinet framing; depth and cloth width remain uncertain.
CAMERA=(-1.22,-2.65,1.88)
TARGET=(-.10,-.02,1.46)
LENS=48
COUNTER_Z=.74
DROP=-.12
scene=Scene('Kitchen corner')
paint=(.73,.65,.49)
cream=(.69,.61,.45)
paper=(.88,.83,.70)
chrome=(.43,.42,.35)
black=(.016,.020,.017)
blue=(.018,.045,.115)

def add(parent,name,node):
    node.name=name+'_mesh'
    parent.include(name,node)
    return node

architecture=Asset('Architecture')
add(architecture,'rear_wall',box((3,.07,3),center=(0,.48,1.5),color=(.70,.64,.51)))
# No wall across the visible glass aperture.
add(architecture,'window_rear_post',box((.075,.12,3),center=(-.89,.49,1.5),color=paint))
scene.include('architecture',architecture)

counter=Asset('Counter and sink')
add(counter,'stone',box((2.8,1.65,.065),center=(-.12,-.30,.8275),color=(.28,.25,.19)))
add(counter,'backsplash',box((2.8,.035,.115),center=(-.12,.425,.917),color=(.28,.25,.19)))
# Dark inset basin; a real opening prevents a countertop-colored basin.
# The cutout and basin are simple independent, editable components.
counter.remove('stone')
stone=box((2.8,1.65,.065),center=(-.12,-.30,.8275),color=(.28,.25,.19))
cut=box((.67,.55,.30),center=(-.86,-.62,.84))
add(counter,'stone',subtract(stone,cut))
add(counter,'sink_dark',fillet_box((.67,.55,.16),radius=.065,
    center=(-.86,-.62,.755),color=(.012,.019,.015)))
for name,size,pos in [
    ('back_rim',(.76,.025,.018),(-.86,-.345,.869)),
    ('right_rim',(.025,.59,.018),(-.495,-.62,.869)),
    ('left_rim',(.025,.59,.018),(-1.225,-.62,.869)),
    ('front_rim',(.76,.025,.018),(-.86,-.90,.869))]:
    add(counter,name,box(size,center=pos,color=chrome))
counter.move((0,0,DROP))
scene.include('counter',counter)

window=Asset('Window and Venetian blinds')
add(window,'glass',box((.018,1.44,2.0),center=(-.91,-.28,1.85),color=(.47,.66,.70)))
for y in (-1.02,.45):
    add(window,'jamb_'+str(y),box((.075,.045,2.12),center=(-.86,y,1.85),color=paper))
for z in (.81,2.89):
    add(window,'frame_'+str(z),box((.075,1.51,.05),center=(-.86,-.28,z),color=paper))
add(window,'middle_mullion',box((.06,.035,2),center=(-.85,-.30,1.85),color=paper))
for i in range(39):
    z=.84+i*.054
    slat=box((.085,1.46,.013),center=(-.79,-.28,z),color=(.76,.77,.67))
    slat.turn('y',-12)
    add(window,'blind_%02d'%i,slat)
for y in (-.65,.22):
    add(window,'ladder_'+str(y),rod(.0028,start=(-.735,y,.84),end=(-.735,y,2.90),color=(.73,.73,.61)))
add(window,'pull_cord',rod(.002,start=(-.72,-.49,1.63),end=(-.72,-.49,.96),color=paper))
scene.include('window',window)

cabinet=Asset('Upper cream cabinet')
add(cabinet,'carcass',box((.86,.43,1.36),center=(.185,.205,2.11),color=cream))
add(cabinet,'left_cheek',box((.028,.45,1.39),center=(-.255,.195,2.125),color=paint))
add(cabinet,'bottom',box((.90,.47,.045),center=(.185,.185,1.43),color=paint))
add(cabinet,'door',box((.79,.035,1.35),center=(.205,-.031,2.12),color=paint))
for name,size,pos in [
    ('left_stile',(.055,.025,1.33),(-.16,-.058,2.12)),
    ('right_stile',(.055,.025,1.33),(.57,-.058,2.12)),
    ('bottom_rail',(.73,.025,.065),(.205,-.058,1.487)),
    ('top_rail',(.73,.025,.065),(.205,-.058,2.753))]:
    add(cabinet,name,box(size,center=pos,color=(.77,.69,.51)))
add(cabinet,'center_panel',box((.64,.012,1.165),center=(.205,-.054,2.12),color=(.71,.63,.46)))
add(cabinet,'door_knob_stem',rod(.012,start=(.55,-.075,1.665),end=(.55,-.105,1.665),color=chrome))
add(cabinet,'door_knob',ball(.019,center=(.55,-.115,1.665),color=chrome))
scene.include('cabinet',cabinet)

roll=Asset('Mounted paper towel roll')
RX=.21
add(roll,'back_mount',rod(.027,start=(RX,-.075,1.66),end=(RX,-.20,1.66),color=chrome))
add(roll,'spindle',rod(.018,start=(RX,-.205,1.60),end=(RX,-.205,2.30),color=chrome))
add(roll,'paper_cylinder',rod(.151,length=.60,center=(RX,-.205,1.978),color=paper))
add(roll,'top_finial',resized(ball(.026,center=(RX,-.205,2.316),color=chrome),(1,1,1.4)))
add(roll,'bottom_support',rod(.019,start=(RX-.14,-.205,1.66),end=(RX+.14,-.205,1.66),color=chrome))
scene.include('paper_roll',roll)

towel=Asset('Towel ring and towel')
add(towel,'mount_plate',rod(.042,start=(-.277,.045,1.72),end=(-.300,.045,1.72),color=chrome))
add(towel,'mount_neck',rod(.015,start=(-.30,.045,1.72),end=(-.355,.045,1.72),color=chrome))
pts=[(-.366,.045+.105*math.cos(2*math.pi*i/48),
      1.59+.137*math.sin(2*math.pi*i/48)) for i in range(49)]
add(towel,'ring',sweep_tube(points=pts,radius=.006,color=chrome))
scene.include('towel',towel)

faucet=Asset('Sink faucet')
FX=-.76
add(faucet,'mount',rod(.038,length=.023,center=(FX,-.40,.882),color=chrome))
add(faucet,'stem',rod(.012,start=(FX,-.40,.89),end=(FX,-.40,1.15),color=chrome))
add(faucet,'spout',sweep_tube(points=[
    (FX,-.40,1.14),(FX,-.405,1.19),(FX,-.435,1.205),
    (FX,-.48,1.18),(FX,-.50,1.13)],radius=.011,color=chrome))
for x in (FX-.105,FX+.10):
    add(faucet,'valve_'+str(x),rod(.024,length=.04,center=(x,-.40,.885),color=chrome))
    add(faucet,'lever_'+str(x),rod(.008,start=(x,-.40,.91),end=(x+.04,-.44,.94),color=chrome))
faucet.move((0,0,DROP))
scene.include('faucet',faucet)

blender=Asset('Small black blender')
BX=-.015
add(blender,'base',fillet_box((.17,.18,.18),radius=.025,center=(BX,.08,.95),color=black))
add(blender,'motor_top',rod(.069,length=.045,center=(BX,.08,1.053),color=black))
jar=Part('Clear blending cup')
add(jar,'jar',rod(.048,length=.28,center=(BX,.08,1.21),color=(.34,.37,.31),opacity=.35))
add(jar,'rim',rod(.050,length=.008,center=(BX,.08,1.354),color=chrome))
jar.turn('y',-12,pivot=(BX,.08,1.05))
add(blender,'cup',jar)
blender.move((0,0,DROP))
scene.include('blender',blender)

can=Asset('Metal counter canister')
add(can,'body',rod(.055,length=.20,center=(-.28,.045,.965),color=(.30,.32,.15)))
add(can,'lid',rod(.060,length=.015,center=(-.28,.045,1.071),color=chrome))
add(can,'label',box((.045,.006,.085),center=(-.28,-.013,.948),color=(.61,.60,.45)))
can.move((0,0,DROP))
scene.include('canister',can)

jug=Asset('Filtered water gallon')
jx,jy=.22,-.19
add(jug,'body',fillet_box((.26,.235,.27),radius=.055,center=(jx,jy,1.005),color=(.62,.65,.58)))
add(jug,'shoulder',resized(ball(.137,center=(jx,jy,1.135),color=(.65,.67,.59)),(1,.87,.88)))
add(jug,'neck',rod(.038,length=.06,center=(jx,jy,1.24),color=(.73,.75,.65)))
add(jug,'cap',rod(.040,length=.023,center=(jx,jy,1.275),color=(.78,.79,.69)))
add(jug,'handle',sweep_tube(points=[
    (jx+.075,jy,1.205),(jx+.125,jy,1.185),
    (jx+.145,jy,1.135),(jx+.125,jy,1.09)],radius=.018,color=(.66,.69,.61)))
jug.move((-.025,0,DROP))
scene.include('gallon',jug)

pitcher=Asset('Blue water filter pitcher')
px,py=.55,.10
add(pitcher,'blue_reservoir',rod(.116,length=.355,center=(px,py,1.065),color=blue))
add(pitcher,'foot',rod(.105,length=.025,center=(px,py,.88),color=(.055,.08,.105)))
lid=resized(ball(.13,center=(px,py,1.253),color=(.29,.30,.26)),(1,1,.18))
lid.turn('y',12)
add(pitcher,'sloping_lid',lid)
add(pitcher,'spout',box((.075,.07,.045),center=(px-.104,py,1.25),color=(.28,.29,.25)))
pts=[]
for i in range(25):
    a=-math.pi/2+math.pi*i/24
    pts.append((px+.112+.092*math.cos(a),py-.003,1.065+.18*math.sin(a)))
add(pitcher,'clear_handle',sweep_tube(points=pts,radius=.017,color=(.39,.43,.39),opacity=.62))
pitcher.move((0,0,DROP))
scene.include('pitcher',pitcher)

dish=Asset('Soap dish')
add(dish,'tray',fillet_box((.20,.11,.022),radius=.01,center=(-1.0,-.43,.884),color=chrome))
add(dish,'soap',fillet_box((.11,.065,.03),radius=.013,center=(-1.0,-.43,.907),color=(.72,.70,.47)))
dish.move((0,0,DROP))
scene.include('soap_dish',dish)

realize(scene)

def mat(name,col,rough=.6,metal=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    m.diffuse_color=(*col,1)
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*col,1)
    p.inputs['Roughness'].default_value=rough
    p.inputs['Metallic'].default_value=metal
    return m

def assign_mesh_name(prefix,material):
    for o in bpy.data.objects:
        if o.type=='MESH' and (o.name==prefix or o.name.startswith(prefix+'.')):
            o.data.materials.clear()
            o.data.materials.append(material)

granite=mat('Brown grey finely mottled granite',(.24,.22,.17),.8)
nt=granite.node_tree
p=nt.nodes.get('Principled BSDF')
tex=nt.nodes.new('ShaderNodeTexNoise')
tex.inputs['Scale'].default_value=155
tex.inputs['Detail'].default_value=3
ramp=nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.26
ramp.color_ramp.elements[0].color=(.045,.039,.028,1)
ramp.color_ramp.elements[1].position=.75
ramp.color_ramp.elements[1].color=(.40,.36,.27,1)
nt.links.new(tex.outputs['Fac'],ramp.inputs[0])
nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
b=nt.nodes.new('ShaderNodeBump')
b.inputs['Strength'].default_value=.18
b.inputs['Distance'].default_value=.0015
nt.links.new(tex.outputs['Fac'],b.inputs['Height'])
nt.links.new(b.outputs[0],p.inputs['Normal'])
assign_mesh_name('stone_mesh',granite)
assign_mesh_name('backsplash_mesh',granite)

metal=mat('Warm brushed nickel',(.38,.36,.29),.24,.78)
for prefix in ('mount_mesh','stem_mesh','spout_mesh','mount_plate_mesh',
               'mount_neck_mesh','ring_mesh','top_finial_mesh',
               'bottom_support_mesh','door_knob_mesh','door_knob_stem_mesh',
               'back_rim_mesh','right_rim_mesh','front_rim_mesh','left_rim_mesh'):
    assign_mesh_name(prefix,metal)

# Soft cloth folds are a separate mesh attached to the towel assembly.
cloth=mat('Ivory terry cloth',(.79,.75,.64),.96)
nt=cloth.node_tree
n=nt.nodes.new('ShaderNodeTexNoise')
n.inputs['Scale'].default_value=200
b=nt.nodes.new('ShaderNodeBump')
b.inputs['Strength'].default_value=.2
b.inputs['Distance'].default_value=.0013
nt.links.new(n.outputs['Fac'],b.inputs['Height'])
nt.links.new(b.outputs[0],nt.nodes.get('Principled BSDF').inputs['Normal'])
verts=[]; faces=[]
nu,nv=24,34
for j in range(nv):
    t=j/(nv-1)
    for i in range(nu):
        u=i/(nu-1)
        width=.22+.09*math.sin(math.pi*t*.85)
        y=.025+(u-.5)*width-.08*t
        x=-.395-.035*math.sin(u*math.pi*6+.6*t)-.033*t
        z=1.477-.59*t+.027*math.sin(u*7)*t*t
        verts.append((x,y,z))
for j in range(nv-1):
    for i in range(nu-1):
        a=j*nu+i
        faces.append((a,a+1,a+1+nu,a+nu))
mesh=bpy.data.meshes.new('Towel fabric')
mesh.from_pydata(verts,[],faces)
mesh.update()
obj=bpy.data.objects.new('Hanging ivory towel',mesh)
bpy.context.collection.objects.link(obj)
obj.data.materials.append(cloth)
obj.parent=bpy.data.objects.get('towel')
for f in mesh.polygons:
    f.use_smooth=True
mod=obj.modifiers.new('Fabric thickness','SOLIDIFY')
mod.thickness=.004
mod=obj.modifiers.new('Soft folds','SUBSURF')
mod.levels=1

ink=mat('Faded marker',(.20,.24,.19),.9)
curve=bpy.data.curves.new('Filter marking','FONT')
curve.body='FILTER'
curve.size=.025
curve.extrude=.0001
ob=bpy.data.objects.new('FILTER label',curve)
bpy.context.collection.objects.link(ob)
ob.location=(jx-.097,jy-.120,.935+DROP)
ob.rotation_euler=(math.pi/2,0,0)
curve.materials.append(ink)

# Cool outdoor glass supplies the visible blue strips behind the blinds.
glassmat=mat('Daylight beyond window',(.40,.63,.70),.7)
gp=glassmat.node_tree.nodes.get('Principled BSDF')
gp.inputs['Emission Color'].default_value=(.48,.70,.79,1)
gp.inputs['Emission Strength'].default_value=.65
assign_mesh_name('glass_mesh',glassmat)

for o in bpy.data.objects:
    if o.type=='MESH' and ('paper_cylinder_mesh' in o.name or
        'blue_reservoir_mesh' in o.name or 'shoulder_mesh' in o.name):
        for f in o.data.polygons:
            f.use_smooth=True

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.67,.69,.72,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.20
set_view(CAMERA,TARGET,lens=LENS)
area_emitter((-.67,-.30,2.15),power=90,size=1.45,
    target=(.18,.03,1.25),color=(.88,.93,1))
area_emitter((-.15,-2,2.6),power=32,size=2.5,
    target=(.1,0,1.45),color=(1,.79,.52))
sc.view_settings.view_transform='AgX'
# Audit: positive dimensions/radii, valid fillets, nonduplicate tube neighbors,
# unique attachment keys, camera/lights/material edits occur after realize.
# Fixed runner handles rendering and saving.
