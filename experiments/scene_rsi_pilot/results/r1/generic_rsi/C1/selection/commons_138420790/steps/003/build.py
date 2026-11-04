import bpy
from sceneact import *

# Three largest discrepancies in step 2:
# 1. Island drawers are too narrow and worktop too low: length 2.35 -> 2.95,
#    depth 1.30 -> 1.13, height scale 1.12; move assembly .22 toward rear.
# 2. Foreground post is too far right and slightly broad: move screen-left
#    along camera-right axis, reduce its cross section to .30 square.
# 3. Background tower starts too low and ceiling is too gray:
#    increase left tower height .32 and darken ceiling/beam materials.
# Preserve lens, camera pose, hood width and its nearly matching upper extent.
# Reference landmarks: post x .17-.30, bottom .99; hood x .42-.73,
# y .05-.43; island x .33-.90, y .56-.85; oven x .68-.78.
# Island depth and unseen rear clearances remain uncertain.

CAMERA = (-3.9, -6.2, 1.78)
TARGET = (0, .65, 1.78)
LENS = 51
ISLAND_L, ISLAND_D = 2.95, 1.13
ISLAND_ANGLE = 35
ISLAND_HEIGHT_SCALE = 1.12
HOOD_BOTTOM, HOOD_TOP = 1.93, 3.80
KEY_POWER, FILL_POWER = 470, 160

scene = Scene('Industrial kitchen')
ivory = (.48, .50, .48)
stone = (.66, .67, .62)

