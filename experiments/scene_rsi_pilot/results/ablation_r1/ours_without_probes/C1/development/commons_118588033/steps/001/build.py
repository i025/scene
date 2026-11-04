from sceneact import *
import bpy
import math

# Visual estimates in normalized image coordinates:
# Column floor contact (.72,.84), ceiling intersection (.77,.02).
# Front bunk upright (.39,.69), upper mattress edge (.25,.44).
# Blue lockers (.10,.59), rear steel lockers (.49,.46).
# Red wall fitting (.81,.55), rear chair contact (.48,.66).
# Foreground right bench enters near (.92,.87).
# Rear floor boundary is near (.57,.67).
# Arbitrary world scale; camera distance and bunk depth remain uncertain.
# This source audit has no rendered evidence of image quality or edit success.

# CAMERA — independent of object dimensions.
CAM_POS = (0.05, -4.2, 1.66)
CAM_TARGET = (0.04, 3.0, 1.69)
LENS = 26

# ARCHITECTURE
ROOM_W, ROOM_D, ROOM_H = 4.4, 9.2, 3.55

# OBJECT DIMENSIONS AND POSES
BUNK_X, BUNK_Y = -1.35, 1.48
BUNK_W, BUNK_L = 1.28, 3.25
BUNK_LEVELS = (0.48, 1.12, 1.76)
POLE = (0.77, -1.45)

# MATERIALS
FLOOR = (.30, .105, .060)
WALL = (.62, .63, .52)
CREAM = (.76, .75, .60)
IRON = (.075, .095, .085)
STEEL = (.39, .43, .40)
BLUE = (.085, .16, .19)
BED = (.66, .68, .59)
WOOD = (.40, .19, .085)

# LIGHTING
PENDANTS = (
    (-.65, -1.10, 2.94, .29),
    (-.38, 1.62, 2.86, .18),
    (.10, 3.50, 2.84, .15),
)

scene = Scene('Shipboard sleeping and machinery compartment')

# Helpers audit dimensions and prevent silent include replacement.
def finite_vector(v):
    return all(math.isfinite(float(n)) for n in v)

def attach(parent, name, node):
    assert name not in parent.members, f'Duplicate include key: {name}'
    return parent.include(name, node)

def put(parent, name, size, center, color):
    assert finite_vector(size) and all(n > 0 for n in size)
    assert finite_vector(center)
    return attach(parent, name, box(size=size, center=center, color=color))

def tube(parent, name, a, b, radius=.022, color=IRON):
    assert math.isfinite(radius) and radius > 0
    assert finite_vector(a) and finite_vector(b)
    assert sum((a[i] - b[i]) ** 2 for i in range(3)) > 1e-12
    return attach(parent, name, rod(radius=radius, start=a, end=b, color=color))

def sphere(parent, name, radius, center, color):
    assert math.isfinite(radius) and radius > 0
    assert finite_vector(center)
    return attach(parent, name, ball(radius=radius, center=center, color=color))

# Inventory: shell, column, three bunks, blue cabinets, rear lockers,
# utility machinery, chair, wall fittings, heater, two cropped benches,
# overhead services and three pendant lamps. All geometry belongs to Assets.

architecture = Asset('Compartment shell')
put(architecture, 'painted plank floor',
    (ROOM_W, ROOM_D, .12), (0, 1.1, -.06), FLOOR)
put(architecture, 'port bulkhead',
    (.12, ROOM_D, ROOM_H), (-2.2, 1.1, 1.775), WALL)
put(architecture, 'rear bulkhead',
    (ROOM_W, .14, ROOM_H), (0, 5.65, 1.775), CREAM)
put(architecture, 'starboard bulkhead',
    (.12, ROOM_D, ROOM_H), (2.2, 1.1, 1.775), CREAM)
put(architecture, 'overhead deck',
    (ROOM_W, ROOM_D, .15), (0, 1.1, 3.60), (.31, .29, .23))
put(architecture, 'rear red skirting',
    (4.4, .055, .34), (0, 5.55, .17), (.32, .12, .075))
put(architecture, 'port skirting',
    (.04, 9, .25), (-2.12, 1.1, .125), WOOD)
for i in range(16):
    put(architecture, f'floor board seam {i}',
        (4.32, .009, .004), (0, -3.3 + i * .56, .003), (.21, .075, .045))
for i, x in enumerate((-1.8, -.9, 0, .9, 1.8)):
    put(architecture, f'ceiling longitudinal joist {i}',
        (.09, 9, .22), (x, 1.1, 3.39), WOOD)
