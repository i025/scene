from sceneact import *
import bpy

# Comparison with rendered step 2:
# 1. Left furniture is too far left: move bunk fronts and cabinets toward the
#    aisle, expose the long bench, and lower the upper two mattresses.
# 2. The foreground column is slightly too far right; the ventilator is cropped.
#    Move the column left and the ventilator forward along the port wall.
# 3. The deck is too pale and the rear equipment too brightly lit.
#    Darken the painted deck and equipment, with less rear illumination.

CAMERA_POSITION = (.35, -3.5, 1.64)
CAMERA_TARGET = (-.10, 4.3, 1.62)
CAMERA_LENS = 32.0
CAMERA_SHIFT = (0, -.08)
CEILING_HEIGHT = 3.25
REAR_Y = 5.65
BULKHEAD_Y = 2.20
COLUMN_X = .82
COLUMN_Y = .05

scene = Scene('Shipboard compartment')
cream = (.46, .47, .37)
ivory = (.61, .61, .49)
iron = (.022, .036, .030)
gray = (.25, .28, .24)
linen = (.57, .60, .52)
wood = (.29, .12, .055)
redfloor = (.115, .032, .017)

def cube(parent, name, size, center, color):
    parent.include(name, box(size=size, center=center, color=color))

def pipe(parent, name, radius, start, end, color=ivory):
    parent.include(name, rod(radius=radius, start=start, end=end, color=color))

architecture = Asset('Architecture')
cube(architecture, 'floor', (5.2, 12, .14), (0, 2.1, -.07), redfloor)
cube(architecture, 'left_wall', (.15, 11, CEILING_HEIGHT),
     (-2.28, 2, CEILING_HEIGHT/2), cream)
cube(architecture, 'rear_wall', (5.2, .15, CEILING_HEIGHT),
     (0, REAR_Y, CEILING_HEIGHT/2), cream)
cube(architecture, 'ceiling', (5.2, 11, .16),
     (0, 2, 3.33), (.28, .25, .17))
cube(architecture, 'right_bulkhead', (2.15, .16, CEILING_HEIGHT),
     (2.175, BULKHEAD_Y, CEILING_HEIGHT/2), ivory)
cube(architecture, 'right_red_base', (2.15, .025, .34),
     (2.175, BULKHEAD_Y-.094, .17), (.22, .065, .032))
cube(architecture, 'rear_red_base', (4.4, .025, .29),
     (0, REAR_Y-.09, .145), (.21, .065, .034))
for i, y in enumerate([-1.5, .4, 2.3, 4.2, 5.5]):
    cube(architecture, f'crossbeam_{i}', (5.0, .13, .22),
         (0, y, 3.12), wood)
for i, x in enumerate([-1.8, -.7, .45, 1.55]):
    cube(architecture, f'ceiling_joist_{i}', (.10, 10, .19),
         (x, 2, 3.18), (.39, .21, .10))
# Slender diagonal overhead braces visible beside the first pendant.
for i, y in enumerate([-1.25, .65, 2.55]):
    pipe(architecture, f'ceiling_brace_{i}', .033,
         (-1.05, y, 2.80), (-.60, y+.48, 3.22), (.43, .27, .15))
scene.include('architecture', architecture)

column = Asset('Cream and oxblood column')
pipe(column, 'lower', .105, (COLUMN_X, COLUMN_Y, .05),
     (COLUMN_X, COLUMN_Y, 1.47), (.19, .044, .020))
pipe(column, 'upper', .107, (COLUMN_X, COLUMN_Y, 1.47),
     (COLUMN_X, COLUMN_Y, 3.30), (.66, .59, .39))
pipe(column, 'foot', .135, (COLUMN_X, COLUMN_Y, .025),
     (COLUMN_X, COLUMN_Y, .07), (.25, .080, .035))
pipe(column, 'collar', .12, (COLUMN_X, COLUMN_Y, 3.02),
     (COLUMN_X, COLUMN_Y, 3.13), (.48, .36, .19))
scene.include('main_column', column)

bunks = Asset('Port three tier bunks')
BX = .40
NEAR_BUNK_Y = 1.40
FAR_BUNK_Y = 4.95
for i, y in enumerate([NEAR_BUNK_Y, FAR_BUNK_Y]):
    for j, x in enumerate([-2.05+BX, -.82+BX]):
        pipe(bunks, f'post_{i}_{j}', .025,
             (x, y, .04), (x, y, 2.22), iron)
        pipe(bunks, f'cap_{i}_{j}', .034,
             (x, y, 2.20), (x, y, 2.25), iron)
