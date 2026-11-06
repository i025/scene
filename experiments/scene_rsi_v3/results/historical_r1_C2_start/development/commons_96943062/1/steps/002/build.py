# Reference inventory, normalized image bounds, approximate:
# Dark carpet floor: (0,.59)-(1,1), with scattered broken panels and strips.
# Back wall: (.11,.37)-(.53,.61), with vent, electrical box and loose cover.
# Right wall: (.52,.03)-(1,.82), with large whiteboard and dark baseboard.
# Drop ceiling: (0,0)-(.59,.39), with rectangular grid, lights and left gaps.
# Bright partial partition: (0,.32)-(.12,.66), with visible panel seams.
# Small hanging American flag and diagonal pole: (.45,.32)-(.59,.43).
# Yellow folded floor material: (.56,.68)-(.90,.79).
# Several dark fallen panels and metal strips occupy the left floor; two long
# pale strips project from under the yellow pile toward the lower right.
# The exact shapes of the debris and the room beyond the frame are uncertain.
#
# Compared with the first render, the whiteboard and flag were too small,
# the bright left partition was almost absent, and the debris and yellow pile
# were too distant. The first render also lacked the reference's dark,
# mottled carpet. Architecture and camera are kept broadly consistent.
#
# Estimated primitive count: architecture 10, ceiling 32, board 6, fixtures 12,
# flag 12, debris 25, yellow pile 6; approximately 103 meshes, no booleans.

from sceneact import *
import bpy
import math

scene = Scene('Damaged classroom')

wall = (.69, .68, .63)
back_wall = (.62, .62, .57)
ceiling_color = (.69, .71, .70)
grid = (.49, .50, .49)
carpet = (.105, .105, .09)
trim = (.10, .105, .095)
metal = (.43, .46, .45)

architecture = Asset('Room architecture')
architecture.include('carpeted floor', box((7.4,17,.12), center=(-.7,-.5,-.06), color=carpet))
architecture.include('right wall', box((.12,17,3.35), center=(3,-.5,1.675), color=wall))
architecture.include('back wall', box((7.4,.12,3.35), center=(-.7,8,1.675), color=back_wall))
architecture.include('right dark baseboard', box((.035,16.9,.18), center=(2.925,-.5,.09), color=trim))
architecture.include('back dark baseboard', box((7.3,.035,.18), center=(-.7,7.92,.09), color=trim))

# A bright partial wall stands close to the camera on the left.
architecture.include('left partition', box((.12,5.8,2.9), center=(-3.65,3.0,1.45), color=(.83,.85,.84)))
architecture.include('partition seam high', box((.014,5.7,.012), center=(-3.575,3.0,2.0), color=(.68,.71,.70)))
architecture.include('partition seam low', box((.014,5.7,.012), center=(-3.575,3.0,.95), color=(.68,.71,.70)))
architecture.include('partition upright seam', box((.014,.015,2.8), center=(-3.575,2.0,1.45), color=(.69,.72,.71)))
scene.include('architecture', architecture)

ceiling_asset = Asset('Suspended ceiling')
ceiling_asset.include('ceiling field', box((7.4,17,.10), center=(-.7,-.5,3.35), color=ceiling_color))
for i,x in enumerate((-4.3,-3.1,-1.9,-.7,.5,1.7,2.9)):
    ceiling_asset.include('long rail %02d' % i,
        box((.014,16.9,.018), center=(x,-.5,3.288), color=grid))
for i in range(15):
    y = -7.5 + i*1.1
    ceiling_asset.include('cross rail %02d' % i,
        box((7.3,.014,.018), center=(-.7,y,3.287), color=grid))
for i,y in enumerate((1.6,3.8,6.0)):
    ceiling_asset.include('fluorescent panel %d' % i,
        box((1.12,1.02,.016), center=(-2.5,y,3.275), color=(.80,.82,.81)))
