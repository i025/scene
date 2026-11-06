import bpy, math
from sceneact import *

# Reference inventory (normalized image bounds):
# Architecture: pale floor (0,.75)-(1,1), rear oak slats (0,.12)-(.46,.76),
# white door (.31,.29)-(.45,.77), white right backsplash (.58,.28)-(1,.94).
# Kitchen: marble counter (.36,.59)-(.87,1), black hob (.39,.77)-(.79,1),
# inset sink (.46,.64)-(.62,.71), dark upper cupboards (.46,0)-(1,.44).
# Low black/white bench (0,.65)-(.20,.80); small door handle and wall switches.
# Hidden cabinet interiors, sink plumbing and room beyond the crop remain uncertain.
# Anchors: door verticals x=.31/.45; slat tops y=.12; counter rear-left
# (.45,.60), front-left (.36,1); upper cabinet end (.46,.02)-(.53,.43).
# World scale is arbitrary. Kitchen recedes along +Y; camera looks slightly down.
# Estimated expansion: ~230 meshes: 47 slats, 32 floor tiles, ~50 cabinet/
# architectural parts, 96 burner-ring rods, and small fittings. No booleans.

scene = Scene('Warm narrow kitchen')
def asset(name):
    a=Asset(name); scene.include(name,a); return a
def block(a,name,size,center,color):
    n=box(size=size,center=center,color=color); a.include(name,n); return n
def bar(a,name,p,q,r,c):
    n=rod(radius=r,start=p,end=q,color=c); a.include(name,n); return n

cream=(.83,.82,.77)
white=(.83,.84,.82)
oak=(.32,.135,.047)
darkwood=(.13,.055,.023)
black=(.009,.012,.011)
stone=(.66,.62,.52)
arch=asset('Room architecture')
block(arch,'Floor base',(7,8,.08),(-1,0,-.06),(.47,.45,.40))
block(arch,'Rear plaster wall',(5.4,.12,3.2),(-1.9,2.55,1.56),cream)
block(arch,'Right glossy backsplash wall',(.12,7,3.2),(.66,-.6,1.56),(.84,.84,.79))
block(arch,'Ceiling',(6.5,7,.10),(-1.9,-.2,3.14),(.82,.81,.76))

floor=asset('Rectangular porcelain floor tiles')
for iy in range(8):
    for ix in range(4):
        x=-3.15+ix*.94+(0.47 if iy%2 else 0)
        block(floor,f'Tile {iy} {ix}',(.932,.66,.013),
              (x,-2.25+iy*.67,-.009),(.53+.016*((ix+iy)%3),.51+.015*((ix+iy)%3),.46+.014*((ix+iy)%3)))

slats=asset('Rear vertical oak screen')
block(slats,'Dark backing',(3.65,.035,2.63),(-2.02,2.467,1.405),(.065,.038,.022))
for i in range(47):
    x=-3.8+i*.078
    block(slats,f'Oak batten {i}',(.048,.071,2.63),(x,2.414,1.405),oak)
block(slats,'Bottom trim',(3.65,.085,.055),(-2.02,2.41,.065),(.23,.12,.055))

door=asset('White rear door and fittings')
block(door,'Door surround',(.855,.065,2.17),(-.77,2.36,1.085),(.86,.86,.81))
block(door,'Door leaf',(.738,.045,2.065),(-.77,2.314,1.054),(.76,.78,.76))
block(door,'Upper narrow reveal',(.738,.008,.012),(-.77,2.284,2.071),(.51,.53,.51))
block(door,'Right reveal',(.009,.008,2.06),(-.399,2.284,1.054),(.42,.44,.42))
block(door,'Handle escutcheon',(.033,.018,.085),(-1.065,2.279,1.035),(.45,.46,.43))
bar(door,'Lever handle',(-1.065,2.246,1.058),(-.952,2.246,1.058),.009,(.37,.39,.37))
bar(door,'Keyhole',(-1.063,2.264,.972),(-1.063,2.247,.972),.008,(.17,.18,.17))
switches=asset('Rear electrical fittings')
block(switches,'Light switch',(.092,.021,.075),(-1.36,2.355,1.085),(.87,.87,.81))
block(switches,'Low socket',(.070,.021,.078),(-1.33,2.355,.31),(.87,.87,.81))