for i, y in enumerate((-2.2, -.2, 2.0, 4.1)):
    put(architecture, f'transverse overhead beam {i}',
        (4.3, .15, .28), (0, y, 3.30), (.47, .27, .13))
attach(scene, 'architecture', architecture)

column = Asset('Foreground cream and brown support column')
tube(column, 'lower brown shaft',
     (POLE[0], POLE[1], .04), (POLE[0], POLE[1], 1.49),
     .105, (.34, .16, .075))
tube(column, 'upper cream shaft',
     (POLE[0], POLE[1], 1.49), (POLE[0], POLE[1], 3.53),
     .105, (.70, .66, .48))
tube(column, 'foot flange',
     (POLE[0], POLE[1], .015), (POLE[0], POLE[1], .055),
     .14, (.41, .25, .14))
attach(scene, 'main support', column)

# Decks support mattresses; upright posts extend to the floor.
bunks = Asset('Three tier port sleeping rack')
front_y = BUNK_Y - BUNK_L / 2
back_y = BUNK_Y + BUNK_L / 2
for i, x in enumerate((-1.99, -.71)):
    for j, y in enumerate((front_y, back_y)):
        tube(bunks, f'upright {i} {j}', (x, y, .0), (x, y, 2.42), .027)
for k, z in enumerate(BUNK_LEVELS):
    put(bunks, f'bunk steel deck {k}',
        (BUNK_W, BUNK_L, .065), (BUNK_X, BUNK_Y, z - .06), IRON)
    put(bunks, f'mattress {k}',
        (BUNK_W - .045, BUNK_L - .06, .105),
        (BUNK_X, BUNK_Y, z + .025), BED)
    put(bunks, f'folded pillow {k}',
        (.78, .48, .14), (BUNK_X, back_y - .40, z + .14),
        (.76, .76, .67))
    tube(bunks, f'outer long edge {k}',
         (-.70, front_y, z), (-.70, back_y, z), .025, STEEL)
    tube(bunks, f'front rail {k}',
         (-1.99, front_y, z - .045), (-.70, front_y, z - .045), .022)
attach(scene, 'port bunks', bunks)

cabinets = Asset('Blue foreground ventilated lockers')
for i, y in enumerate((-.99, -.30)):
    put(cabinets, f'cabinet body {i}',
        (.55, .62, 1.00), (-1.94, y, .65), BLUE)
    put(cabinets, f'door panel {i}',
        (.025, .54, .88), (-1.647, y, .65), (.12, .21, .24))
    for j in range(15):
        put(cabinets, f'vent opening {i} {j}',
            (.012, .40, .014), (-1.630, y, .29 + j * .045),
            (.025, .055, .06))
    put(cabinets, f'door latch {i}',
        (.035, .035, .09), (-1.613, y - .19, .72), (.48, .49, .42))
# Shelf top meets cabinet bottoms at z=.15; riser supports the shelf.
put(cabinets, 'cabinet supporting ledge',
    (.81, 1.65, .09), (-1.84, -.66, .105), (.08, .11, .09))
put(cabinets, 'ledge floor support',
    (.65, 1.55, .06), (-1.84, -.66, .03), (.08, .11, .09))
attach(scene, 'blue lockers', cabinets)

lockers = Asset('Rear steel storage lockers')
for i, x in enumerate((-.67, -.09, .49)):
    put(lockers, f'body {i}', (.55, .56, 1.82), (x, 4.42, 1.05), STEEL)
    put(lockers, f'door {i}',
        (.515, .027, 1.73), (x, 4.12, 1.05), (.46, .49, .45))
    for j in range(4):
        put(lockers, f'upper ventilation {i} {j}',
            (.26, .012, .023), (x, 4.098, 1.60 - j * .075),
            (.22, .27, .25))
    put(lockers, f'latch {i}',
        (.035, .035, .13), (x + .18, 4.073, 1.05), (.15, .17, .15))
    for j, xx in enumerate((x - .20, x + .20)):
        put(lockers, f'foot {i} {j}',
            (.045, .42, .15), (xx, 4.42, .075), IRON)
    sphere(lockers, f'rounded baggage {i}', .17,
           (x, 4.44, 2.01), (.34, .37, .31))
attach(scene, 'rear lockers', lockers)

