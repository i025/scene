# Reference inventory and image anchors, estimated from the photograph:
# - Room: dark carpet occupies roughly (0, .59) to (1, 1); back wall spans
#   (.11, .38) to (.53, .61); right wall extends from the back corner to the
#   entire right edge. The ceiling fills the upper portion of the image.
# - Back-right corner: ceiling approximately (.52, .38), floor (.52, .59).
#   Ceiling and floor edges on the right wall slope upward and downward,
#   respectively, as they approach the right image edge.
# - Whiteboard on the right wall: approximately (.59, .25) to (.91, .58),
#   with a narrow gray border and bottom tray.
# - Back wall: dark rectangular vent around (.15, .44)-(.24, .47); open
#   electrical panel and small wall plates around (.30, .45)-(.43, .54).
# - Small hanging American flag near (.46, .33)-(.51, .42), in front of
#   the back corner. Its exact attachment and folds are uncertain.
# - Left side: bright partition from approximately (0, .33) to (.12, .67);
#   missing ceiling tiles and dark voids above it.
# - Foreground: scattered dark broken panels and narrow metal strips in the
#   left and middle floor; yellow folded insulation near (.56, .68)-(.90, .79);
#   long pale rails extend toward the lower right edge. Individual fragments
#   are irregular and partly occluded, so their shapes are approximate.
#
# Approximate expanded primitive count: architecture 7, ceiling and grid 45,
# board 6, back-wall fittings 9, flag 14, foreground debris 24, partition 4:
# about 109 separate primitives, plus lights. No boolean operations.

import math
import bpy
from mathutils import Vector
from sceneact import Scene, Asset, box, rod, realize, set_view, area_emitter

scene = Scene("Damaged office")

# Dimensions and camera parameters are separate so either can be revised.
room_width = 4.6
back_y = 5.0
front_y = -7.0
room_height = 3.0
right_x = room_width / 2
left_x = -room_width / 2
camera_position = (-1.50, -6.0, 1.55)
camera_target = (1.85, 5.0, 1.57)
camera_lens = 35

wall_color = (0.72, 0.70, 0.65)
ceiling_color = (0.68, 0.70, 0.69)
grid_color = (0.46, 0.48, 0.47)
carpet_color = (0.085, 0.082, 0.075)
trim_color = (0.10, 0.11, 0.105)

architecture = Asset("Room architecture")
architecture.include("carpet", box(
    (room_width, 12.5, 0.10),
    center=(0, -0.75, -0.05), color=carpet_color))
architecture.include("back wall", box(
    (room_width, 0.12, room_height),
    center=(0, back_y + 0.06, room_height / 2), color=wall_color))
architecture.include("right wall", box(
    (0.12, 12.1, room_height),
    center=(right_x + 0.06, -1.0, room_height / 2), color=(0.75, 0.73, 0.68)))
architecture.include("back baseboard", box(
    (room_width, 0.035, 0.16),
    center=(0, back_y - 0.025, 0.08), color=trim_color))
architecture.include("right baseboard", box(
    (0.035, 12.0, 0.16),
    center=(right_x - 0.025, -1.0, 0.08), color=trim_color))
scene.include("architecture", architecture)

# Suspended ceiling: large light panels, thin grid, and dark openings at left.
ceiling = Asset("Suspended ceiling")
ceiling.include("ceiling backing", box(
    (room_width, 12.0, 0.045),
    center=(0, -1.0, room_height + 0.04), color=(0.24, 0.25, 0.24)))
# The leftmost row is interrupted near the camera.
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

# Bright temporary partition on the near left.
partition = Asset("Left partition")
partition.include("main white surface", box(
    (0.08, 4.5, 2.45), center=(left_x + 0.04, -1.3, 1.225),
    color=(0.86, 0.87, 0.85)))
for y in (-2.8, -1.4, 0.0):
    partition.include("vertical seam %.1f" % y, box(
        (0.012, 0.018, 2.25), center=(left_x + 0.09, y, 1.23),
        color=(0.75, 0.77, 0.75)))
scene.include("partition", partition)

