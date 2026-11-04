from sceneact import *
import bpy
import math

# Major dimensions and camera are estimated from the single photograph.
ROOM_WIDTH = 4.5
ROOM_DEPTH = 10.5
CEILING_HEIGHT = 3.25
CAMERA_POSITION = (0.35, -3.5, 1.64)
CAMERA_TARGET = (-0.10, 4.3, 1.62)
CAMERA_LENS = 26.0

COLUMN_X = 1.26
COLUMN_Y = 0.05
BULKHEAD_Y = 2.65

scene = Scene('Shipboard compartment')

cream = (.60, .60, .47)
ivory = (.72, .72, .60)
redfloor = (.29, .105, .062)
iron = (.035, .055, .049)
gray = (.32, .35, .31)
linen = (.67, .69, .61)
wood = (.32, .13, .065)

def cube(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def pipe(parent, name, radius, start, end, color=ivory):
    parent.include(
        name,
        rod(radius=radius, start=start, end=end, color=color)
    )

architecture = Asset('Architecture')
cube(architecture, 'floor',
     (4.8, 12.0, .14), (0, 2.1, -.07), redfloor)
cube(architecture, 'left_wall',
     (.15, 11.0, CEILING_HEIGHT),
     (-2.28, 2.0, CEILING_HEIGHT / 2), cream)
cube(architecture, 'rear_wall',
     (ROOM_WIDTH, .15, CEILING_HEIGHT),
     (0, 7.05, CEILING_HEIGHT / 2), cream)
cube(architecture, 'ceiling',
     (4.8, 11.0, .16), (0, 2.0, 3.33), (.35, .30, .20))

# A transverse bulkhead borders the opening into the rear compartment.
cube(architecture, 'right_bulkhead',
     (1.18, .16, CEILING_HEIGHT),
     (1.69, BULKHEAD_Y, CEILING_HEIGHT / 2), ivory)
cube(architecture, 'right_red_base',
     (1.18, .025, .34),
     (1.69, BULKHEAD_Y - .094, .17), (.29, .12, .07))
cube(architecture, 'right_side_wall',
     (.16, 4.4, CEILING_HEIGHT),
     (2.20, 4.85, CEILING_HEIGHT / 2), cream)
cube(architecture, 'rear_red_base',
     (4.4, .025, .29), (0, 6.95, .145), (.28, .12, .07))

for i, y in enumerate([-1.5, .4, 2.3, 4.2, 6.1]):
    cube(architecture, f'crossbeam_{i}',
         (4.5, .13, .22), (0, y, 3.12), wood)
for i, x in enumerate([-1.8, -.7, .45, 1.55]):
    cube(architecture, f'ceiling_joist_{i}',
         (.10, 10.0, .19), (x, 2.0, 3.18), (.43, .25, .13))
scene.include('architecture', architecture)

column = Asset('Cream and oxblood column')
pipe(column, 'lower', .105,
     (COLUMN_X, COLUMN_Y, .05),
     (COLUMN_X, COLUMN_Y, 1.52), (.28, .095, .045))
pipe(column, 'upper', .107,
     (COLUMN_X, COLUMN_Y, 1.52),
     (COLUMN_X, COLUMN_Y, 3.30), (.71, .66, .46))
pipe(column, 'foot', .135,
     (COLUMN_X, COLUMN_Y, .025),
     (COLUMN_X, COLUMN_Y, .07), (.33, .15, .09))
pipe(column, 'collar', .12,
     (COLUMN_X, COLUMN_Y, 3.02),
     (COLUMN_X, COLUMN_Y, 3.13), (.55, .43, .25))
scene.include('main_column', column)

bunks = Asset('Port three tier bunks')
for i, y in enumerate([1.65, 5.45]):
    for j, x in enumerate([-2.05, -.82]):
        pipe(bunks, f'post_{i}_{j}', .025,
             (x, y, .10), (x, y, 2.38), iron)
        pipe(bunks, f'cap_{i}_{j}', .034,
             (x, y, 2.35), (x, y, 2.41), iron)

for tier, z in enumerate([.47, 1.03, 1.59]):
    cube(bunks, f'bed_pan_{tier}',
         (1.19, 3.77, .065), (-1.44, 3.55, z), (.13, .16, .13))
    cube(bunks, f'mattress_{tier}',
         (1.12, 3.68, .115), (-1.44, 3.55, z + .085), linen)
    cube(bunks, f'pillow_{tier}',
         (.78, .50, .12), (-1.43, 4.95, z + .19), (.76, .77, .68))
    for side, x in enumerate([-2.035, -.845]):
        pipe(bunks, f'long_rail_{tier}_{side}', .022,
             (x, 1.65, z), (x, 5.45, z), iron)
    pipe(bunks, f'end_rail_{tier}', .022,
         (-2.05, 1.65, z + .20), (-.82, 1.65, z + .20), iron)
    cube(bunks, f'blanket_{tier}',
         (.98, .72, .045), (-1.45, 2.05, z + .163), (.45, .48, .40))

pipe(bunks, 'high_rail', .022,
     (-.82, 1.65, 2.33), (-.82, 5.45, 2.33), iron)
scene.include('bunks', bunks)

storage = Asset('Port ventilated cabinets')
for k, y in enumerate([-.05, .70]):
    cube(storage, f'body_{k}',
         (.65, .64, .97), (-1.79, y, .91), (.055, .10, .095))
    cube(storage, f'door_{k}',
         (.035, .56, .87), (-1.445, y, .91), (.095, .15, .14))
    for n in range(17):
        cube(storage, f'louver_{k}_{n}',
             (.018, .43, .013),
             (-1.42, y, .55 + n * .043), (.27, .32, .28))
    cube(storage, f'handle_{k}',
         (.025, .045, .13), (-1.403, y - .20, .95), iron)
cube(storage, 'top_ledge',
     (.83, 1.65, .055), (-1.8, .33, 1.43), iron)
scene.include('port_lockers', storage)

bench = Asset('Port bench')
cube(bench, 'seat',
     (.47, 4.35, .065), (-1.78, -.05, .42), (.025, .075, .063))
for i, y in enumerate([-1.8, -.2, 1.6]):
    for j, x in enumerate([-1.96, -1.60]):
        pipe(bench, f'leg_{i}_{j}', .018,
             (x, y, .02), (x, y, .40), iron)
scene.include('left_bench', bench)

rightbench = Asset('Right foreground bench')
cube(rightbench, 'seat',
     (.48, 2.8, .075), (1.95, -1.35, .49), (.025, .075, .059))
for i, y in enumerate([-2.5, -.3]):
    for j, x in enumerate([1.77, 2.12]):
        pipe(rightbench, f'leg_{i}_{j}', .019,
             (x, y, .01), (x, y, .47), iron)
scene.include('right_bench', rightbench)

equipment = Asset('Rear steel equipment')
cube(equipment, 'cabinet',
     (1.04, .62, 1.86), (-.28, 5.85, 1.10), (.39, .42, .37))
cube(equipment, 'left_door',
     (.48, .028, 1.73), (-.54, 5.52, 1.10), (.44, .46, .40))
cube(equipment, 'right_door',
     (.48, .028, 1.73), (-.02, 5.52, 1.10), (.37, .40, .35))
for i in range(10):
    cube(equipment, f'vent_{i}',
         (.23, .016, .018), (-.55, 5.497, 1.15 + i * .055),
         (.20, .24, .21))
for i, z in enumerate([.39, .83, 1.27, 1.70]):
    cube(equipment, f'hinge_{i}',
         (.06, .045, .10), (.19, 5.48, z), (.18, .20, .17))
cube(equipment, 'handle',
     (.035, .06, .24), (-.10, 5.47, 1.18), (.13, .15, .12))
for i, x in enumerate([-.66, -.30, .07]):
    pipe(equipment, f'top_duct_{i}', .075,
         (x, 5.9, 2.03), (x, 5.9, 2.28), gray)
scene.include('rear_locker', equipment)

machinery = Asset('Aisle machinery')
cube(machinery, 'dark_housing',
     (.79, .83, .91), (.65, 4.50, .53), (.18, .20, .16))
cube(machinery, 'front_panel',
     (.66, .035, .68), (.65, 4.065, .59), (.25, .27, .21))
cube(machinery, 'top',
     (.89, .91, .07), (.65, 4.5, 1.02), (.24, .25, .18))
for i, x in enumerate([.34, .68, .95]):
    pipe(machinery, f'valve_stem_{i}', .024,
         (x, 4.45, 1.04), (x, 4.45, 1.24), (.35, .31, .18))
    pipe(machinery, f'valve_bar_{i}', .015,
         (x - .09, 4.45, 1.24), (x + .09, 4.45, 1.24), iron)
scene.include('machinery', machinery)

chair = Asset('Pale metal chair')
cube(chair, 'seat',
     (.46, .44, .06), (-.43, 4.11, .48), (.47, .48, .37))
cube(chair, 'back',
     (.43, .055, .35), (-.43, 4.31, .86), (.52, .53, .43))
for i, x in enumerate([-.63, -.23]):
    for j, y in enumerate([3.94, 4.29]):
        pipe(chair, f'leg_{i}_{j}', .018,
             (x, y, .03), (x, y, .47), (.52, .53, .42))
    pipe(chair, f'back_frame_{i}', .02,
         (x, 4.31, .45), (x, 4.31, 1.06), (.57, .58, .46))
    pipe(chair, f'arm_{i}', .018,
         (x, 3.97, .70), (x, 4.30, .70), (.55, .56, .44))
scene.include('chair', chair)

vent = Asset('Port wall ventilator')
cube(vent, 'case',
     (.20, .70, .77), (-2.12, .58, 2.20), (.62, .62, .49))
cube(vent, 'dark_opening',
     (.022, .52, .55), (-2.005, .58, 2.19), (.045, .063, .057))
for i in range(6):
    cube(vent, f'blade_{i}',
         (.045, .49, .038), (-1.98, .58, 1.96 + i * .085),
         (.68, .68, .56))
scene.include('wall_vent', vent)

wallitems = Asset('Starboard fittings')
wall_front = BULKHEAD_Y - .08
cube(wallitems, 'slate_frame',
     (.79, .055, .80), (1.66, wall_front - .03, 1.94),
     (.33, .34, .27))
cube(wallitems, 'slate',
     (.72, .025, .72), (1.66, wall_front - .073, 1.94),
     (.20, .24, .21))
cube(wallitems, 'white_notice',
     (.30, .025, .85), (2.13, wall_front - .025, 1.70),
     (.78, .78, .66))
for i in range(8):
    cube(wallitems, f'notice_line_{i}',
         (.23, .009, .012),
         (2.13, wall_front - .043, 1.91 - i * .055),
         (.43, .43, .37))
cube(wallitems, 'red_mount',
     (.40, .10, .65), (1.48, wall_front - .06, 1.11),
     (.68, .045, .025))
pipe(wallitems, 'extinguisher', .12,
     (1.48, wall_front - .19, .88),
     (1.48, wall_front - .19, 1.28), (.78, .055, .028))
pipe(wallitems, 'extinguisher_neck', .045,
     (1.48, wall_front - .19, 1.28),
     (1.48, wall_front - .19, 1.39), (.27, .25, .16))
pipe(wallitems, 'handle', .022,
     (1.38, wall_front - .19, 1.40),
     (1.58, wall_front - .19, 1.40), iron)
cube(wallitems, 'label',
     (.14, .014, .16), (1.48, wall_front - .315, 1.12),
     (.80, .70, .48))
scene.include('wall_fittings', wallitems)

pipes = Asset('Overhead and rear pipework')
pipe(pipes, 'port_main', .055,
     (-1.80, -2, 2.80), (-1.80, 6.8, 2.80))
pipe(pipes, 'parallel_main', .035,
     (-1.36, -2, 2.92), (-1.36, 6.5, 2.92))
pipe(pipes, 'rear_cross', .047,
     (-2.1, 5.2, 2.69), (1.9, 5.2, 2.69), iron)
pipe(pipes, 'rear_riser', .035,
     (.91, 5.20, .1), (.91, 5.20, 2.69), iron)
pipe(pipes, 'rear_second_riser', .026,
     (1.29, 5.65, .1), (1.29, 5.65, 2.89), gray)
pipe(pipes, 'back_horizontal', .037,
     (-1.9, 6.65, 2.47), (1.65, 6.65, 2.47))
for i, y in enumerate([-.6, 1.1, 2.8, 4.5, 6.2]):
    pipe(pipes, f'hanger_{i}', .015,
         (-1.80, y, 2.80), (-1.80, y, 3.2), iron)
    pipe(pipes, f'branch_{i}', .033,
         (-1.80, y, 2.80), (-1.25, y, 2.58))
    pipe(pipes, f'branch_upright_{i}', .033,
         (-1.25, y, 2.58), (-1.25, y, 3.15))
for i, x in enumerate([-.05, .35, .70]):
    pipe(pipes, f'back_duct_{i}', .067,
         (x, 6.75, 2.0), (x, 6.75, 3.13), (.36, .37, .28))
scene.include('pipes', pipes)

# Keep each luminous underside in its own named asset for material targeting.
lamps = Asset('Pendant lamps')
lamp_locations = [
    (-.83, -.02, 2.77),
    (-.49, 3.45, 2.72),
    (-.24, 5.75, 2.67)
]
for i, (x, y, z) in enumerate(lamp_locations):
    lamp = Asset(f'Pendant_{i}')
    pipe(lamp, 'drop', .022,
         (x, y, z + .13), (x, y, 3.24), iron)
    pipe(lamp, 'neck', .07,
         (x, y, z + .01), (x, y, z + .12), (.20, .23, .20))
    pipe(lamp, 'shade_top', .15,
         (x, y, z - .025), (x, y, z + .015), (.48, .50, .43))
    pipe(lamp, 'shade_rim', .265,
         (x, y, z - .075), (x, y, z - .035), (.70, .72, .66))
    underside = Asset(f'LampGlow_{i}')
    pipe(underside, 'disc', .235,
         (x, y, z - .084), (x, y, z - .076), (.96, .98, .90))
    lamp.include(f'LampGlow_{i}', underside)
    lamps.include(f'Pendant_{i}', lamp)
scene.include('lamps', lamps)

seams = Asset('Deck joints')
for i, y in enumerate([-.6, 1.0, 2.8, 4.6, 6.4]):
    cube(seams, f'seam_{i}',
         (4.4, .012, .003), (0, y, .003), (.20, .075, .043))
scene.include('deck_seams', seams)

realize(scene)

set_view(
    position=CAMERA_POSITION,
    target=CAMERA_TARGET,
    lens=CAMERA_LENS,
    sensor=36
)

bs = bpy.context.scene
if bs.world is None:
    bs.world = bpy.data.worlds.new('World')
bs.world.use_nodes = True
background = bs.world.node_tree.nodes.get('Background')
if background:
    background.inputs['Color'].default_value = (.34, .36, .29, 1)
    background.inputs['Strength'].default_value = .32

area_emitter(
    position=(-.83, -.02, 2.64), power=190, size=.65,
    target=(-.8, .8, 0), color=(1.0, .94, .78)
)
area_emitter(
    position=(-.49, 3.45, 2.59), power=150, size=.5,
    target=(-.3, 3.5, .1), color=(.88, .95, 1.0)
)
area_emitter(
    position=(-.24, 5.75, 2.54), power=110, size=.45,
    target=(0, 5.6, .5), color=(1, .96, .81)
)
area_emitter(
    position=(.1, -2.8, 2.45), power=100, size=3,
    target=(0, 3, 1.4), color=(1, .86, .68)
)

def mesh_descendants(root):
    if root.type == 'MESH':
        yield root
    for child in root.children:
        yield from mesh_descendants(child)

for i in range(len(lamp_locations)):
    marker = bpy.data.objects.get(f'LampGlow_{i}')
    if marker is None:
        continue
    for obj in mesh_descendants(marker):
        for slot in obj.material_slots:
            if slot.material is None:
                continue
            material = slot.material.copy()
            slot.material = material
            material.use_nodes = True
            shader = material.node_tree.nodes.get('Principled BSDF')
            if shader is None:
                continue
            if 'Emission Color' in shader.inputs:
                shader.inputs['Emission Color'].default_value = (.92, .98, 1, 1)
            elif 'Emission' in shader.inputs:
                shader.inputs['Emission'].default_value = (.92, .98, 1, 1)
            if 'Emission Strength' in shader.inputs:
                shader.inputs['Emission Strength'].default_value = 2.5

bs.view_settings.view_transform = 'AgX'
