import bpy, math
from mathutils import Vector
from sceneact import *

# Reference inventory, normalized bounds:
# Oak rear slats (0,.12)-(.46,.76), white door (.31,.29)-(.45,.77),
# low black bench (0,.65)-(.20,.80), pale tiled floor below y=.76.
# Marble counter (.36,.59)-(.87,1), black hob (.39,.77)-(.79,1),
# dark inset sink (.46,.64)-(.62,.71), walnut cupboards (.46,0)-(1,.44),
# glossy cream backsplash (.58,.28)-(1,.94), extractor and warm light strip.
# Small visible parts: lever, keyhole, two electrical plates, draining grooves.
# Cabinet interiors and plumbing are occluded and remain unspecified.
# Anchors: slat top y=.12; door bottom y=.77; door sides x=.31/.45;
# counter far left (.45,.60), foreground left (.36,1); cabinet end x=.46.
#
# Revision evidence: rear framing and counter left contour are already close.
# Door top is too high, sink appears as a narrow distant slit, and upper
# cupboards end too high. Material assignment by Blender object names failed:
# realized meshes have generic names, leaving important finishes uncontrolled.
# Keep camera and rear slats fixed. Locally shorten the door, lower/narrow
# upper cabinets, and lengthen/move the sink slightly toward the camera.
# Assign materials by recorded primitive centers, preserving semantic groups.
# Expected effects: door top descends, sink opening gains projected depth,
# dark cupboards occupy the upper-right region, hob reads as black glass.
# Attribution is mixed between local geometry and material/lighting corrections.
# Door bottom, floor contacts, counter silhouette and rear slat anchors stay fixed.
# Estimated expansion: about 245 primitive meshes, including 47 slats,
# 32 tiles and 96 burner segments. No booleans or fillet expansions.

scene = Scene('Warm narrow kitchen')
records = []

def asset(name):
    a = Asset(name)
    scene.include(name, a)
    return a

def block(a, name, size, center, color, finish=None):
    n = box(size=size, center=center, color=color)
    a.include(name, n)
    records.append((Vector(center), color, finish, name))
    return n

def bar(a, name, p, q, r, color, finish=None):
    n = rod(radius=r, start=p, end=q, color=color)
    a.include(name, n)
    records.append(((Vector(p)+Vector(q))*.5, color, finish, name))
    return n

cream=(.78,.77,.72)
white=(.78,.80,.78)
oak=(.29,.125,.043)
darkwood=(.075,.028,.010)
black=(.006,.008,.007)
stone=(.65,.60,.50)

arch=asset('Room architecture')
block(arch,'Floor base',(7,8,.08),(-1,0,-.06),(.36,.34,.30))
block(arch,'Rear plaster wall',(5.4,.12,3.2),(-1.9,2.55,1.56),cream)
block(arch,'Glossy backsplash wall',(.12,7,3.2),(.66,-.6,1.56),
      (.77,.77,.72),'backsplash')
block(arch,'Ceiling',(6.5,7,.10),(-1.9,-.2,3.14),(.80,.79,.75))

floor=asset('Rectangular porcelain floor tiles')
for iy in range(8):
    for ix in range(4):
        x=-3.15+ix*.94+(.47 if iy%2 else 0)
        v=.012*((ix+iy)%3)
        block(floor,f'Tile {iy} {ix}',(.932,.66,.013),
              (x,-2.25+iy*.67,-.009),(.42+v,.40+v,.355+v),'tile')

slats=asset('Rear vertical oak screen')
block(slats,'Dark backing',(3.65,.035,2.63),(-2.02,2.467,1.405),
      (.038,.022,.012))
for i in range(47):
    block(slats,f'Oak batten {i}',(.048,.071,2.63),
          (-3.8+i*.078,2.414,1.405),oak,'oak')
block(slats,'Bottom trim',(3.65,.085,.055),(-2.02,2.41,.065),
      (.20,.095,.034),'oak')

door=asset('White rear door and fittings')
block(door,'Door surround',(.855,.065,1.98),(-.77,2.36,.99),(.84,.84,.80))
block(door,'Door leaf',(.738,.045,1.88),(-.77,2.314,.962),white)
block(door,'Upper reveal',(.738,.008,.009),(-.77,2.284,1.901),(.50,.52,.50))
block(door,'Right reveal',(.009,.008,1.88),(-.399,2.284,.962),(.43,.45,.43))
block(door,'Handle escutcheon',(.033,.018,.085),(-1.065,2.279,1.035),
      (.38,.40,.38),'metal')