for tier, z in enumerate([.47, .96, 1.45]):
    cube(bunks, f'bed_pan_{tier}', (1.19, 3.55, .065),
         (-1.44+BX, 3.175, z), (.085, .115, .085))
    cube(bunks, f'mattress_{tier}', (1.12, 3.47, .115),
         (-1.44+BX, 3.175, z+.085), linen)
    cube(bunks, f'pillow_{tier}', (.78, .50, .12),
         (-1.43+BX, 4.58, z+.19), (.68, .70, .61))
    for side, x in enumerate([-2.035+BX, -.845+BX]):
        pipe(bunks, f'long_rail_{tier}_{side}', .022,
             (x, NEAR_BUNK_Y, z), (x, FAR_BUNK_Y, z), iron)
    pipe(bunks, f'end_rail_{tier}', .022,
         (-2.05+BX, NEAR_BUNK_Y, z+.15),
         (-.82+BX, NEAR_BUNK_Y, z+.15), iron)
    cube(bunks, f'blanket_{tier}', (.98, .66, .035),
         (-1.45+BX, 1.90, z+.16), (.46, .49, .41))
pipe(bunks, 'high_rail', .022,
     (-.82+BX, NEAR_BUNK_Y, 2.17),
     (-.82+BX, FAR_BUNK_Y, 2.17), iron)
scene.include('bunks', bunks)

storage = Asset('Port ventilated cabinets')
for k, y in enumerate([.12, .87]):
    cube(storage, f'body_{k}', (.65, .64, .83),
         (-1.60, y, .925), (.026, .052, .046))
    cube(storage, f'door_{k}', (.035, .56, .75),
         (-1.255, y, .925), (.043, .079, .069))
    for n in range(17):
        cube(storage, f'louver_{k}_{n}', (.018, .43, .012),
             (-1.23, y, .58+n*.041), (.13, .18, .15))
    cube(storage, f'handle_{k}', (.025, .045, .13),
         (-1.213, y-.20, .95), iron)
cube(storage, 'top_ledge', (.83, 1.65, .055),
     (-1.61, .50, 1.37), iron)
scene.include('port_lockers', storage)

bench = Asset('Port bench')
cube(bench, 'seat', (.47, 5.0, .065),
     (-1.40, .25, .42), (.012, .040, .030))
for i, y in enumerate([-1.8, -.2, 1.6, 2.5]):
    for j, x in enumerate([-1.58, -1.22]):
        pipe(bench, f'leg_{i}_{j}', .018,
             (x, y, .02), (x, y, .40), iron)
scene.include('left_bench', bench)

rightbench = Asset('Right foreground bench')
cube(rightbench, 'seat', (.48, 2.8, .075),
     (1.64, -1.35, .49), (.012, .045, .032))
for i, y in enumerate([-2.5, -.3]):
    for j, x in enumerate([1.46, 1.81]):
        pipe(rightbench, f'leg_{i}_{j}', .019,
             (x, y, .01), (x, y, .47), iron)
scene.include('right_bench', rightbench)

equipment = Asset('Rear steel equipment')
EY = 4.80
cube(equipment, 'cabinet', (1.04, .62, 1.72),
     (-.20, EY, 1.03), (.22, .25, .22))
cube(equipment, 'left_door', (.48, .028, 1.60),
     (-.46, EY-.33, 1.03), (.28, .31, .27))
cube(equipment, 'right_door', (.48, .028, 1.60),
     (.06, EY-.33, 1.03), (.24, .27, .23))
for i in range(10):
    cube(equipment, f'vent_{i}', (.23, .016, .018),
         (-.47, EY-.353, 1.09+i*.050), (.12, .16, .13))
for i, z in enumerate([.36, .77, 1.18, 1.60]):
    cube(equipment, f'hinge_{i}', (.06, .045, .10),
         (.27, EY-.37, z), (.10, .13, .10))
cube(equipment, 'handle', (.035, .06, .24),
     (-.02, EY-.38, 1.12), (.065, .09, .065))
for i, x in enumerate([-.58, -.22, .15]):
    pipe(equipment, f'top_duct_{i}', .075,
         (x, EY+.05, 1.89), (x, EY+.05, 2.14), gray)
scene.include('rear_locker', equipment)