# Whiteboard lies on the right wall, long dimension along the room.
board = Asset("Right wall whiteboard")
board_y = 2.05
board_length = 3.65
board_z = 1.77
board_height = 1.38
board.include("white writing surface", box(
    (0.035, board_length, board_height),
    center=(right_x - 0.035, board_y, board_z),
    color=(0.82, 0.83, 0.82)))
for y in (board_y - board_length / 2, board_y + board_length / 2):
    board.include("vertical frame %.2f" % y, box(
        (0.055, 0.035, board_height + 0.05),
        center=(right_x - 0.06, y, board_z), color=(0.47, 0.49, 0.48)))
for z in (board_z - board_height / 2, board_z + board_height / 2):
    board.include("horizontal frame %.2f" % z, box(
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

# A small hanging fabric flag, represented as separate stripe meshes.
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

# Flat broken ceiling pieces and metal strips on the carpet.
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
                color=(.18, .19, .18) if i % 2 else (.27, .27, .25))
    piece.turn(axis="+z", degrees=angle)
    debris.include("broken dark panel %d" % i, piece)
    if i in (0, 2, 3, 6):
        shard = box((sx * .65, sy * .17, .012),
                    center=(x, y, .044), color=(.48, .47, .43))
        shard.turn(axis="+z", degrees=angle + 7)
        debris.include("exposed fragment %d" % i, shard)
for i, (x, y, length, angle) in enumerate([
    (-1.0, .25, 1.6, -20), (-1.25, -1.05, 1.45, 18),
    (.9, -2.0, 2.7, -20), (1.35, -2.3, 2.5, -20)
]):
    rail = box((length, .045, .025), center=(x, y, .045),
               color=(.60, .61, .59))
    rail.turn(axis="+z", degrees=angle)
    debris.include("loose metal strip %d" % i, rail)

# Yellow insulation sheets overlap the loose rails.
insulation = Asset("Yellow insulation")
for i, (x, y, z, sx, sy, ang) in enumerate([
    (1.00, -.80, .085, 1.25, .76, -9),
    (1.22, -1.05, .125, 1.10, .72, -7),
    (.75, -.55, .070, .72, .62, 2),
]):
    sheet = box((sx, sy, .055), center=(x, y, z),
                color=(.72 + .025 * i, .59 + .02 * i, .22))
    sheet.turn(axis="+z", degrees=ang)
    insulation.include("overlapping yellow sheet %d" % i, sheet)
scene.include("debris", debris)
scene.include("insulation", insulation)

realize(scene)

# Set the original portrait aspect before making the projection check.
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
area_emitter((0, -1.5, 2.85), power=450, size=5,
             target=(0, 1, 0), color=(1.0, .98, .94))
area_emitter((-1.5, -4, 2.4), power=240, size=4,
             target=(0, 3, 1), color=(.91, .94, 1.0))

# Restrained procedural carpet texture, leaving all scene geometry editable.
for obj in bpy.data.objects:
    if obj.type == "MESH" and "carpet" in obj.name.lower():
        for mat in obj.data.materials:
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            bsdf = nodes.get("Principled BSDF")
            if bsdf:
                noise = nodes.new("ShaderNodeTexNoise")
                noise.inputs["Scale"].default_value = 155
                noise.inputs["Detail"].default_value = 2
                ramp = nodes.new("ShaderNodeValToRGB")
                ramp.color_ramp.elements[0].color = (.035, .034, .031, 1)
                ramp.color_ramp.elements[1].color = (.13, .125, .11, 1)
                links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
                links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
                bsdf.inputs["Roughness"].default_value = .95

# Geometry landmarks and visual reference estimates, (x right, y down).
landmarks = [
    ("back corner ceiling", (right_x, back_y, room_height), (.52, .38)),
    ("back corner floor", (right_x, back_y, 0), (.52, .59)),
    ("board far upper", (right_x, board_y + board_length / 2,
                         board_z + board_height / 2), (.59, .35)),
    ("board near lower", (right_x, board_y - board_length / 2,
                          board_z - board_height / 2), (.91, .58)),
    ("insulation near edge", (1.7, -1.4, .15), (.89, .77)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("Landmark                         reference       projected")
for name, point, reference in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (
        .5 * (clip.x / clip.w + 1), .5 * (1 - clip.y / clip.w))
    print("%-30s %s %s" % (name, reference,
          None if uv is None else tuple(round(v, 3) for v in uv)))