bar(door,'Lever handle',(-1.065,2.246,1.058),(-.952,2.246,1.058),
    .009,(.30,.32,.30),'metal')
bar(door,'Keyhole',(-1.063,2.264,.972),(-1.063,2.247,.972),
    .008,(.12,.13,.12))

switches=asset('Rear electrical fittings')
block(switches,'Light switch',(.092,.021,.075),(-1.36,2.355,1.085),
      (.86,.86,.80))
block(switches,'Low socket',(.070,.021,.078),(-1.33,2.355,.31),
      (.86,.86,.80))

bench=asset('Low black bench with white front')
block(bench,'Carcass',(.99,.40,.46),(-2.39,2.14,.245),(.012,.016,.013))
block(bench,'White inset front',(.91,.018,.31),(-2.39,1.927,.239),
      (.76,.79,.76))
block(bench,'Top slab',(1.04,.43,.055),(-2.39,2.12,.493),black,'glass')
block(bench,'Right side',(.055,.43,.44),(-1.882,2.12,.25),(.014,.017,.013))

lower=asset('Base kitchen cabinets')
block(lower,'Cabinet body',(.83,3.92,.79),(.20,-.28,.43),(.50,.46,.38))
block(lower,'Recessed plinth',(.72,3.86,.10),(.24,-.28,.065),(.06,.045,.03))
for i,y in enumerate([-1.65,-.8,.05,.90]):
    block(lower,f'Cabinet front {i}',(.027,.825,.715),
          (-.229,y,.452),(.57,.53,.44))

counter=asset('Marble worktop surrounding sink opening')
block(counter,'Front long stone strip',(.155,3.95,.058),
      (-.192,-.29,.872),stone,'stone')
block(counter,'Wall long stone strip',(.147,3.95,.058),
      (.556,-.29,.872),stone,'stone')
block(counter,'Near worktop',(.67,2.745,.058),
      (.22,-.8925,.872),stone,'stone')
block(counter,'Back worktop',(.67,.37,.058),
      (.22,1.50,.872),stone,'stone')

sink=asset('Inset sink and draining board')
sy=.895
block(sink,'Metal rim',(.615,.75,.018),(.215,sy,.903),
      (.21,.19,.12),'sinkmetal')
block(sink,'Dark basin',(.435,.62,.021),(.128,sy,.912),
      (.009,.012,.009),'basin')
block(sink,'Recessed basin bottom',(.35,.51,.012),(.128,sy,.916),
      (.018,.022,.016),'basin')
block(sink,'Drainer',(.14,.62,.013),(.428,sy,.917),
      (.075,.069,.040),'sinkmetal')
for i in range(7):
    block(sink,f'Drainer groove {i}',(.103,.008,.004),
          (.428,sy-.25+i*.083,.926),(.22,.19,.105),'sinkmetal')
for i,(sz,ct) in enumerate([
    ((.009,.63,.017),(-.092,sy,.926)),
    ((.009,.63,.017),(.348,sy,.926)),
    ((.44,.009,.017),(.128,sy-.315,.926)),
    ((.44,.009,.017),(.128,sy+.315,.926))]):
    block(sink,f'Basin lip {i}',sz,ct,(.29,.25,.14),'sinkmetal')

hob=asset('Black glass four burner ceramic hob')
block(hob,'Glass surface',(.635,1.18,.016),(.164,-1.61,.912),black,'glass')
for k,(cx,cy,r) in enumerate([
    (.025,-1.24,.142),(.31,-1.22,.125),
    (.025,-1.77,.17),(.32,-1.77,.143)]):
    for j in range(24):
        a=2*math.pi*j/24
        b=2*math.pi*(j+1)/24
        bar(hob,f'Burner {k} segment {j}',
            (cx+r*math.cos(a),cy+r*math.sin(a),.922),
            (cx+r*math.cos(b),cy+r*math.sin(b),.922),
            .0015,(.09,.095,.075),'burner')

upper=asset('Dark walnut upper cabinetry')
block(upper,'Rear deep end panel',(.80,.055,1.83),
      (.20,1.66,2.38),darkwood,'walnut')
block(upper,'Main cupboard body',(.34,4.2,1.66),
      (.45,-.45,2.37),darkwood,'walnut')
block(upper,'Long bottom trim',(.38,4.2,.055),
      (.43,-.45,1.53),(.11,.045,.014),'walnut')
for i,y in enumerate([-2.1,-1.25,-.40,.45,1.28]):
    block(upper,f'Walnut door {i}',(.022,.82,1.61),
          (.269,y,2.38),darkwood,'walnut')
    block(upper,f'Door lower lip {i}',(.030,.82,.025),
          (.25,y,1.565),(.13,.060,.021),'walnut')