bench=asset('Low black bench with white front')
block(bench,'Carcass',(.99,.40,.46),(-2.39,2.14,.245),(.023,.026,.023))
block(bench,'White inset front',(.91,.018,.31),(-2.39,1.927,.239),(.78,.81,.78))
block(bench,'Top slab',(1.04,.43,.055),(-2.39,2.12,.493),(.014,.017,.015))
block(bench,'Right side',(.055,.43,.44),(-1.882,2.12,.25),(.022,.024,.020))

lower=asset('Base kitchen cabinets')
block(lower,'Cabinet body',(.83,3.92,.79),(.20,-.28,.43),(.56,.53,.46))
block(lower,'Dark recessed plinth',(.72,3.86,.10),(.24,-.28,.065),(.075,.060,.044))
for i,y in enumerate([-1.65,-.8,.05,.90]):
    block(lower,f'Cabinet front {i}',(.027,.825,.715),(-.229,y,.452),(.63,.60,.52))

counter=asset('Pale marble worktop with sink opening')
# Hole is retained by four surrounding solids.
z=.872
block(counter,'Front long stone strip',(.155,3.95,.058),(-.192,-.29,z),stone)
block(counter,'Wall long stone strip',(.147,3.95,.058),(.556,-.29,z),stone)
block(counter,'Near worktop',(.67,2.88,.058),(.22,-.825,z),stone)
block(counter,'Back worktop',(.67,.30,.058),(.22,1.535,z),stone)

sink=asset('Inset dark sink and draining board')
block(sink,'Metal rim',(.615,.59,.018),(.215,1.085,.903),(.23,.22,.15))
block(sink,'Black basin cavity',(.435,.48,.021),(.128,1.085,.912),(.018,.019,.015))
block(sink,'Basin inner bottom',(.35,.37,.012),(.128,1.085,.916),(.034,.034,.026))
block(sink,'Drainer',(.14,.48,.013),(.428,1.085,.917),(.11,.105,.071))
for i in range(6):
    block(sink,f'Drainer groove {i}',(.103,.008,.004),(.428,.905+i*.069,.926),(.25,.23,.16))
for i,(sz,ct) in enumerate([
    ((.009,.49,.017),(-.092,1.085,.926)),
    ((.009,.49,.017),(.348,1.085,.926)),
    ((.44,.009,.017),(.128,.84,.926)),
    ((.44,.009,.017),(.128,1.33,.926))]):
    block(sink,f'Basin lip {i}',sz,ct,(.34,.30,.19))

hob=asset('Black glass four burner ceramic hob')
block(hob,'Glass surface',(.635,1.18,.016),(.164,-1.61,.912),(.008,.012,.011))
for k,(cx,cy,r) in enumerate([(.025,-1.24,.142),(.31,-1.22,.125),(.025,-1.77,.17),(.32,-1.77,.143)]):
    for j in range(24):
        a=2*math.pi*j/24
        b=2*math.pi*(j+1)/24
        bar(hob,f'Burner {k} arc {j}',
            (cx+r*math.cos(a),cy+r*math.sin(a),.922),
            (cx+r*math.cos(b),cy+r*math.sin(b),.922),
            .0017,(.16,.17,.14))

upper=asset('Dark walnut upper cabinetry')
block(upper,'Rear deep end panel',(.80,.055,1.39),(.20,1.66,2.60),darkwood)
block(upper,'Main upper cupboard body',(.43,4.2,1.17),(.405,-.45,2.635),darkwood)
block(upper,'Long bottom trim',(.47,4.2,.055),(.385,-.45,2.038),(.17,.079,.030))
for i,y in enumerate([-2.1,-1.25,-.40,.45,1.28]):
    block(upper,f'Walnut door {i}',(.022,.82,1.135),(.177,y,2.655),darkwood)
    block(upper,f'Door lower lip {i}',(.030,.82,.025),(.158,y,2.075),(.23,.12,.047))