machinery = Asset('Aisle machinery')
MX, MY = .50, 3.70
cube(machinery, 'dark_housing', (.79, .83, 1.03),
     (MX, MY, .59), (.075, .095, .070))
cube(machinery, 'front_panel', (.66, .035, .80),
     (MX, MY-.435, .65), (.11, .14, .10))
cube(machinery, 'top', (.89, .91, .07),
     (MX, MY, 1.14), (.12, .14, .09))
for i, x in enumerate([MX-.31, MX+.03, MX+.30]):
    pipe(machinery, f'valve_stem_{i}', .024,
         (x, MY-.05, 1.17), (x, MY-.05, 1.36), (.22, .20, .11))
    pipe(machinery, f'valve_bar_{i}', .015,
         (x-.09, MY-.05, 1.36), (x+.09, MY-.05, 1.36), iron)
scene.include('machinery', machinery)

chair = Asset('Pale metal chair')
CX, CY = -.34, 3.30
cube(chair, 'seat', (.46, .44, .06),
     (CX, CY, .48), (.28, .31, .23))
back = box(size=(.43, .055, .35),
           center=(CX, CY+.20, .86), color=(.12, .15, .11))
back.turn(axis='+x', degrees=12)
chair.include('back', back)
for i, x in enumerate([CX-.20, CX+.20]):
    for j, y in enumerate([CY-.17, CY+.18]):
        pipe(chair, f'leg_{i}_{j}', .018,
             (x, y, .03), (x, y, .47), (.46, .49, .37))
    pipe(chair, f'back_frame_{i}', .02,
         (x, CY+.20, .45), (x, CY+.24, 1.06), (.49, .52, .39))
    pipe(chair, f'arm_{i}', .018,
         (x, CY-.14, .70), (x, CY+.19, .70), (.48, .51, .38))
scene.include('chair', chair)

vent = Asset('Port wall ventilator')
VENT_Y = 2.45
cube(vent, 'case', (.20, .70, .77),
     (-2.12, VENT_Y, 2.20), (.55, .56, .43))
cube(vent, 'dark_opening', (.022, .52, .55),
     (-2.005, VENT_Y, 2.19), (.020, .031, .026))
for i in range(6):
    cube(vent, f'blade_{i}', (.045, .49, .038),
         (-1.98, VENT_Y, 1.96+i*.085), (.60, .62, .49))
scene.include('wall_vent', vent)

wallitems = Asset('Starboard fittings')
wall_front = BULKHEAD_Y-.08
cube(wallitems, 'slate_frame', (.79, .055, .80),
     (1.66, wall_front-.03, 1.94), (.28, .30, .23))
cube(wallitems, 'slate', (.72, .025, .72),
     (1.66, wall_front-.073, 1.94), (.15, .20, .17))
cube(wallitems, 'white_notice', (.35, .025, .85),
     (2.25, wall_front-.025, 1.70), (.72, .73, .62))
for i in range(8):
    cube(wallitems, f'notice_line_{i}', (.25, .009, .012),
         (2.25, wall_front-.043, 1.91-i*.055), (.37, .38, .31))
cube(wallitems, 'red_mount', (.40, .10, .65),
     (1.48, wall_front-.06, 1.11), (.60, .025, .012))
pipe(wallitems, 'extinguisher', .12,
     (1.48, wall_front-.19, .88), (1.48, wall_front-.19, 1.28),
     (.72, .035, .016))
pipe(wallitems, 'extinguisher_neck', .045,
     (1.48, wall_front-.19, 1.28), (1.48, wall_front-.19, 1.39),
     (.22, .22, .13))
pipe(wallitems, 'handle', .022,
     (1.38, wall_front-.19, 1.40), (1.58, wall_front-.19, 1.40), iron)
cube(wallitems, 'label', (.14, .014, .16),
     (1.48, wall_front-.315, 1.12), (.74, .66, .45))
scene.include('wall_fittings', wallitems)

pipes = Asset('Overhead and rear pipework')
pipe(pipes, 'port_main', .055,
     (-1.80, -2, 2.80), (-1.80, 5.45, 2.80))
pipe(pipes, 'parallel_main', .035,
     (-1.36, -2, 2.92), (-1.36, 5.40, 2.92))
pipe(pipes, 'rear_cross', .047,
     (-2.1, 4.3, 2.69), (1.9, 4.3, 2.69), iron)
pipe(pipes, 'rear_riser', .035,
     (.91, 4.3, .1), (.91, 4.3, 2.69), iron)
