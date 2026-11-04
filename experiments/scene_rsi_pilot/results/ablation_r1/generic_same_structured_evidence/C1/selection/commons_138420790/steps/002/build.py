from sceneact import *
import bpy

# Reference anchors: post x=.17-.30, foot y=.99; island top corners
# (.33,.59),(.62,.62),(.90,.57), base (.62,.85); hood x=.42-.73.
# Main discrepancies in step 1:
# 1. View was too distant and frontal: move camera closer and farther left,
#    retaining lens=36; lower eye height to match hood and countertop levels.
# 2. Island end was too narrow and post too central: revise island proportions
#    and reposition the foreground post using the new camera.
# 3. Ceiling and black cabinets were washed out: reduce broad light power,
#    darken roof structure, and extend the cabinetry toward the right.
CAMERA = (-4.2, -3.6, 1.40)
TARGET = (-.4, .1, 1.40)
LENS = 36
ISLAND_CENTER = (-.25, -.48)
ISLAND_WIDTH = 1.75
ISLAND_DEPTH = 1.30
CEILING_HEIGHT = 3.85
KEY_POWER = 480

scene = Scene('Contemporary kitchen')
ivory = (.57, .59, .56)
black = (.018, .023, .022)
steel = (.40, .44, .43)

def cube(parent, name, size, center, color):
    return parent.include(name, box(size=size, center=center, color=color))

room = Asset('Room architecture')
cube(room, 'floor', (15,14,.12), (0,0,-.07), (.62,.61,.57))
cube(room, 'rear_wall', (11,.16,3.85), (.5,2.03,1.925), (.23,.25,.23))
cube(room, 'left_wall', (.15,8,3.85), (-3.5,.2,1.925), (.29,.30,.27))
cube(room, 'roof', (12,12,.12), (0,0,3.91), (.012,.017,.016))
scene.include('architecture', room)

tiles = Asset('Floor tile joints')
for i in range(-7,9):
    cube(tiles, f'x_joint_{i}', (.004,14,.002), (i*.9,0,-.008), (.41,.41,.38))
    cube(tiles, f'y_joint_{i}', (15,.004,.002), (0,i*.9,-.008), (.41,.41,.38))
scene.include('floor_joints', tiles)

roof = Asset('Exposed ceiling beams')
for i,x in enumerate([-3,-1.9,-.8,.3,1.4,2.5,3.6,4.7]):
    cube(roof, f'joist_{i}', (.09,9,.20), (x,.1,3.73), (.012,.018,.017))
for i,y in enumerate([-.9,.9,2.0]):
    cube(roof, f'cross_beam_{i}', (11,.21,.32), (.4,y,3.57), (.025,.033,.031))
for i in range(20):
    cube(roof, f'roof_seam_{i}', (.014,9,.025), (-3+i*.4,0,3.835), (.006,.009,.008))
roof.include('pipe', rod(radius=.025, start=(-2.7,1.25,3.55),
                         end=(4.7,1.25,3.55), color=(.065,.08,.075)))
scene.include('ceiling_structure', roof)

posts = Asset('Timber supports')
cube(posts, 'foreground_post', (.32,.36,4.5), (-2.49,-1.05,2.23), (.30,.17,.075))
cube(posts, 'rear_post', (.19,.21,3.8), (4.12,1.36,1.9), (.38,.23,.11))
scene.include('wood_columns', posts)

back = Asset('Rear countertop and cabinetry')
cube(back, 'lower_bank', (5.0,.68,.87), (.35,1.55,.435), black)
cube(back, 'counter', (5.04,.73,.045), (.35,1.51,.892), (.035,.041,.037))
cube(back, 'backsplash', (5.15,.045,.86), (.35,1.91,1.33), (.025,.032,.028))
for i in range(7):
    cube(back, f'base_door_{i}', (.701,.028,.77),
         (-1.79+i*.714,1.185,.445), (.034,.040,.036))
cube(back, 'upper_cabinets', (4.65,.52,.43), (.40,1.66,2.01), (.045,.055,.049))
cube(back, 'warm_splash_panel', (2.70,.025,.37), (.82,1.873,1.155), (.26,.19,.15))
cube(back, 'under_cabinet_strip', (2.74,.04,.014), (.82,1.55,1.79), (.65,.48,.31))
scene.include('rear_counter', back)