def block(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

architecture = Asset('Architecture')
block(architecture, 'floor', (14,14,.12), (0,0,-.06), (.49,.48,.44))
block(architecture, 'rear_wall', (9,.16,4.3), (0,2.85,2.15), (.19,.20,.18))
block(architecture, 'left_wall', (.16,8,4.3), (-3.5,1.5,2.15), (.25,.26,.23))
block(architecture, 'ceiling', (10,10,.14), (0,0,3.88), (.006,.009,.008))
for i,x in enumerate([-3.3,-1.8,-.3,1.2,2.7,4.2]):
    block(architecture, f'joist_{i}', (.12,8,.22), (x,.8,3.72), (.008,.012,.010))
for i,y in enumerate([-1.5,1.25,3]):
    block(architecture, f'beam_{i}', (10,.24,.38), (0,y,3.59), (.014,.021,.019))
scene.include('architecture', architecture)

tiles = Asset('Floor joints')
for i in range(-8,9):
    block(tiles, f'x_joint_{i}', (.004,13,.002), (i*.92,0,.001), (.40,.40,.37))
    block(tiles, f'y_joint_{i}', (13,.004,.002), (0,i*.92,.001), (.40,.40,.37))
scene.include('floor_joints', tiles)

island = Asset('Island')
block(island, 'plinth', (ISLAND_L-.12,ISLAND_D-.13,.10), (0,0,.05), (.15,.17,.16))
block(island, 'body', (ISLAND_L,ISLAND_D,.79), (0,0,.50), ivory)
block(island, 'solid_left_end', (.055,ISLAND_D,.85),
      (-ISLAND_L/2-.01,0,.51), (.44,.46,.44))
for i in range(3):
    z = .215+i*.245
    block(island, f'drawer_{i}', (ISLAND_L-.065,.035,.226),
          (0,-ISLAND_D/2-.022,z), (.55,.57,.54))
    block(island, f'drawer_gap_{i}', (ISLAND_L-.07,.018,.012),
          (0,-ISLAND_D/2-.043,z+.116), (.22,.24,.22))
block(island, 'stone_top', (ISLAND_L+.035,ISLAND_D+.035,.045),
      (0,0,.9275), stone)
block(island, 'cooktop_outline', (.70,.48,.004), (-.77,-.02,.952), (.53,.54,.49))
block(island, 'cooktop', (.68,.46,.004), (-.77,-.02,.955), (.66,.67,.61))
block(island, 'sink_rim', (.50,.38,.009), (.40,.25,.955), (.73,.76,.72))
block(island, 'sink_basin', (.445,.325,.009), (.40,.25,.961), (.42,.46,.43))
block(island, 'sink_bottom', (.37,.25,.009), (.40,.25,.966), (.53,.58,.54))
faucet = Part('Chrome faucet')
faucet.include('spout', sweep_tube(
    points=[(.59,.44,.96),(.59,.44,1.12),(.58,.44,1.18),
            (.52,.44,1.205),(.39,.44,1.205),(.35,.44,1.17),(.35,.44,1.105)],
    radius=.012, color=(.63,.68,.66)))
faucet.include('lever', rod(radius=.008, start=(.65,.44,.97),
                           end=(.65,.44,1.07), color=(.53,.58,.56)))
island.include('faucet', faucet)
island.resize((1,1,ISLAND_HEIGHT_SCALE), pivot=(0,0,0))
island.turn('z', ISLAND_ANGLE, pivot=(0,0,0))
island.move((.10,.22,0))
scene.include('island', island)

hood = Asset('Suspended stone extractor')
block(hood, 'shell', (1.05,.90,HOOD_TOP-HOOD_BOTTOM),
      (-.03,.02,(HOOD_TOP+HOOD_BOTTOM)/2), (.73,.72,.66))
block(hood, 'underside', (.94,.79,.018),
      (-.03,.02,HOOD_BOTTOM-.005), (.40,.42,.37))
block(hood, 'bottom_edge', (1.06,.91,.022),
      (-.03,.02,HOOD_BOTTOM+.006), (.64,.64,.58))
block(hood, 'control', (.035,.025,.012),
      (-.35,-.44,HOOD_BOTTOM+.025), (.23,.25,.21))
hood.turn('z', 25, pivot=(-.03,.02,0))
scene.include('extractor', hood)

back = Asset('Back kitchen cabinetry')
block(back, 'left_tower', (1.12,.66,2.68), (-1.66,2.22,1.34), (.022,.027,.024))
block(back, 'tower_front', (1.10,.025,2.63), (-1.66,1.875,1.34), (.031,.037,.032))
block(back, 'tower_seam', (1.10,.015,.009), (-1.66,1.854,2.32), (.012,.016,.013))
block(back, 'base_run', (3.95,.63,.89), (.32,2.23,.445), (.022,.029,.024))
block(back, 'rear_counter', (4.05,.72,.045), (.32,2.18,.915), (.067,.079,.068))
block(back, 'backsplash', (4.05,.055,.73), (.32,2.57,1.30), (.025,.035,.029))
block(back, 'upper_cabinets', (3.95,.40,.48), (.30,2.43,1.98), (.020,.029,.022))
block(back, 'warm_niche_back', (2.0,.025,.38), (-.28,2.525,1.18), (.25,.19,.16))
block(back, 'niche_light', (2,.025,.015), (-.28,2.49,1.39), (.85,.67,.47))
for i,x in enumerate([-1.05,-.25,.55,1.35]):
    block(back, f'base_seam_{i}', (.008,.012,.79), (x,1.906,.45), (.010,.015,.011))
oven_x = 2.10
block(back, 'oven_tower', (.87,.70,2.18), (oven_x,2.25,1.09), (.021,.029,.023))
for i,z in enumerate([.87,1.40]):
    block(back, f'oven_trim_{i}', (.72,.035,.43), (oven_x,1.88,z), (.18,.21,.19))
    block(back, f'oven_glass_{i}', (.62,.018,.28), (oven_x,1.853,z+.025), (.015,.031,.035))
    block(back, f'oven_handle_{i}', (.57,.035,.024), (oven_x,1.823,z+.15), (.40,.44,.41))
    block(back, f'oven_controls_{i}', (.67,.015,.055), (oven_x,1.849,z-.16), (.27,.29,.26))
block(back, 'right_end_panel', (.38,.77,2.52), (2.65,2.23,1.26), (.021,.030,.023))
scene.include('back_cabinets', back)

kettle = Asset('Red kettle')
kettle.include('body', ball(radius=.092, center=(-.23,2.12,1.035), color=(.72,.008,.020)))
block(kettle, 'base', (.17,.14,.025), (-.23,2.12,.944), (.008,.012,.009))
kettle.include('handle', sweep_tube(
    points=[(-.31,2.12,1.06),(-.31,2.12,1.145),(-.27,2.12,1.174),
            (-.20,2.12,1.174),(-.15,2.12,1.13),(-.15,2.12,1.06)],
    radius=.012, color=(.012,.015,.012)))
scene.include('kettle', kettle)

posts = Asset('Structural timber')
block(posts, 'foreground_post', (.30,.30,4.5), (-2.062,-1.531,2.25), (.29,.17,.085))
block(posts, 'rear_right_post', (.17,.21,3.55), (2.95,2.15,1.775), (.40,.26,.14))
scene.include('timber', posts)

partition = Asset('Right room boundary')
block(partition, 'dark_partition', (.16,1.25,2.65), (2.86,2.38,1.325), (.027,.036,.028))
block(partition, 'gray_fascia', (3.4,.15,.36), (1.45,2.71,2.68), (.29,.32,.29))
block(partition, 'distant_wall', (.17,2,3.3), (3.65,3,1.65), (.56,.56,.49))
scene.include('partition', partition)

realize(scene)

def meshes(name):
    parent = bpy.data.objects.get(name)
    return [] if parent is None else [o for o in parent.children_recursive if o.type == 'MESH']

for ob in meshes('timber'):
    for slot in ob.material_slots:
        if not slot.material:
            continue
        mat = slot.material.copy()
        slot.material = mat
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bs = nodes.get('Principled BSDF')
        coord = nodes.new('ShaderNodeTexCoord')
        stretch = nodes.new('ShaderNodeVectorMath')
        stretch.operation = 'MULTIPLY'
        stretch.inputs[1].default_value = (6,6,.16)
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 5
        noise.inputs['Detail'].default_value = 3
        ramp = nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .22
        ramp.color_ramp.elements[0].color = (.075,.035,.014,1)
        ramp.color_ramp.elements[1].position = .80
        ramp.color_ramp.elements[1].color = (.32,.185,.085,1)
        links.new(coord.outputs['Generated'], stretch.inputs[0])
        links.new(stretch.outputs['Vector'], noise.inputs['Vector'])
        links.new(noise.outputs['Fac'], ramp.inputs[0])
        links.new(ramp.outputs['Color'], bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value = .67

for ob in meshes('extractor'):
    for slot in ob.material_slots:
        if not slot.material:
            continue
        mat = slot.material.copy()
        slot.material = mat
        mat.use_nodes = True
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bs = nodes.get('Principled BSDF')
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 90
        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .10
        bump.inputs['Distance'].default_value = .010
        links.new(noise.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bs.inputs['Normal'])
        bs.inputs['Roughness'].default_value = .86

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('AmbientWorld')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value = (.28,.31,.32,1)
background.inputs['Strength'].default_value = .10

set_view(CAMERA, TARGET, lens=LENS, sensor=36, shift=(0,-.045))
sc.camera.data.clip_end = 100
area_emitter((-3,-3,3.25), power=KEY_POWER, size=3.4,
             target=(0,.6,.7), color=(1,.94,.84))
area_emitter((2,-.4,3.1), power=FILL_POWER, size=2.5,
             target=(0,0,.8), color=(.86,.92,1))
area_emitter((-.28,2.02,1.43), power=38, size=1.5,
             target=(-.28,2.2,.93), color=(1,.75,.57))
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
# Audit: every dimension/radius is positive; all tube points are distinct.
# Explicit pivots preserve support; assemblies retain separate component meshes.