pipe(pipes, 'rear_second_riser', .026,
     (1.12, 4.75, .1), (1.12, 4.75, 2.89), gray)
pipe(pipes, 'back_horizontal', .037,
     (-1.9, 5.35, 2.47), (1.65, 5.35, 2.47))
for i, y in enumerate([-.6, 1.1, 2.8, 4.5]):
    pipe(pipes, f'hanger_{i}', .015,
         (-1.80, y, 2.80), (-1.80, y, 3.20), iron)
    pipe(pipes, f'branch_{i}', .033,
         (-1.80, y, 2.80), (-1.25, y, 2.58))
    pipe(pipes, f'branch_upright_{i}', .033,
         (-1.25, y, 2.58), (-1.25, y, 3.15))
for i, x in enumerate([-.05, .35, .70]):
    pipe(pipes, f'back_duct_{i}', .067,
         (x, 5.35, 2.0), (x, 5.35, 3.13), (.29, .31, .23))
scene.include('pipes', pipes)

lamps = Asset('Pendant lamps')
lamp_locations = [
    (-.18, -.02, 2.70),
    (-.22, 2.80, 2.66),
    (-.12, 4.85, 2.67)
]
for i, (x, y, z) in enumerate(lamp_locations):
    lamp = Asset(f'Pendant_{i}')
    pipe(lamp, 'drop', .022, (x, y, z+.13), (x, y, 3.24), iron)
    pipe(lamp, 'neck', .07,
         (x, y, z+.01), (x, y, z+.12), (.16, .19, .15))
    pipe(lamp, 'shade_top', .15,
         (x, y, z-.025), (x, y, z+.015), (.39, .43, .36))
    pipe(lamp, 'shade_rim', .235,
         (x, y, z-.075), (x, y, z-.035), (.64, .68, .60))
    underside = Asset(f'LampGlow_{i}')
    pipe(underside, 'disc', .215,
         (x, y, z-.084), (x, y, z-.076), (.96, .98, .90))
    lamp.include(f'LampGlow_{i}', underside)
    lamps.include(f'Pendant_{i}', lamp)
scene.include('lamps', lamps)

realize(scene)
set_view(position=CAMERA_POSITION, target=CAMERA_TARGET,
         lens=CAMERA_LENS, sensor=36, shift=CAMERA_SHIFT)

bs = bpy.context.scene
if bs.world is None:
    bs.world = bpy.data.worlds.new('World')
bs.world.use_nodes = True
background = bs.world.node_tree.nodes.get('Background')
if background:
    background.inputs['Color'].default_value = (.26, .29, .23, 1)
    background.inputs['Strength'].default_value = .18

for i, (x, y, z) in enumerate(lamp_locations):
    area_emitter(position=(x, y, z-.13),
                 power=[125, 78, 55][i], size=[.6, .5, .45][i],
                 target=(x, y+.5, .1), color=(.96, .98, .88))
area_emitter(position=(.1, -2.8, 2.45), power=40, size=3,
             target=(0, 3, 1.4), color=(1, .86, .68))

def mesh_descendants(root):
    if root.type == 'MESH':
        yield root
    for child in root.children:
        yield from mesh_descendants(child)

for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    for material in obj.data.materials:
        if material is None:
            continue
        material.use_nodes = True
        shader = material.node_tree.nodes.get('Principled BSDF')
        if shader and 'Roughness' in shader.inputs:
            shader.inputs['Roughness'].default_value = .43

for i in range(len(lamp_locations)):
    markers = [obj for obj in bpy.data.objects
               if obj.type != 'MESH'
               and obj.name.split('.')[0] == f'LampGlow_{i}']
    for marker in markers:
        for obj in mesh_descendants(marker):
            for slot in obj.material_slots:
                if slot.material is None:
                    continue
                material = slot.material.copy()
                slot.material = material
                material.use_nodes = True
                shader = material.node_tree.nodes.get('Principled BSDF')
                if shader:
                    if 'Emission Color' in shader.inputs:
                        shader.inputs['Emission Color'].default_value = (.92, .98, 1, 1)
                    elif 'Emission' in shader.inputs:
                        shader.inputs['Emission'].default_value = (.92, .98, 1, 1)
                    if 'Emission Strength' in shader.inputs:
                        shader.inputs['Emission Strength'].default_value = 3

bs.view_settings.view_transform = 'AgX'