tall = Asset('Left tall cupboard')
cube(tall, 'carcass', (.74,.80,2.43), (-1.89,1.37,1.215), (.017,.023,.021))
cube(tall, 'front', (.715,.035,2.36), (-1.89,.955,1.215), (.038,.047,.041))
cube(tall, 'top_door_joint', (.72,.012,.007), (-1.89,.931,2.05), (.01,.014,.012))
scene.include('left_tall_cabinet', tall)

ovens = Asset('Double oven tower')
OX = 2.70
cube(ovens, 'tower', (.76,.76,2.32), (OX,1.51,1.16), (.024,.030,.027))
for i,z in enumerate([1.00,1.57]):
    cube(ovens, f'frame_{i}', (.65,.035,.49), (OX,1.111,z), (.23,.25,.23))
    cube(ovens, f'glass_{i}', (.555,.022,.32), (OX,1.085,z+.035), (.012,.027,.034))
    cube(ovens, f'control_strip_{i}', (.58,.024,.072), (OX,1.076,z+.208), (.075,.09,.085))
    cube(ovens, f'handle_{i}', (.48,.065,.026), (OX,1.043,z-.13), (.43,.45,.41))
cube(ovens, 'bottom_door', (.65,.03,.65), (OX,1.107,.34), (.028,.035,.030))
scene.include('ovens', ovens)

right = Asset('Right tall black enclosure')
cube(right, 'carcass', (.98,.74,2.40), (3.56,1.47,1.20), (.017,.023,.021))
cube(right, 'front_panel', (.92,.045,2.13), (3.56,1.074,1.10), (.026,.034,.028))
cube(right, 'gray_top_band', (1.18,.84,.31), (3.46,1.51,2.40), (.23,.26,.23))
scene.include('right_cabinet', right)

ix,iy = ISLAND_CENTER
island = Asset('Island cabinet')
cube(island, 'toe_recess', (ISLAND_WIDTH-.10,ISLAND_DEPTH-.10,.105),
     (ix,iy,.077), (.11,.135,.12))
cube(island, 'body', (ISLAND_WIDTH,ISLAND_DEPTH,.80), (ix,iy,.505), ivory)
cube(island, 'left_end', (.045,ISLAND_DEPTH,.86),
     (ix-ISLAND_WIDTH/2-.003,iy,.49), (.48,.51,.48))
for i,z in enumerate([.235,.503,.771]):
    cube(island, f'drawer_{i}', (ISLAND_WIDTH-.045,.032,.252),
         (ix+.008,iy-ISLAND_DEPTH/2-.023,z), (.60,.62,.58))
    cube(island, f'reveal_{i}', (ISLAND_WIDTH-.045,.015,.011),
         (ix+.008,iy-ISLAND_DEPTH/2-.043,z+.131), (.16,.19,.17))
cube(island, 'countertop', (ISLAND_WIDTH+.035,ISLAND_DEPTH+.035,.036),
     (ix,iy,.936), (.73,.74,.68))
scene.include('island', island)

sink = Asset('Inset sink and chrome tap')
sx,sy = .17,-.11
cube(sink, 'rim', (.49,.36,.006), (sx,sy,.958), (.51,.55,.51))
cube(sink, 'bowl', (.445,.31,.007), (sx,sy,.962), (.32,.37,.34))
cube(sink, 'basin', (.37,.245,.004), (sx,sy,.966), (.49,.54,.49))
sink.include('tap_foot', rod(radius=.025,length=.022,
                              center=(sx,sy+.23,.972),color=steel))
sink.include('curved_tap', sweep_tube(
    points=[(sx,sy+.23,.98),(sx,sy+.23,1.14),
            (sx,sy+.21,1.20),(sx,sy+.15,1.22),
            (sx,sy+.08,1.20),(sx,sy+.06,1.14)],
    radius=.011,color=(.59,.65,.63)))
scene.include('sink', sink)

hob = Asset('Flush pale cooktop')
cube(hob, 'panel', (.57,.46,.003), (-.68,-.65,.956), (.66,.69,.61))
for i,x in enumerate([-.83,-.55]):
    cube(hob, f'zone_{i}', (.17,.22,.0015), (x,-.65,.959), (.74,.76,.68))