for i,y in enumerate((3.4,4.6,5.8)):
    ceiling_asset.include('missing tile %d' % i,
        box((1.08,.82,.016), center=(-3.75,y,3.265), color=(.10,.12,.12)))
ceiling_asset.include('ceiling detector',
    ball(.09, center=(-1.45,2.7,3.22), color=(.78,.78,.74)))
scene.include('ceiling', ceiling_asset)

# Board extends closer along the right wall than in the initial build.
board = Asset('Wall mounted whiteboard')
board.include('writing surface',
    box((.035,5.5,1.85), center=(2.915,2.5,1.88), color=(.86,.87,.86)))
for z in (.95,2.81):
    board.include('horizontal frame %.2f' % z,
        box((.045,5.58,.045), center=(2.88,2.5,z), color=metal))
for y in (-.29,5.29):
    board.include('vertical frame %.2f' % y,
        box((.045,.045,1.90), center=(2.88,y,1.88), color=metal))
board.include('lower marker ledge',
    box((.12,5.5,.032), center=(2.84,2.5,.93), color=(.59,.61,.59)))
scene.include('whiteboard', board)

fixtures = Asset('Back wall fixtures')
fixtures.include('vent dark inset', box((.90,.025,.40), center=(-2.25,7.91,1.91), color=(.24,.28,.27)))
for z in (1.76,1.84,1.92,2.00,2.06):
    fixtures.include('vent slat %.2f' % z, box((.84,.018,.012), center=(-2.25,7.89,z), color=(.34,.37,.35)))
fixtures.include('electrical panel', box((.31,.055,.47), center=(-.55,7.89,1.72), color=(.36,.40,.38)))
fixtures.include('panel dark interior', box((.20,.018,.32), center=(-.55,7.85,1.75), color=(.14,.17,.16)))
cover = box((.54,.045,.48), center=(-.29,7.80,1.39), color=(.44,.48,.45))
cover.turn(axis='+y', degrees=-35)
fixtures.include('hanging panel cover', cover)
fixtures.include('small wall plate', box((.16,.025,.20), center=(.27,7.89,1.36), color=(.76,.76,.71)))
fixtures.include('small switch', box((.12,.025,.16), center=(.02,7.89,1.42), color=(.71,.72,.68)))
fixtures.include('right wall outlet', box((.02,.12,.17), center=(2.91,.4,.42), color=(.65,.64,.59)))
scene.include('back wall fixtures', fixtures)

flag = Asset('Hanging American flag')
flag.include('diagonal flag pole', rod(.018, start=(1.68,7.82,3.10), end=(2.96,5.65,2.75), color=(.24,.24,.22)))
flag.include('light fabric field', box((.50,.025,1.02), center=(1.74,7.77,2.56), color=(.84,.82,.75)))
for i in range(7):
    x = 1.50+i*.075
    flag.include('red stripe %02d' % i, box((.038,.014,.95), center=(x,7.75,2.56), color=(.59,.08,.09)))
flag.include('blue canton', box((.23,.018,.35), center=(1.59,7.735,2.87), color=(.10,.16,.29)))
scene.include('flag', flag)

debris = Asset('Floor debris')
pieces = [
    ((1.05,.62,.035),(-2.7,.3,.035),-13,(.20,.21,.19)),
    ((.85,.42,.028),(-1.6,2.6,.03),16,(.18,.19,.17)),
    ((1.35,.54,.035),(-1.95,-2.0,.04),-10,(.25,.25,.22)),
    ((.78,.37,.025),(-3.25,1.5,.025),8,(.27,.27,.24)),
    ((.70,.30,.024),(.6,2.5,.025),-18,(.38,.37,.31)),
    ((.55,.24,.018),(-1.1,3.3,.02),-8,(.29,.29,.25)),
]
for i,(size,center,angle,color) in enumerate(pieces):
    p = box(size, center=center, color=color)
    p.turn(axis='+z', degrees=angle)
    debris.include('broken panel %02d' % i, p)

