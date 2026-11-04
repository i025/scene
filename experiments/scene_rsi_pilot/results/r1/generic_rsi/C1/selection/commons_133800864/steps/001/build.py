from sceneact import *
import bpy, math, random
from mathutils import Vector

# Approximate image landmarks (u,v):
# window/cabinet boundary (.29,.00)-(.39,.52), cabinet bottom (.40,.52)-(.83,.47)
# roll (.61,.09)-(.83,.42), towel (.26,.48)-(.46,.83)
# gallon (.59,.65)-(.78,.89), pitcher (.73,.60)-(.97,.85)
# sink enters lower left; counter occupies most of the bottom quarter.
# Camera is left of the cabinet, slightly above the counter, looking downward.
# Cabinet depth and the window's angle to the rear wall are the main uncertainties.
CAMERA = (-1.22, -2.65, 1.88)
TARGET = (-.10, -.02, 1.46)
LENS = 48
COUNTER_Z = .86
CABINET_BOTTOM = 1.43
LIGHT_POWER = 420

scene = Scene('Kitchen corner')
cream = (.73,.66,.49)
paint = (.82,.76,.61)
paper = (.91,.87,.76)
chrome = (.48,.47,.39)
black = (.022,.025,.021)
blue = (.025,.065,.15)

def add(parent, name, node):
    parent.include(name, node)
    return node

architecture = Asset('Architecture')
add(architecture, 'rear_wall',
    box((3,.07,3.0), center=(0,.48,1.5), color=paint))
add(architecture, 'left_wall',
    box((.07,1.25,3.0), center=(-.89,-.10,1.5), color=paint))
scene.include('architecture', architecture)

counter = Asset('Counter and sink')
add(counter,'stone',
    box((2.2,1.31,.065), center=(0,-.185,COUNTER_Z-.0325),
        color=(.34,.31,.23)))
add(counter,'backsplash',
    box((2.2,.035,.115), center=(0,.425,.917),color=(.34,.31,.23)))
# A dark basin entering the cropped foreground.
add(counter,'sink_dark',
    fillet_box((.67,.55,.16), radius=.065,
               center=(-.64,-.62,.793), color=(.025,.035,.029)))
for name, size, pos in [
    ('back_rim',(.76,.035,.018),(-.64,-.345,.869)),
    ('right_rim',(.035,.59,.018),(-.275,-.62,.869)),
    ('left_rim',(.035,.59,.018),(-1.005,-.62,.869)),
    ('front_rim',(.76,.035,.018),(-.64,-.90,.869))]:
    add(counter,name,box(size,center=pos,color=chrome))
scene.include('counter',counter)

window = Asset('Window and Venetian blinds')
# Window is on the return wall; the narrow strips expose cool outdoor light.
add(window,'glass',
    box((.018,1.04,1.65),center=(-.842,-.115,1.765),
        color=(.57,.72,.76)))
for y in (-.655,.425):
    add(window,'jamb_'+str(y),
        box((.075,.05,1.77),center=(-.81,y,1.77),color=(.88,.86,.75)))
for z in (.91,2.62):
    add(window,'frame_'+str(z),
        box((.075,1.12,.055),center=(-.81,-.115,z),color=paper))
add(window,'middle_mullion',
    box((.055,.035,1.65),center=(-.795,-.13,1.765),color=paper))
for i in range(31):
    z=.945+i*.054
    slat=box((.082,1.075,.014),center=(-.775,-.115,z),
             color=(.83,.83,.73))
    slat.turn('y',-12)
    add(window,'blind_%02d'%i,slat)
for y in (-.50,.24):
    add(window,'ladder_front_'+str(y),
        rod(.0028,start=(-.722,y,.93),end=(-.722,y,2.64),color=(.81,.80,.68)))
add(window,'pull_cord',rod(.002,start=(-.704,-.49,1.61),
                          end=(-.704,-.49,.96),color=paper))
scene.include('window',window)