block(upper,'Rear side edge',(.026,.075,1.38),(-.208,1.66,2.60),(.105,.042,.017))
hood=asset('Integrated stainless extractor')
block(hood,'Extractor underside',(.39,1.02,.035),(.397,-.56,2.008),(.43,.44,.40))
block(hood,'Extractor filter',(.285,.66,.009),(.385,-.56,1.985),(.28,.29,.26))
for i in range(5):
    block(hood,f'Filter slot {i}',(.23,.009,.003),(.385,-.82+i*.125,1.977),(.17,.18,.16))
lights=asset('Under cabinet light strip')
block(lights,'Warm diffuser',(.025,4.12,.018),(.177,-.45,2.010),(1,.78,.45))

realize(scene)

# Restrained procedural materials: long wood grain, fine stone mottling.
def principled(mat):
    return mat.node_tree.nodes.get('Principled BSDF')
def proc_material(name,c1,c2,scale,rough=.45,kind='NOISE'):
    m=bpy.data.materials.new(name); m.use_nodes=True
    n=m.node_tree.nodes; l=m.node_tree.links
    bs=principled(m); bs.inputs['Roughness'].default_value=rough
    tex=n.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value=3.3
    tex.inputs['Detail'].default_value=2
    coord=n.new('ShaderNodeTexCoord')
    mapping=n.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'
    mapping.inputs[1].default_value=scale
    l.new(coord.outputs['Generated'],mapping.inputs[0])
    l.new(mapping.outputs['Vector'],tex.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.22; ramp.color_ramp.elements[0].color=(*c1,1)
    ramp.color_ramp.elements[1].position=.80; ramp.color_ramp.elements[1].color=(*c2,1)
    l.new(tex.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs[0],bs.inputs['Base Color'])
    return m
wood=proc_material('Warm vertical oak grain',(.15,.063,.020),(.43,.22,.095),(3,3,.13),.42)
walnut=proc_material('Dark walnut grain',(.055,.019,.007),(.21,.095,.034),(3,2,.10),.34)
marble=proc_material('Subtle warm stone',(.47,.44,.36),(.78,.74,.65),(7,20,2),.28)
for obj in bpy.context.scene.objects:
    if obj.type!='MESH': continue
    nm=obj.name.lower()
    if 'batten' in nm:
        obj.data.materials.clear(); obj.data.materials.append(wood)
    elif 'walnut' in nm or 'deep end panel' in nm or 'main upper cupboard' in nm:
        obj.data.materials.clear(); obj.data.materials.append(walnut)
    elif 'stone strip' in nm or 'worktop' in nm:
        obj.data.materials.clear(); obj.data.materials.append(marble)
    elif obj.data.materials:
        bs=principled(obj.data.materials[0])
        if bs:
            bs.inputs['Roughness'].default_value=.42
            if 'glass surface' in nm:
                bs.inputs['Roughness'].default_value=.12
            if 'backsplash' in nm:
                bs.inputs['Roughness'].default_value=.19
            if 'diffuser' in nm:
                bs.inputs['Emission Color'].default_value=(1,.65,.30,1)
                bs.inputs['Emission Strength'].default_value=4

sc=bpy.context.scene
if sc.world is None:
    sc.world=bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes=True
background=sc.world.node_tree.nodes.get('Background')
if background is None: background=sc.world.node_tree.nodes.new('ShaderNodeBackground')
output=sc.world.node_tree.nodes.get('World Output')
if output is None: output=sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'],output.inputs['Surface'])
background.inputs['Color'].default_value=(.77,.79,.80,1)
background.inputs['Strength'].default_value=.35
set_view(position=(0,-3.2,1.50),target=(.015,2.5,1.12),lens=32,sensor=36)
area_emitter(position=(-2.7,-.5,2.7),power=520,size=4,target=(-.6,1.4,.7),color=(1,.91,.78))
area_emitter(position=(.11,-.15,1.96),power=85,size=2.4,target=(.61,-.1,1.20),color=(1,.76,.45))
area_emitter(position=(-1.8,-3,1.9),power=180,size=3,target=(-.4,2,1.2),color=(.90,.94,1))
sc.render.resolution_x=512
sc.render.resolution_y=342
sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
