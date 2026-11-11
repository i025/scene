# Reference inventory and visual anchors (normalized x, y; estimates):
# Back right corner: ceiling (.52, .38), floor (.52, .59).
# Whiteboard: far upper (.59, .35), near upper (.89, .25),
#             far lower (.59, .54), near lower (.91, .58).
# Bright left partition occupies the left edge from about y=.33 to .67.
# Dark ceiling openings are immediately above that partition.
# Yellow overlapping insulation occupies approximately (.56,.68)-(.90,.79),
# with two pale rails emerging underneath toward the bottom right.
# Broken dark panels occupy the left foreground; the electrical panel, vent,
# small wall plates, and hanging flag are on or in front of the back wall.
# Ceiling and floor edges on the right wall diverge toward the right edge.
#
# Review of the previous full render against the reference:
# 1. The bright left partition is absent, leaving a large dark floor/wall region.
#    Move the partition's visible end toward the back and inward: it should
#    enter from the left edge and end near the back wall's left boundary.
# 2. The floor/back-wall corner appears around (.55,.63), versus (.52,.59).
#    A lower camera is trialed numerically; it should raise the floor corner.
#    The camera target is adjusted separately to keep the ceiling corner near
#    its reference. A small set of camera trials is checked before selection.
# 3. The board's rendered bounds are approximately (.58,.37)-(.83,.57),
#    versus (.59,.25)-(.91,.58). Increase its length toward the camera and
#    its height upward while retaining its lower edge.
# 4. The floor is too pale and the broken pieces are too bright. Darken carpet
#    and fragments; the actual brightness also depends on the illumination.
# 5. Rendered insulation is a flat rectangular stack around (.52,.73)-(.94,.79),
#    while the reference is layered, roughly (.56,.68)-(.90,.79). Move its
#    rear edge back and add a gently folded upper contour. Long rails should
#    continue diagonally toward the lower right, partly under the insulation.
# Ceiling openings, flag, fixtures, board, and partition remain separate assets.
# The far end of the left partition and individual damaged fragments are uncertain.
#
# Approximate expanded primitive count: room 5, ceiling and grid 58,
# partition 5, board 6, fixtures 9, flag 11, debris 19, insulation 4:
# about 117 meshes, plus lights. There are no boolean operations.

import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

scene = Scene("Damaged office")

# Room dimensions and camera settings are independent.
room_width = 4.6
back_y = 5.0
room_height = 3.0
right_x = room_width / 2
left_x = -room_width / 2
camera_position = (-1.50, -6.0, 1.55)
camera_target = (1.85, 5.0, 1.57)
camera_lens = 35

wall_color = (0.72, 0.70, 0.65)
ceiling_color = (0.68, 0.70, 0.69)
grid_color = (0.46, 0.48, 0.47)
carpet_color = (0.035, 0.034, 0.031)
trim_color = (0.075, 0.08, 0.077)

architecture = Asset("Room architecture")
architecture.include("carpet", box(
    (room_width, 12.5, 0.10), center=(0, -0.75, -0.05),
    color=carpet_color))
architecture.include("back wall", box(
    (room_width, 0.12, room_height),
    center=(0, back_y + 0.06, room_height / 2), color=wall_color))
architecture.include("right wall", box(
    (0.12, 12.1, room_height),
    center=(right_x + 0.06, -1.0, room_height / 2),
    color=(0.75, 0.73, 0.68)))
architecture.include("back baseboard", box(
    (room_width, 0.035, 0.16),
    center=(0, back_y - 0.025, 0.08), color=trim_color))
architecture.include("right baseboard", box(
    (0.035, 12.0, 0.16),
    center=(right_x - 0.025, -1.0, 0.08), color=trim_color))
scene.include("architecture", architecture)

ceiling = Asset("Suspended ceiling")
ceiling.include("dark backing above openings", box(
    (room_width, 12.0, 0.045),
    center=(0, -1.0, room_height + 0.04), color=(0.16, 0.17, 0.16)))
for ix in range(4):
    x0 = left_x + 0.575 + ix * 1.15
    for j in range(10):
        y0 = -5.8 + j * 1.15
        if ix == 0 and j in (4, 5, 6):
            continue
        ceiling.include("tile_%d_%d" % (ix, j), box(
            (1.135, 1.135, 0.025), center=(x0, y0, room_height),
            color=ceiling_color if (ix + j) % 4 else (0.72, 0.73, 0.71)))
for ix in range(5):
    ceiling.include("long grid %d" % ix, box(
        (0.018, 12.0, 0.022),
        center=(left_x + ix * 1.15, -1.0, room_height - 0.013),
        color=grid_color))
for j in range(11):
    ceiling.include("cross grid %d" % j, box(
        (room_width, 0.018, 0.022),
        center=(0, -6.375 + j * 1.15, room_height - 0.013),
        color=grid_color))