cabinet = Asset('Upper cream cabinet')
# Left cheek remains visible to the left of the inset front door.
add(cabinet,'carcass',
    box((.86,.43,1.13),center=(.185,.205,1.995),color=cream))
add(cabinet,'left_cheek',
    box((.028,.45,1.16),center=(-.255,.195,2.01),color=paint))
add(cabinet,'bottom',
    box((.90,.47,.045),center=(.185,.185,CABINET_BOTTOM),color=paint))
add(cabinet,'door',
    box((.79,.035,1.12),center=(.205,-.031,2.005),color=paint))
# Raised perimeter around a subtly recessed central panel.
for name,size,pos in [
    ('left_stile',(.055,.025,1.10),(-.16,-.058,2.005)),
    ('right_stile',(.055,.025,1.10),(.57,-.058,2.005)),
    ('bottom_rail',(.73,.025,.065),(.205,-.058,1.487)),
    ('top_rail',(.73,.025,.065),(.205,-.058,2.523))]:
    add(cabinet,name,box(size,center=pos,color=(.85,.78,.61)))
add(cabinet,'center_panel',
    box((.64,.012,.935),center=(.205,-.054,2.005),color=(.79,.72,.56)))
add(cabinet,'door_knob_stem',
    rod(.012,start=(.55,-.075,1.665),end=(.55,-.105,1.665),color=chrome))
add(cabinet,'door_knob',ball(.019,center=(.55,-.115,1.665),color=chrome))
scene.include('cabinet',cabinet)

roll = Asset('Mounted paper towel roll')
add(roll,'back_mount',
    rod(.027,start=(.255,-.075,1.66),end=(.255,-.20,1.66),color=chrome))
add(roll,'spindle',
    rod(.018,start=(.255,-.205,1.60),end=(.255,-.205,2.20),color=chrome))
add(roll,'paper_cylinder',
    rod(.133,length=.515,center=(.255,-.205,1.925),color=paper))
add(roll,'top_finial',
    resized(ball(.026,center=(.255,-.205,2.223),color=chrome),(1,1,1.4)))
add(roll,'bottom_support',
    rod(.019,start=(.12,-.205,1.655),end=(.39,-.205,1.655),color=chrome))
scene.include('paper_roll',roll)

towel = Asset('Towel ring and towel')
# Ring lies on the exposed left cheek of the cabinet.
add(towel,'mount_plate',
    rod(.042,start=(-.277,.045,1.72),end=(-.300,.045,1.72),color=chrome))
add(towel,'mount_neck',
    rod(.015,start=(-.30,.045,1.72),end=(-.355,.045,1.72),color=chrome))
ring_points=[]
for i in range(65):
    a=2*math.pi*i/64
    ring_points.append((-.366,.045+.105*math.cos(a),1.59+.137*math.sin(a)))
add(towel,'ring',sweep_tube(points=ring_points,radius=.006,color=chrome))
scene.include('towel',towel)

faucet=Asset('Sink faucet')
add(faucet,'mount',rod(.038,length=.023,center=(-.65,-.40,.882),color=chrome))
add(faucet,'stem',rod(.014,start=(-.65,-.40,.89),end=(-.65,-.40,1.14),color=chrome))
add(faucet,'spout',sweep_tube(points=[
    (-.65,-.40,1.13),(-.65,-.405,1.18),(-.65,-.435,1.20),
    (-.65,-.48,1.18),(-.65,-.50,1.13)],radius=.012,color=chrome))
for x in (-.755,-.55):
    add(faucet,'valve_'+str(x),rod(.024,length=.04,center=(x,-.40,.885),color=chrome))
    add(faucet,'lever_'+str(x),rod(.008,start=(x,-.40,.91),end=(x+.04,-.44,.94),color=chrome))
scene.include('faucet',faucet)

blender=Asset('Small black blender')
add(blender,'base',fillet_box((.17,.18,.16),radius=.025,
                             center=(-.08,.08,.94),color=black))
add(blender,'motor_top',rod(.069,length=.045,center=(-.08,.08,1.033),color=black))
jar=Part('Clear blending cup')
add(jar,'jar',rod(.054,length=.26,center=(-.08,.08,1.18),
                  color=(.57,.60,.54),opacity=.30))