machine = Asset('Central dark utility machinery')
put(machine, 'housing', (.82, .72, .98), (.45, 2.94, .54), (.23, .26, .22))
put(machine, 'top cover',
    (.89, .77, .055), (.45, 2.94, 1.0575), (.29, .31, .26))
put(machine, 'front panel',
    (.72, .025, .79), (.45, 2.565, .55), (.27, .29, .25))
for i, x in enumerate((.12, .75)):
    tube(machine, f'front support {i}', (x, 2.64, 0), (x, 2.64, .18), .035)
for i, x in enumerate((.19, .65)):
    tube(machine, f'vertical brass pipe {i}',
         (x, 2.94, 1.08), (x, 2.94, 2.75), .027, (.35, .31, .18))
    tube(machine, f'pipe top cross {i}',
         (x, 2.94, 2.75), (x, 4.8, 2.75), .027, IRON)
    sphere(machine, f'valve center {i}', .065,
           (x, 2.94, 1.28), (.35, .31, .18))
    tube(machine, f'valve handle {i}',
         (x - .11, 2.94, 1.29), (x + .11, 2.94, 1.29), .014)
attach(scene, 'utility machine', machine)

chair = Asset('Pale metal chair in rear aisle')
cx, cy = -.40, 2.49
put(chair, 'seat', (.46, .43, .06), (cx, cy, .49), (.47, .46, .33))
for i, x in enumerate((cx - .21, cx + .21)):
    for j, y in enumerate((cy - .18, cy + .18)):
        tube(chair, f'leg {i} {j}',
             (x, y, 0), (x, y, .48), .019, (.63, .62, .46))
    tube(chair, f'back upright {i}',
         (x, cy + .18, .46), (x, cy + .26, .96),
         .021, (.62, .61, .46))
put(chair, 'backrest',
    (.43, .06, .24), (cx, cy + .23, .83), (.45, .46, .35))
attach(scene, 'aisle chair', chair)

wallfit = Asset('Starboard display bulkhead and fittings')
put(wallfit, 'partition', (1.38, .12, 3.12), (1.50, 2.85, 1.56), CREAM)
put(wallfit, 'brown lower paint',
    (1.38, .018, .35), (1.50, 2.777, .175), (.32, .13, .075))
put(wallfit, 'dark framed notice board',
    (.88, .07, .92), (1.49, 2.75, 1.99), (.27, .28, .23))
put(wallfit, 'slate board face',
    (.80, .015, .84), (1.49, 2.707, 1.99), (.25, .29, .27))
put(wallfit, 'white paper notice',
    (.37, .012, .69), (2.02, 2.70, 1.51), (.78, .78, .67))
put(wallfit, 'red emergency backplate',
    (.37, .10, .63), (1.35, 2.67, 1.02), (.78, .045, .022))
sphere(wallfit, 'round red top', .18, (1.35, 2.65, 1.30), (.80, .055, .025))
put(wallfit, 'emergency handle',
    (.12, .10, .25), (1.35, 2.57, 1.11), (.24, .19, .11))
sphere(wallfit, 'handle bright cap', .058,
       (1.35, 2.51, 1.32), (.78, .75, .57))
for i in range(6):
    put(wallfit, f'paper text {i}',
        (.25, .007, .008), (2.02, 2.688, 1.70 - i * .055), (.40, .42, .35))
attach(scene, 'right wall fittings', wallfit)

vent = Asset('High port wall air heater')
put(vent, 'pale rectangular casing',
    (.20, .66, .84), (-2.03, .26, 2.37), (.66, .66, .54))
for i in range(7):
    put(vent, f'dark grille slit {i}',
        (.017, .51, .045), (-1.92, .26, 2.12 + i * .075), (.055, .075, .067))
put(vent, 'top label',
    (.017, .24, .055), (-1.914, .26, 2.68), (.28, .28, .23))
attach(scene, 'port ventilation unit', vent)

# Seat undersides meet the tops of their floor-supported legs.
for name, x, y, length in (
    ('port', -1.68, -1.12, 3.4),
    ('starboard', 1.55, -2.00, 2.2),
):
    bench = Asset(name + ' foreground bench')
    put(bench, 'dark green seat',
        (.59, length, .08), (x, y, .45), (.045, .11, .075))
    for i, yy in enumerate((y - length / 2 + .18, y + length / 2 - .18)):
        for j, xx in enumerate((x - .23, x + .23)):
            tube(bench, f'leg {i} {j}', (xx, yy, 0), (xx, yy, .41), .025)
    attach(scene, name + ' bench', bench)

