# Reference inventory, approximate normalized image coordinates:
# - Pale plaster wall above a deep blue lower wall, with a narrow strip of floor
#   at the bottom. The wall color boundary is near y=0.61.
# - Green two-panel chalkboard at x=0.11..0.90, y=0.28..0.68. The center seam
#   is visible. The left panel has cloudy, curved chalk smears and the right
#   has darker vertical wipe streaks.
# - Small hanging paper notice at x=0.46..0.60, y=0.06..0.23, with a dark
#   round fixture just to its left.
# - Middle desk at x=0.19..0.60, y=0.79..0.85, and a chair back behind it.
# - Foreground desk at x=0.09..0.58, y=0.88..1.00; a cropped chair overlaps
#   its front. A second cropped desk and chair enter from the right.
#   Hidden furniture construction and the exact chalk marks are uncertain.
#
# Review of the second rendering: the board placement is close, but its surface
# is too light and uniformly streaked. The desks and foreground chair backs
# occupy too much of the lower image. This revision darkens the board, gives the
# left and right panels different wear, and lowers the visible furniture.
# Estimated expanded primitives: approximately 125: 4 room parts, 5 board
# parts, 30 chalk marks, 25 notice/fixture parts, and about 60 furniture parts.
# No boolean operations.

from sceneact import *
import bpy
import random

random.seed(18)
scene = Scene("Classroom")

cream = (0.73, 0.72, 0.67)
blue = (0.008, 0.075, 0.27)
floor_col = (0.58, 0.43, 0.34)
wood = (0.68, 0.35, 0.12)
topwood = (0.90, 0.65, 0.34)
edgewood = (0.72, 0.39, 0.15)
metal = (0.49, 0.51, 0.48)

room = Asset("architecture")
room.include("upper_plaster_wall", box((8.5, 0.15, 4.8),
    center=(0, 0.08, 2.85), color=cream))
room.include("blue_lower_wall", box((8.5, 0.035, 1.28),
    center=(0, -0.015, 0.64), color=blue))
room.include("floor", box((8.5, 6.0, 0.09),
    center=(0, -2.9, -0.055), color=floor_col))
room.include("baseboard", box((8.5, 0.045, 0.045),
    center=(0, -0.06, 0.025), color=(0.69, 0.55, 0.43)))
scene.include("room", room)

board = Asset("chalkboard")
bottom, top = 0.99, 2.95
mid = (bottom + top) / 2
board.include("left_panel", box((3.02, 0.065, top-bottom),
    center=(-1.51, -0.095, mid), color=(0.025, 0.10, 0.05)))
board.include("right_panel", box((3.02, 0.065, top-bottom),
    center=(1.51, -0.095, mid), color=(0.018, 0.075, 0.035)))
board.include("center_seam", box((0.022, 0.025, top-bottom),
    center=(0, -0.14, mid), color=(0.10, 0.14, 0.09)))
board.include("bottom_rail", box((6.05, 0.045, 0.025),
    center=(0, -0.15, bottom), color=(0.30, 0.34, 0.26)))
board.include("top_edge", box((6.05, 0.025, 0.015),
    center=(0, -0.13, top), color=(0.10, 0.16, 0.10)))

# Fine vertical drips supplement the procedural board wear.
for i in range(30):
    x = random.uniform(-2.96, 2.96)
    z = random.uniform(1.05, 2.58)
    length = random.uniform(0.10, 0.54)
    board.include("chalk_drip_%02d" % i, rod(
        random.uniform(0.0015, 0.0035),
        start=(x, -0.132, z),
        end=(x + random.uniform(-0.014, 0.014), -0.132,
             min(2.90, z + length)),
        color=random.choice([(0.10, 0.19, 0.11),
                             (0.20, 0.29, 0.19),
                             (0.29, 0.36, 0.25)])))
scene.include("board", board)

notice = Asset("hanging_notice")
notice.include("paper", box((1.02, 0.015, 0.78),
    center=(0.22, -0.085, 3.68), color=(0.78, 0.76, 0.70)))
notice.include("top_bar", box((1.04, 0.02, 0.02),
    center=(0.22, -0.102, 4.07), color=(0.65, 0.61, 0.54)))
notice.include("bottom_bar", box((1.04, 0.02, 0.016),
    center=(0.22, -0.102, 3.29), color=(0.66, 0.62, 0.55)))
notice.include("left_string", rod(0.0025,
    start=(-0.29, -0.095, 4.07), end=(0.22, -0.095, 4.36),
    color=(0.52, 0.49, 0.43)))
notice.include("right_string", rod(0.0025,
    start=(0.73, -0.095, 4.07), end=(0.22, -0.095, 4.36),
    color=(0.52, 0.49, 0.43)))
for row in range(9):
    z = 3.98 - row * 0.065
    notice.include("print_left_%d" % row, box(
        (random.uniform(0.18, 0.35), 0.006, 0.006),
        center=(-0.04, -0.105, z), color=(0.46, 0.45, 0.42)))
    notice.include("print_right_%d" % row, box(
        (random.uniform(0.12, 0.24), 0.006, 0.006),
        center=(0.43, -0.105, z), color=(0.46, 0.45, 0.42)))