block(upper,'Rear side edge',(.026,.075,1.83),
      (-.208,1.66,2.38),(.055,.019,.007),'walnut')

hood=asset('Integrated stainless extractor')
block(hood,'Extractor underside',(.33,1.02,.035),
      (.435,-.56,1.50),(.39,.40,.36),'metal')
block(hood,'Extractor filter',(.245,.66,.009),
      (.435,-.56,1.477),(.24,.25,.22),'metal')
for i in range(5):
    block(hood,f'Filter slot {i}',(.21,.009,.003),
          (.435,-.82+i*.125,1.470),(.10,.11,.09))

lights=asset('Under cabinet light strip')
block(lights,'Warm diffuser',(.018,4.12,.012),
      (.285,-.45,1.508),(1,.73,.35),'light')

realize(scene)

def plain(name, color, rough=.45, metallic=0):
    m=bpy.data.materials.new(name)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=rough
    bs.inputs['Metallic'].default_value=metallic
    return m

def textured(name, c1, c2, scale, rough):
    m=plain(name,c1,rough)
    nodes=m.node_tree.nodes
    links=m.node_tree.links
    bs=nodes.get('Principled BSDF')
    coord=nodes.new('ShaderNodeTexCoord')
    mul=nodes.new('ShaderNodeVectorMath')
    mul.operation='MULTIPLY'
    mul.inputs[1].default_value=scale
    noise=nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=3.3
    noise.inputs['Detail'].default_value=2.0
    ramp=nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.22
    ramp.color_ramp.elements[0].color=(*c1,1)
    ramp.color_ramp.elements[1].position=.80
    ramp.color_ramp.elements[1].color=(*c2,1)
    links.new(coord.outputs['Generated'],mul.inputs[0])
    links.new(mul.outputs[0],noise.inputs['Vector'])
    links.new(noise.outputs['Fac'],ramp.inputs[0])
    links.new(ramp.outputs[0],bs.inputs['Base Color'])
    return m

mats={
    'oak':textured('Vertical oak grain',(.15,.052,.013),(.37,.17,.055),(3,3,.12),.40),
    'walnut':textured('Dark walnut grain',(.025,.008,.003),(.105,.038,.010),(3,2,.10),.30),
    'stone':textured('Warm marble variation',(.45,.40,.31),(.75,.69,.57),(7,20,2),.25),
    'glass':plain('Deep black reflective glass',(.003,.004,.003),.10),
    'basin':plain('Black sink interior',(.008,.010,.006),.24),
    'sinkmetal':plain('Dark bronze stainless rim',(.20,.16,.075),.28,.65),
    'metal':plain('Brushed stainless steel',(.39,.40,.36),.32,.65),
    'backsplash':plain('Glossy ivory backsplash',(.79,.78,.72),.17),
    'burner':plain('Subtle burner outlines',(.085,.09,.07),.36),
    'light':plain('Warm luminous diffuser',(1,.72,.34),.28)
}
lbs=mats['light'].node_tree.nodes.get('Principled BSDF')
lbs.inputs['Emission Color'].default_value=(1,.68,.30,1)
lbs.inputs['Emission Strength'].default_value=5

# Every emitted primitive is associated with its semantic material through its
# recorded geometric center, independent of Blender's generic mesh names.
cache={}
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':
        continue
    pts=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
    low=Vector(tuple(min(p[i] for p in pts) for i in range(3)))
    high=Vector(tuple(max(p[i] for p in pts) for i in range(3)))
    center=(low+high)*.5
    rec=min(records,key=lambda r:(r[0]-center).length_squared)
    _,color,finish,name=rec
    if finish in mats:
        mat=mats[finish]
    else:
        key=tuple(color)
        if key not in cache:
            cache[key]=plain('Finish '+str(key),color,.48)
        mat=cache[key]
    obj.data.materials.clear()
    obj.data.materials.append(mat)

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None:
    background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None:
    output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.77,.79,.80,1)
background.inputs['Strength'].default_value=.25

set_view(position=(0,-3.2,1.50),target=(.015,2.5,1.12),lens=32,sensor=36)
area_emitter(position=(-2.7,-.5,2.7),power=350,size=4,
             target=(-.6,1.4,.7),color=(1,.91,.78))
area_emitter(position=(.30,-.15,1.46),power=32,size=2.4,
             target=(.61,-.1,1.05),color=(1,.76,.45))
area_emitter(position=(-1.8,-3,1.9),power=110,size=3,
             target=(-.4,2,1.2),color=(.90,.94,1))
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