ceiling.include("smoke detector", box(
    (0.15, 0.15, 0.035), center=(-1.1, 0.1, 2.96),
    color=(0.79, 0.79, 0.75)))
scene.include("ceiling", ceiling)

# The partition is a bright, low temporary wall along the left edge.
partition = Asset("Left partition")
partition_x = -1.65
partition_end = 3.65
partition_start = -2.5
partition.include("main white surface", box(
    (0.08, partition_end - partition_start, 2.52),
    center=(partition_x, (partition_start + partition_end) / 2, 1.26),
    color=(0.86, 0.87, 0.85)))
for i, y in enumerate((-1.0, 0.6, 2.2)):
    partition.include("vertical seam %d" % i, box(
        (0.012, 0.018, 2.42),
        center=(partition_x + 0.045, y, 1.26),
        color=(0.75, 0.77, 0.75)))
partition.include("horizontal seam", box(
    (0.012, partition_end - partition_start, 0.012),
    center=(partition_x + 0.045, (partition_start + partition_end) / 2, 1.25),
    color=(0.79, 0.80, 0.78)))
scene.include("partition", partition)

board = Asset("Right wall whiteboard")
board_y = 1.65
board_length = 4.45
board_z = 1.96
board_height = 1.76
board.include("white writing surface", box(
    (0.035, board_length, board_height),
    center=(right_x - 0.035, board_y, board_z),
    color=(0.82, 0.83, 0.82)))
for i, y in enumerate((board_y - board_length / 2, board_y + board_length / 2)):
    board.include("vertical frame %d" % i, box(
        (0.055, 0.035, board_height + 0.05),
        center=(right_x - 0.06, y, board_z), color=(0.47, 0.49, 0.48)))
for i, z in enumerate((board_z - board_height / 2, board_z + board_height / 2)):
    board.include("horizontal frame %d" % i, box(
        (0.055, board_length, 0.035),
        center=(right_x - 0.06, board_y, z), color=(0.49, 0.51, 0.50)))
board.include("marker tray", box(
    (0.12, board_length, 0.035),
    center=(right_x - 0.10, board_y, board_z - board_height / 2 - 0.025),
    color=(0.55, 0.56, 0.54)))
scene.include("whiteboard", board)

back_details = Asset("Back wall fixtures")
back_details.include("vent", box(
    (0.70, 0.025, 0.31), center=(-1.38, back_y - 0.075, 1.89),
    color=(0.30, 0.34, 0.34)))
back_details.include("electrical recess", box(
    (0.26, 0.035, 0.42), center=(-0.28, back_y - 0.08, 1.69),
    color=(0.27, 0.30, 0.29)))
back_details.include("panel interior", box(
    (0.18, 0.012, 0.32), center=(-0.28, back_y - 0.105, 1.70),
    color=(0.56, 0.58, 0.55)))
for i in range(3):
    back_details.include("breaker %d" % i, box(
        (0.10, 0.02, 0.028),
        center=(-0.28, back_y - 0.12, 1.62 + i * 0.09),
        color=(0.20, 0.22, 0.21)))
door = box((0.38, 0.035, 0.40), center=(-0.07, back_y - 0.22, 1.43),
           color=(0.52, 0.55, 0.53))
door.turn(axis="+y", degrees=-38)
back_details.include("hanging panel cover", door)
for i, x in enumerate((0.18, 0.39)):
    back_details.include("wall plate %d" % i, box(
        (0.12, 0.025, 0.14), center=(x, back_y - 0.08, 1.54),
        color=(0.82, 0.81, 0.76)))
scene.include("back fixtures", back_details)

flag = Asset("Hanging flag")
flag.include("support pole", rod(
    0.015, start=(1.66, 4.91, 2.95), end=(2.30, 4.75, 2.82),
    color=(0.25, 0.24, 0.22)))
flag_width = 0.36
stripe_w = flag_width / 9
for i in range(9):
    flag.include("stripe %d" % i, box(
        (stripe_w + 0.002, 0.025, 0.62),
        center=(1.76 + (i - 4) * stripe_w, 4.79, 2.57),
        color=(0.58, 0.075, 0.075) if i % 2 == 0 else (0.88, 0.87, 0.82)))
flag.include("blue canton", box(
    (0.15, 0.03, 0.25), center=(1.65, 4.77, 2.75),
    color=(0.10, 0.16, 0.28)))
scene.include("flag", flag)