strips = [
    ((-3.3,-.9,.055),(-1.0,-1.65,.055),.025,(.55,.57,.55)),
    ((-2.9,-2.2,.065),(-1.0,-2.9,.065),.025,(.30,.31,.29)),
    ((-2.65,.55,.07),(-1.15,.26,.07),.018,(.48,.49,.45)),
    ((-2.9,2.8,.05),(-1.4,3.1,.05),.016,(.42,.43,.39)),
    ((1.25,-2.5,.025),(2.9,-4.5,.025),.035,(.61,.58,.51)),
    ((1.55,-2.6,.03),(3.0,-4.2,.03),.035,(.67,.65,.59)),
    ((-2.5,-1.75,.06),(-1.3,-2.5,.06),.015,(.12,.13,.12)),
]
for i,(start,end,r,col) in enumerate(strips):
    debris.include('loose strip %02d' % i, rod(r, start=start, end=end, color=col))
for i,(x,y) in enumerate(((-3,1.1),(-2.3,2.1),(-.9,1.4),(0,2.8),(.9,3.2),(-1.9,-.8),(.4,.6))):
    debris.include('small fragment %02d' % i, box((.13,.10,.018), center=(x,y,.02), color=(.37,.37,.32)))
scene.include('floor debris', debris)

mat = Asset('Yellow folded floor insulation')
mat.include('lower folded layer', box((1.95,1.55,.07), center=(1.55,-1.15,.045), color=(.64,.51,.21)))
mat.include('middle folded layer', box((1.90,1.40,.07), center=(1.60,-1.27,.105), color=(.73,.60,.27)))
top = box((1.92,1.42,.065), center=(1.70,-1.40,.16), color=(.78,.66,.31))
top.turn(axis='+z', degrees=-8)
mat.include('upper yellow sheet', top)
mat.include('left folded edge', box((.16,1.30,.10), center=(.67,-1.09,.10), color=(.80,.67,.33)))
mat.include('second folded edge', box((.12,1.28,.09), center=(.84,-1.10,.12), color=(.69,.55,.23)))
scene.include('yellow floor insulation', mat)

realize(scene)

sc = bpy.context.scene
if sc.world is None:
    sc.world = bpy.data.worlds.new('SceneWorld')
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get('Background')
if background is None:
    background = sc.world.node_tree.nodes.new('ShaderNodeBackground')
output = sc.world.node_tree.nodes.get('World Output')
if output is None:
    output = sc.world.node_tree.nodes.new('ShaderNodeOutputWorld')
sc.world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
background.inputs['Color'].default_value = (.72,.75,.76,1)
background.inputs['Strength'].default_value = .55

# Subtle procedural carpet mottling, shared across the large floor surface.
floor_obj = None
for obj in sc.objects:
    if obj.type == 'MESH' and obj.dimensions.x > 7 and obj.dimensions.y > 16 and obj.dimensions.z < .2 and obj.location.z < .1:
        floor_obj = obj
        break
if floor_obj is not None:
    material = bpy.data.materials.new('Dark mottled carpet')
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get('Principled BSDF')
    tex = nodes.new('ShaderNodeTexNoise')
    tex.inputs['Scale'].default_value = 170
    tex.inputs['Detail'].default_value = 2
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (.035,.037,.032,1)
    ramp.color_ramp.elements[1].color = (.14,.14,.12,1)
    links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 1
    floor_obj.data.materials.clear()
    floor_obj.data.materials.append(material)

set_view((-2.0,-8.6,1.72), (2.55,7.7,1.50), lens=30, sensor=36)
area_emitter((-1.8,-2.0,3.05), power=450, size=5.0, target=(0,3,0))
area_emitter((-3.5,5.0,2.8), power=300, size=4.0, target=(1,5,1))
area_emitter((1.0,3.0,3.15), power=180, size=3.0, target=(1,3,0))