scene.include("notice", notice)

fixture = Asset("wall_fixture")
fixture.include("round_mount", ball(0.055, center=(-0.50, -0.10, 3.87),
    color=(0.055, 0.055, 0.05)))
fixture.include("center", ball(0.018, center=(-0.50, -0.153, 3.87),
    color=(0.40, 0.39, 0.35)))
scene.include("wall_fixture", fixture)

def make_desk(name, x, y, width, depth, height):
    desk = Asset(name)
    desk.include("wooden_top", box((width, depth, 0.075),
        center=(x, y, height), color=topwood))
    desk.include("front_edge", box((width, 0.025, 0.065),
        center=(x, y-depth/2, height-0.02), color=edgewood))
    for sx in (-1, 1):
        lx = x + sx * (width/2 - 0.12)
        for sy in (-1, 1):
            ly = y + sy * (depth/2 - 0.09)
            desk.include("leg_%d_%d" % (sx, sy), rod(0.024,
                start=(lx + sx*0.035, ly, -0.4),
                end=(lx, ly, height-0.035), color=metal))
    desk.include("underframe", rod(0.018,
        start=(x-width/2+0.13, y, height-0.13),
        end=(x+width/2-0.13, y, height-0.13),
        color=(0.25, 0.28, 0.27)))
    return desk

def make_chair(name, x, y, width, back_bottom, back_top):
    chair = Asset(name)
    chair.include("seat", box((width, 0.43, 0.055),
        center=(x, y, back_bottom-0.14), color=wood))
    chair.include("backrest", box((width*0.88, 0.045, back_top-back_bottom),
        center=(x, y+0.20, (back_bottom+back_top)/2), color=wood))
    for sx in (-1, 1):
        lx = x + sx*(width/2-0.055)
        chair.include("back_upright_%d" % sx, rod(0.018,
            start=(lx, y+0.19, -0.5),
            end=(lx, y+0.19, back_top), color=metal))
        chair.include("front_leg_%d" % sx, rod(0.018,
            start=(lx, y-0.18, -0.5),
            end=(lx, y-0.18, back_bottom-0.14), color=metal))
    return chair

scene.include("middle_chair",
    make_chair("middle_chair", -1.12, -1.12, 0.65, 0.39, 0.75))
scene.include("middle_desk",
    make_desk("middle_desk", -0.75, -1.48, 2.65, 0.56, 0.52))
scene.include("foreground_chair",
    make_chair("foreground_chair", -1.70, -3.65, 0.83, -0.34, 0.18))
scene.include("foreground_desk",
    make_desk("foreground_desk", -1.03, -2.45, 3.00, 0.63, 0.26))
scene.include("right_chair",
    make_chair("right_chair", 2.52, -3.65, 0.85, -0.34, 0.18))
scene.include("right_desk",
    make_desk("right_desk", 2.62, -2.40, 1.86, 0.64, 0.26))

realize(scene)

# The panel colors are generated from editable procedural materials. The left
# uses irregular broad chalk wear mixed with faint vertical streaks; the right
# emphasizes darker vertical wiping.
panels = []
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        dims = obj.dimensions
        if 2.9 < dims.x < 3.2 and 1.8 < dims.z < 2.1 and dims.y < 0.15:
            panels.append(obj)

for obj in panels:
    if not obj.data.materials:
        continue
    mat = obj.data.materials[0].copy()
    obj.data.materials[0] = mat
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        continue
    left = obj.location.x < 0
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeVectorMath")
    mapping.operation = 'MULTIPLY'
    mapping.inputs[1].default_value = (8.0 if left else 13.0, 1.0,
                                       2.0 if left else 0.55)
    tex = nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = 3.2
    tex.inputs["Detail"].default_value = 3.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.24
    ramp.color_ramp.elements[1].position = 0.79
    if left:
        ramp.color_ramp.elements[0].color = (0.008, 0.035, 0.015, 1)
        ramp.color_ramp.elements[1].color = (0.12, 0.21, 0.11, 1)
    else:
        ramp.color_ramp.elements[0].color = (0.006, 0.027, 0.012, 1)
        ramp.color_ramp.elements[1].color = (0.075, 0.14, 0.075, 1)
    links.new(coord.outputs["Generated"], mapping.inputs[0])
    links.new(mapping.outputs[0], tex.inputs["Vector"])
    links.new(tex.outputs["Fac"], ramp.inputs[0])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.88

sc = bpy.context.scene
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
background.inputs["Color"].default_value = (0.82, 0.83, 0.79, 1)
background.inputs["Strength"].default_value = 0.8

set_view((0, -10.8, 1.78), (0, 0, 1.84), lens=50, sensor=36)
area_emitter((-3.5, -4.5, 6.5), power=800, size=6, target=(0, 0, 1.6))
area_emitter((4, -1, 5), power=350, size=5, target=(0, 0, 1.6))