add(jar,'rim',rod(.056,length=.012,center=(-.08,.08,1.316),color=chrome))
jar.turn('y',-12,pivot=(-.08,.08,1.05))
add(blender,'cup',jar)
scene.include('blender',blender)

can=Asset('Metal counter canister')
add(can,'body',rod(.055,length=.20,center=(-.28,.045,.965),color=(.39,.40,.22)))
add(can,'lid',rod(.060,length=.015,center=(-.28,.045,1.071),color=chrome))
add(can,'label',box((.045,.006,.085),center=(-.28,-.013,.948),color=(.71,.69,.55)))
scene.include('canister',can)

jug=Asset('Filtered water gallon')
jug_x,jug_y=.22,-.19
add(jug,'body',fillet_box((.26,.235,.235),radius=.055,
                          center=(jug_x,jug_y,.987),color=(.73,.75,.67)))
add(jug,'shoulder',
    resized(ball(.137,center=(jug_x,jug_y,1.10),color=(.75,.76,.68)),(1,.87,.83)))
add(jug,'neck',rod(.038,length=.060,center=(jug_x,jug_y,1.205),color=(.80,.81,.72)))
add(jug,'cap',rod(.040,length=.023,center=(jug_x,jug_y,1.24),color=(.86,.86,.77)))
# Molded handle on the upper right shoulder.
handle_pts=[(jug_x+.075,jug_y,1.17),(jug_x+.125,jug_y,1.15),
            (jug_x+.145,jug_y,1.10),(jug_x+.125,jug_y,1.055)]
add(jug,'handle',sweep_tube(points=handle_pts,radius=.018,color=(.77,.78,.70)))
scene.include('gallon',jug)

pitcher=Asset('Blue water filter pitcher')
px,py=.52,.10
add(pitcher,'blue_reservoir',
    rod(.116,length=.28,center=(px,py,1.025),color=blue,opacity=.82))
add(pitcher,'foot',rod(.105,length=.025,center=(px,py,.88),color=(.09,.13,.17)))
lid=resized(ball(.13,center=(px,py,1.174),color=(.39,.40,.34)),(1,1,.18))
lid.turn('y',12)
add(pitcher,'sloping_lid',lid)
add(pitcher,'spout',
    box((.075,.07,.045),center=(px-.104,py,1.17),color=(.38,.39,.33)))
handle=[]
for i in range(33):
    a=-math.pi/2 + math.pi*i/32
    handle.append((px+.112+.092*math.cos(a),py-.003,1.025+.142*math.sin(a)))
add(pitcher,'clear_handle',sweep_tube(points=handle,radius=.017,
                                    color=(.53,.56,.51),opacity=.52))
scene.include('pitcher',pitcher)

# Small foreground soap dish, cropped with the sink.
dish=Asset('Soap dish')
add(dish,'tray',fillet_box((.20,.11,.022),radius=.01,
                           center=(-.92,-.43,.884),color=chrome))
add(dish,'soap',fillet_box((.11,.065,.03),radius=.013,
                          center=(-.92,-.43,.907),color=(.76,.75,.51)))
scene.include('soap_dish',dish)

realize(scene)

def meshes_under(name):
    root=bpy.data.objects.get(name)
    if not root:
        return []
    return [o for o in [root]+list(root.children_recursive) if o.type=='MESH']