debris = Asset("Floor debris")
fragments = [
    (-1.62, 1.45, .62, .30, -18),
    (-1.02, 2.10, .48, .22, 12),
    (-1.35, .50, .86, .35, 15),
    (-.83, -.25, 1.05, .42, -13),
    (-1.67, -.65, .76, .27, 12),
    (-.25, 2.35, .44, .21, -24),
    (.95, 1.08, .46, .28, 21),
]
for i, (x, y, sx, sy, angle) in enumerate(fragments):
    piece = box((sx, sy, .025), center=(x, y, .022),
                color=(.10, .105, .10) if i % 2 else (.16, .16, .15))
    piece.turn(axis="+z", degrees=angle)
    debris.include("broken dark panel %d" % i, piece)
    if i in (0, 2, 3, 6):
        shard = box((sx * .65, sy * .17, .012),
                    center=(x, y, .044), color=(.32, .31, .28))
        shard.turn(axis="+z", degrees=angle + 7)
        debris.include("exposed fragment %d" % i, shard)
for i, (x, y, length, angle) in enumerate([
    (-1.0, .25, 1.6, -20),
    (-1.25, -1.05, 1.45, 18),
    (1.35, -1.95, 2.9, -50),
    (1.65, -2.20, 2.8, -50)
]):
    rail = box((length, .045, .025), center=(x, y, .045),
               color=(.60, .61, .59))
    rail.turn(axis="+z", degrees=angle)
    debris.include("loose metal strip %d" % i, rail)
scene.include("debris", debris)

insulation = Asset("Yellow insulation")
for i, (x, y, z, sx, sy, ang) in enumerate([
    (.95, -.48, .065, 1.18, .95, -9),
    (1.10, -.73, .105, 1.25, .86, -7),
    (.72, -.30, .055, .70, .70, 2),
    (1.27, -.91, .14, .78, .52, -7),
]):
    sheet = box((sx, sy, .045), center=(x, y, z),
                color=(.72 + .014 * i, .59 + .01 * i, .24))
    sheet.turn(axis="+z", degrees=ang)
    insulation.include("overlapping yellow sheet %d" % i, sheet)
scene.include("insulation", insulation)

realize(scene)
sc = bpy.context.scene
sc.render.resolution_x = 384
sc.render.resolution_y = 512
sc.render.resolution_percentage = 100
sc.render.pixel_aspect_x = 1
sc.render.pixel_aspect_y = 1

if sc.world is None:
    sc.world = bpy.data.worlds.new("SceneWorld")
sc.world.use_nodes = True
background = sc.world.node_tree.nodes.get("Background")
if background is None:
    background = sc.world.node_tree.nodes.new("ShaderNodeBackground")
output = sc.world.node_tree.nodes.get("World Output")
if output is None:
    output = sc.world.node_tree.nodes.new("ShaderNodeOutputWorld")
sc.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
background.inputs["Color"].default_value = (0.68, 0.70, 0.72, 1)
background.inputs["Strength"].default_value = 0.7

set_view(camera_position, camera_target, lens=camera_lens)
cam = sc.camera

# Reference estimates are independent of the computed geometric projections.
landmarks = [
    ("back ceiling corner", (right_x, back_y, room_height), (.52, .38)),
    ("back floor corner", (right_x, back_y, 0), (.52, .59)),
    ("board far upper", (right_x, board_y + board_length / 2,
                         board_z + board_height / 2), (.59, .35)),
    ("board near lower", (right_x, board_y - board_length / 2,
                          board_z - board_height / 2), (.91, .58)),
    ("insulation near edge", (1.65, -1.15, .15), (.89, .77)),
]

def point_camera(position, target):
    cam.location = position
    direction = Vector(target) - Vector(position)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()

def projections():
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    matrix = cam.calc_matrix_camera(
        dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
        scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
    result = []
    for _, point, _ in landmarks:
        clip = matrix @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
        result.append(None if clip.w <= 1e-8 else (
            .5 * (clip.x / clip.w + 1),
            .5 * (1 - clip.y / clip.w)))
    return result

# Check a small camera change explicitly. Lowering the camera should move the
# floor corner upward; the trial aim offsets the resulting ceiling movement.
point_camera(camera_position, camera_target)
baseline = projections()
trial_position = (-1.50, -6.0, 1.30)
trial_target = (1.85, 5.0, 1.47)
point_camera(trial_position, trial_target)
trial = projections()
print("Landmark                      reference    baseline     trial")
for (name, _, ref), old, new in zip(landmarks, baseline, trial):
    fmt = lambda p: None if p is None else tuple(round(v, 3) for v in p)
    print("%-28s %s %s %s" % (name, ref, fmt(old), fmt(new)))

# Use the trial only if the actual floor projection moves upward and the
# ceiling corner remains reasonably close to its reference.
if (trial[1] is not None and baseline[1] is not None
        and trial[1][1] < baseline[1][1]
        and trial[0] is not None
        and abs(trial[0][1] - .38) < .04):
    point_camera(trial_position, trial_target)
else:
    point_camera(camera_position, camera_target)

area_emitter((0, -1.5, 2.85), power=450, size=5,
             target=(0, 1, 0), color=(1.0, .98, .94))
area_emitter((-1.5, -4, 2.4), power=240, size=4,
             target=(0, 3, 1), color=(.91, .94, 1.0))