pipes = Asset('Overhead service pipes and hangers')
for i, x in enumerate((-1.77, -1.38, .24)):
    tube(pipes, f'long pipe {i}',
         (x, -2.4, 2.97), (x, 5.4, 2.97), .034, CREAM)
for i, y in enumerate((-.9, .85, 2.55, 4.25)):
    tube(pipes, f'cross service {i}',
         (-2.1, y, 3.00), (.60, y, 3.00), .025, IRON)
    tube(pipes, f'hanger {i}',
         (-1.42, y, 3.03), (-1.42, y, 3.51), .018, CREAM)
pipe_points = [
    (-1.9, -1.4, 3.23),
    (-1.05, -.35, 2.91),
    (-.85, .25, 2.85),
    (-.85, 1.4, 2.85),
    (-.65, 1.65, 3.05),
]
assert all(finite_vector(p) for p in pipe_points)
assert all(
    sum((a[k] - b[k]) ** 2 for k in range(3)) > 1e-12
    for a, b in zip(pipe_points, pipe_points[1:])
)
attach(pipes, 'bent pale pipe',
       sweep_tube(points=pipe_points, radius=.043, color=CREAM))
attach(scene, 'service pipes', pipes)

# Dedicated diffuser Assets allow exact, isolated material customization.
diffuser_parent_names = []
for i, (x, y, z, radius) in enumerate(PENDANTS):
    lamp = Asset(f'Pendant lamp {i}')
    tube(lamp, 'cord', (x, y, z + .11), (x, y, 3.48), .014)
    tube(lamp, 'metal shade',
         (x, y, z - .0125), (x, y, z + .0625),
         radius, (.33, .36, .33))
    diffuser_name = f'Pendant diffuser {i}'
    diffuser = Asset(diffuser_name)
    tube(diffuser, 'luminous disk',
         (x, y, z - .036), (x, y, z - .014),
         radius * .91, (.95, .96, .84))
    attach(lamp, diffuser_name, diffuser)
    diffuser_parent_names.append(diffuser_name)
    attach(scene, f'ceiling pendant {i}', lamp)

# Source audit: all primitive dimensions and radii are positive and finite.
# No fillet_box is used. Rod endpoints and consecutive sweep points differ.
# Include keys are checked within each parent. Composite parts stay together.
realize(scene)

set_view(CAM_POS, CAM_TARGET, lens=LENS, sensor=36)

world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new('Dim compartment ambient')
    bpy.context.scene.world = world
world.use_nodes = True
background = world.node_tree.nodes.get('Background')
if background is None:
    background = world.node_tree.nodes.new('ShaderNodeBackground')
    output = world.node_tree.nodes.get('World Output')
    if output is None:
        output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
background.inputs['Color'].default_value = (.36, .37, .30, 1)
background.inputs['Strength'].default_value = .32

area_emitter(
    (-.65, -1.10, 2.84), power=150, size=.70,
    target=(-.7, -.4, .1), color=(.93, .96, 1.0))
area_emitter(
    (-.38, 1.62, 2.77), power=105, size=.65,
    target=(0, 2.3, .4), color=(.93, .97, 1.0))
area_emitter(
    (.10, 3.50, 2.75), power=90, size=.60,
    target=(0, 3.8, .5), color=(.98, 1.0, .91))
area_emitter(
    (.15, -3.3, 2.7), power=65, size=3,
    target=(0, 1, 1.1), color=(1.0, .83, .65))

for parent_name in diffuser_parent_names:
    parent = bpy.data.objects.get(parent_name)
    assert parent is not None, f'Missing diffuser parent: {parent_name}'
    meshes = [obj for obj in parent.children_recursive if obj.type == 'MESH']
    assert meshes, f'Empty diffuser subtree: {parent_name}'
    for obj in meshes:
        assert len(obj.material_slots) > 0
        for slot in obj.material_slots:
            assert slot.material is not None
            slot.material = slot.material.copy()
            slot.material.use_nodes = True
            bsdf = slot.material.node_tree.nodes.get('Principled BSDF')
            assert bsdf is not None
            emission = bsdf.inputs.get('Emission Color')
            if emission is None:
                emission = bsdf.inputs.get('Emission')
            assert emission is not None
            emission.default_value = (.84, .90, 1.0, 1)
            strength = bsdf.inputs.get('Emission Strength')
            if strength is not None:
                strength.default_value = 2.5

bpy.context.scene.view_settings.view_transform = 'AgX'
# The external runner controls output settings and performs the sole render.