def material(name,color,roughness=.5,metallic=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    p.inputs['Metallic'].default_value=metallic
    return m

# Fine mottled stone, using generated coordinates rather than image textures.
granite=material('Warm speckled granite',(.32,.29,.23),.75)
nt=granite.node_tree
p=nt.nodes.get('Principled BSDF')
noise=nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value=175
noise.inputs['Detail'].default_value=2.5
ramp=nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.25
ramp.color_ramp.elements[0].color=(.075,.068,.049,1)
ramp.color_ramp.elements[1].position=.77
ramp.color_ramp.elements[1].color=(.59,.55,.43,1)
nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
bump=nt.nodes.new('ShaderNodeBump')
bump.inputs['Strength'].default_value=.22
bump.inputs['Distance'].default_value=.0018
nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
nt.links.new(bump.outputs[0],p.inputs['Normal'])
for name in ('stone','backsplash'):
    for o in meshes_under(name):
        o.data.materials.clear()
        o.data.materials.append(granite)

metal=material('Brushed warm nickel',(.48,.46,.38),.25,.78)
for name in ('faucet','mount_plate','mount_neck','ring','top_finial',
             'bottom_support','door_knob','door_knob_stem'):
    for o in meshes_under(name):
        o.data.materials.clear()
        o.data.materials.append(metal)

# A separate cloth surface: softly corrugated folds and an uneven hem.
clothmat=material('Ivory terry cloth',(.83,.80,.69),.95)
cn=clothmat.node_tree.nodes.new('ShaderNodeTexNoise')
cn.inputs['Scale'].default_value=210
cb=clothmat.node_tree.nodes.new('ShaderNodeBump')
cb.inputs['Strength'].default_value=.24
cb.inputs['Distance'].default_value=.0015
clothmat.node_tree.links.new(cn.outputs['Fac'],cb.inputs['Height'])
clothmat.node_tree.links.new(cb.outputs[0],
    clothmat.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
verts=[]; faces=[]
nu,nv=22,32
for j in range(nv):
    t=j/(nv-1)
    for i in range(nu):
        u=i/(nu-1)
        width=.18+.07*math.sin(math.pi*t*.85)
        y=.023+(u-.5)*width-.06*t
        x=-.385-.025*math.sin(u*math.pi*6+.6*t)-.025*t
        z=1.477-.493*t+.025*math.sin(u*7)*t*t
        if t<.12:
            x-=.025*math.sin(t/.12*math.pi)
        verts.append((x,y,z))
for j in range(nv-1):
    for i in range(nu-1):
        a=j*nu+i
        faces.append((a,a+1,a+1+nu,a+nu))
mesh=bpy.data.meshes.new('Hanging towel fabric mesh')
mesh.from_pydata(verts,[],faces)
mesh.update()
obj=bpy.data.objects.new('Hanging ivory towel',mesh)
bpy.context.collection.objects.link(obj)
obj.data.materials.append(clothmat)
obj.parent=bpy.data.objects.get('towel')
for poly in mesh.polygons:
    poly.use_smooth=True
solid=obj.modifiers.new('Fabric thickness','SOLIDIFY')
solid.thickness=.004
sub=obj.modifiers.new('Soft folds','SUBSURF')
sub.levels=1

# Handwritten front marking on the jug.
ink=material('Faded marker',(.24,.28,.24),.9)
curve=bpy.data.curves.new('Filter marking','FONT')
curve.body='FILTER'
curve.size=.026
curve.extrude=.0001
text_obj=bpy.data.objects.new('FILTER handwritten label',curve)
bpy.context.collection.objects.link(text_obj)
text_obj.location=(jug_x-.072,jug_y-.120,.947)
text_obj.rotation_euler=(math.pi/2,0,0)
curve.materials.append(ink)

# Smooth cylindrical small appliances and paper roll.
for name in ('paper_roll','gallon','pitcher','blender','canister'):
    for o in meshes_under(name):
        for f in o.data.polygons:
            f.use_smooth=True

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes=True
sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.66,.69,.72,1)
sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
set_view(CAMERA,TARGET,lens=LENS)
area_emitter((-1.05,-.20,2.20),power=LIGHT_POWER,size=1.6,
             target=(.15,.05,1.25),color=(.84,.91,1))
area_emitter((-.15,-2.0,2.6),power=110,size=2.5,
             target=(.1,0,1.45),color=(1,.83,.60))
sc.view_settings.view_transform='AgX'
# All primitives have positive dimensions; tube paths have distinct neighbors.
# Rendering and file output are intentionally left to the fixed runner.