scene.include('cooktop', hob)

hood = Asset('Suspended plaster extractor')
cube(hood, 'enclosure', (1.17,.89,2.04), (-.12,.04,2.82), (.64,.63,.56))
cube(hood, 'bottom_plate', (1.13,.85,.022), (-.12,.04,1.789), (.44,.45,.39))
cube(hood, 'vent', (.65,.43,.011), (-.12,.04,1.775), (.15,.18,.15))
scene.include('extractor', hood)

kettle = Asset('Red kettle on rear counter')
KX = 1.10
kettle.include('body', ball(radius=.092,center=(KX,1.50,1.005),color=(.70,.004,.012)))
cube(kettle, 'base', (.17,.14,.035), (KX,1.50,.925), (.009,.012,.010))
kettle.include('handle', sweep_tube(
    points=[(KX-.08,1.5,1.04),(KX-.08,1.5,1.13),
            (KX-.01,1.5,1.16),(KX+.07,1.5,1.12),(KX+.08,1.5,1.04)],
    radius=.015,color=(.026,.019,.016)))
scene.include('red_kettle', kettle)

# API audit: all dimensions/radii positive; no fillet_box calls.
# Repeated sibling keys are indexed. World/camera/lights follow realize.
realize(scene)
sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('Ambient world')
sc.world.use_nodes = True
bg = sc.world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (.14,.16,.14,1)
bg.inputs['Strength'].default_value = .20

def meshes_in(name):
    root = bpy.data.objects.get(name)
    return [o for o in root.children_recursive if o.type == 'MESH'] if root else []

# Material changes target group descendants and copy shared materials first.
for obj in meshes_in('wood_columns'):
    for slot in obj.material_slots:
        if slot.material is None:
            continue
        mat = slot.material.copy()
        slot.material = mat
        mat.use_nodes = True
        nt = mat.node_tree
        bs = nt.nodes.get('Principled BSDF')
        coord = nt.nodes.new('ShaderNodeTexCoord')
        stretch = nt.nodes.new('ShaderNodeVectorMath')
        stretch.operation = 'MULTIPLY'
        stretch.inputs[1].default_value = (8,8,.19)
        noise = nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 4
        noise.inputs['Detail'].default_value = 3
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position = .20
        ramp.color_ramp.elements[0].color = (.085,.036,.012,1)
        ramp.color_ramp.elements[1].position = .80
        ramp.color_ramp.elements[1].color = (.36,.205,.087,1)
        nt.links.new(coord.outputs['Generated'],stretch.inputs[0])
        nt.links.new(stretch.outputs[0],noise.inputs['Vector'])
        nt.links.new(noise.outputs['Fac'],ramp.inputs[0])
        nt.links.new(ramp.outputs['Color'],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value = .66
        bump = nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .16
        bump.inputs['Distance'].default_value = .008
        nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])

for obj in meshes_in('extractor'):
    for slot in obj.material_slots:
        if slot.material is None:
            continue
        mat = slot.material.copy()
        slot.material = mat
        mat.use_nodes = True
        nt = mat.node_tree
        noise = nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 95
        bump = nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .12
        bump.inputs['Distance'].default_value = .008
        nt.links.new(noise.outputs['Fac'],bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])

for obj in meshes_in('sink'):
    for slot in obj.material_slots:
        if slot.material:
            mat = slot.material.copy()
            slot.material = mat
            mat.use_nodes = True
            bs = mat.node_tree.nodes.get('Principled BSDF')
            bs.inputs['Metallic'].default_value = .75
            bs.inputs['Roughness'].default_value = .24

set_view(CAMERA,TARGET,lens=LENS,sensor=36,shift=(0,.008))
area_emitter((-3.5,-3.0,3.25),power=KEY_POWER,size=3.4,
             target=(-.1,0,.8),color=(1,.93,.82))
area_emitter((1.5,-.7,3.35),power=230,size=2.4,
             target=(.0,-.2,.7),color=(.88,.94,1))
area_emitter((.85,1.48,1.72),power=25,size=1.7,
             target=(.85,1.86,1.15),color=(1,.70,.49))

sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.view_settings.view_transform = 'AgX'
