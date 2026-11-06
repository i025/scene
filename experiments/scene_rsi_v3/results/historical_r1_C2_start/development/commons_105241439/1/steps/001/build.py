# Reference inventory, normalized image coordinates:
# - Off-white classroom wall fills the upper background; blue painted lower wall
#   begins around y=0.61. Floor is visible along the bottom, mostly occluded.
# - Wide green chalkboard at x=0.11..0.90, y=0.28..0.68, split vertically at
#   the center. Left panel has broad chalk smudges; right has vertical streaks.
# - Small paper notice hangs above the board at x=0.46..0.60, y=0.06..0.23,
#   with a small dark wall fixture to its left.
# - Middle desk top at x=0.19..0.60, y=0.79..0.85, with thin metal legs.
#   A wooden chair back rises behind it at x=0.29..0.38, y=0.74..0.80.
# - Foreground desk spans x=0.09..0.58 from y=0.88 to the bottom edge;
#   its legs and a chair are partly cut off. Another desk and chair enter from
#   the lower right. Their hidden portions and exact construction are uncertain.
# Estimated expanded primitive count: about 150, including board marks,
# notice details, furniture parts and architecture. No boolean operations.

from sceneact import *
import bpy
import math
import random

random.seed(8)
scene = Scene("Classroom")

cream = (0.73, 0.72, 0.67)
blue = (0.015, 0.12, 0.34)
floor_col = (0.56, 0.40, 0.29)
green_l = (0.055, 0.20, 0.115)
green_r = (0.055, 0.16, 0.095)
chalk = (0.43, 0.57, 0.43)
pale_chalk = (0.62, 0.68, 0.55)
wood = (0.74, 0.43, 0.19)
topwood = (0.91, 0.68, 0.38)
edgewood = (0.75, 0.43, 0.19)
metal = (0.55, 0.57, 0.54)
darkmetal = (0.25, 0.28, 0.27)

architecture = Asset("architecture")
architecture.include("upper_plaster_wall", box((8.5, 0.15, 4.8), center=(0, 0.08, 2.85), color=cream))
architecture.include("blue_lower_wall", box((8.5, 0.035, 1.40), center=(0, -0.015, 0.70), color=blue))
architecture.include("floor", box((8.5, 6.0, 0.09), center=(0, -2.9, -0.055), color=floor_col))
architecture.include("baseboard", box((8.5, 0.045, 0.075), center=(0, -0.06, 0.04), color=(0.72, 0.62, 0.51)))
scene.include("room", architecture)

board = Asset("chalkboard")
board_bottom = 1.11
board_top = 2.87
board_mid = (board_bottom + board_top) / 2
board.include("left_panel", box((2.73, 0.065, 1.76), center=(-1.37, -0.095, board_mid), color=green_l))
board.include("right_panel", box((2.73, 0.065, 1.76), center=(1.37, -0.095, board_mid), color=green_r))
board.include("center_seam", box((0.025, 0.025, 1.76), center=(0, -0.14, board_mid), color=(0.24, 0.27, 0.21)))
board.include("bottom_rail", box((5.50, 0.045, 0.035), center=(0, -0.15, board_bottom), color=(0.46, 0.48, 0.40)))
board.include("top_edge", box((5.50, 0.025, 0.018), center=(0, -0.13, board_top), color=(0.18, 0.24, 0.17)))

# Broad, irregular chalk traces across the left board.
for i in range(34):
    x = random.uniform(-2.65, -0.12)
    z = random.uniform(1.20, 2.75)
    length = random.uniform(0.10, 0.60)
    dx = random.uniform(-0.13, 0.13)
    dz = random.uniform(-0.08, 0.08)
    board.include("left_chalk_%02d" % i, rod(
        random.uniform(0.0025, 0.009),
        start=(x, -0.137, z), end=(min(-0.03, x + length), -0.137, z + dz),
        color=random.choice([chalk, pale_chalk, (0.28, 0.43, 0.29)])))
for i in range(32):
    x = random.uniform(-2.65, 2.65)
    z = random.uniform(1.25, 2.62)
    length = random.uniform(0.15, 0.68)
    board.include("vertical_chalk_%02d" % i, rod(
        random.uniform(0.0015, 0.005),
        start=(x, -0.139, z), end=(x + random.uniform(-0.025, 0.025), -0.139, min(2.83, z + length)),
        color=random.choice([(0.25, 0.37, 0.26), (0.34, 0.45, 0.33)])))
# Curved wiped areas near the middle of the left half.
for j in range(4):
    points = []
    for k in range(8):
        a = 0.2 + k * 2.25 / 7
        points.append((-0.72 + (0.48 + j * 0.06) * math.cos(a),
                       -0.142,
                       2.20 + (0.40 + j * 0.035) * math.sin(a)))
    board.include("wiped_arc_%d" % j, sweep_tube(points=points, radius=0.006, color=(0.34, 0.46, 0.33)))
scene.include("board", board)

notice = Asset("hanging_notice")
notice.include("paper", box((0.96, 0.015, 0.74), center=(0.18, -0.085, 3.49), color=(0.78, 0.77, 0.71)))
notice.include("top_bar", box((0.98, 0.02, 0.025), center=(0.18, -0.102, 3.86), color=(0.63, 0.59, 0.51)))
notice.include("bottom_bar", box((0.98, 0.02, 0.018), center=(0.18, -0.102, 3.12), color=(0.65, 0.61, 0.54)))
notice.include("left_string", rod(0.003, start=(-0.30, -0.095, 3.86), end=(0.18, -0.095, 4.14), color=(0.49, 0.46, 0.40)))
notice.include("right_string", rod(0.003, start=(0.66, -0.095, 3.86), end=(0.18, -0.095, 4.14), color=(0.49, 0.46, 0.40)))
for row in range(9):
    z = 3.72 - row * 0.061
    notice.include("print_left_%d" % row, box((random.uniform(0.18, 0.35), 0.006, 0.007), center=(-0.09, -0.105, z), color=(0.46, 0.45, 0.42)))
    notice.include("print_right_%d" % row, box((random.uniform(0.12, 0.24), 0.006, 0.007), center=(0.38, -0.105, z), color=(0.46, 0.45, 0.42)))
scene.include("notice", notice)

fixture = Asset("small_wall_fixture")
fixture.include("dark_round_mount", ball(0.055, center=(-0.48, -0.10, 3.68), color=(0.09, 0.09, 0.08)))
fixture.include("center", ball(0.018, center=(-0.48, -0.153, 3.68), color=(0.46, 0.44, 0.40)))
scene.include("wall_fixture", fixture)

def make_desk(name, x, y, width, depth, height):
    desk = Asset(name)
    desk.include("wooden_top", box((width, depth, 0.075), center=(x, y, height), color=topwood))
    desk.include("front_edge", box((width, 0.025, 0.065), center=(x, y - depth/2, height - 0.02), color=edgewood))
    for sx in (-1, 1):
        lx = x + sx * (width/2 - 0.12)
        for sy in (-1, 1):
            ly = y + sy * (depth/2 - 0.09)
            desk.include("leg_%d_%d" % (sx, sy), rod(0.024,
                start=(lx + sx * 0.035, ly, 0.02),
                end=(lx, ly, height - 0.035), color=metal))
    desk.include("underframe", rod(0.018, start=(x-width/2+0.13, y, height-0.13),
                                  end=(x+width/2-0.13, y, height-0.13), color=darkmetal))
    return desk

def make_chair(name, x, y, width=0.64):
    chair = Asset(name)
    chair.include("seat", box((width, 0.43, 0.055), center=(x, y, 0.46), color=wood))
    chair.include("backrest", box((width * 0.88, 0.045, 0.48), center=(x, y + 0.20, 0.82), color=wood))
    for sx in (-1, 1):
        lx = x + sx * (width/2 - 0.055)
        chair.include("back_upright_%d" % sx, rod(0.018, start=(lx, y+0.19, 0.03),
                                                  end=(lx, y+0.19, 1.05), color=metal))
        chair.include("front_leg_%d" % sx, rod(0.018, start=(lx, y-0.18, 0.03),
                                               end=(lx, y-0.18, 0.45), color=metal))
    return chair

scene.include("middle_chair", make_chair("middle_chair", -1.12, -1.12, 0.65))
scene.include("middle_desk", make_desk("middle_desk", -0.75, -1.48, 2.65, 0.56, 0.78))
scene.include("foreground_chair", make_chair("foreground_chair", -1.70, -2.64, 0.83))
scene.include("foreground_desk", make_desk("foreground_desk", -1.03, -2.45, 3.00, 0.63, 0.78))
scene.include("right_chair", make_chair("right_chair", 2.52, -2.62, 0.85))
scene.include("right_desk", make_desk("right_desk", 2.62, -2.40, 1.86, 0.64, 0.78))

realize(scene)

# Subtle vertical chalk texture on the large board surfaces.
for obj in bpy.data.objects:
    if obj.type != 'MESH':
        continue
    if "panel" not in obj.name.lower():
        continue
    if not obj.data.materials:
        continue
    mat = obj.data.materials[0].copy()
    obj.data.materials[0] = mat
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        tex = nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 4.0
        tex.inputs["Detail"].default_value = 2.0
        mapping = nodes.new("ShaderNodeVectorMath")
        mapping.operation = 'MULTIPLY'
        mapping.inputs[1].default_value = (6.0, 1.0, 0.32)
        coord = nodes.new("ShaderNodeTexCoord")
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.22
        ramp.color_ramp.elements[0].color = (0.025, 0.085, 0.045, 1)
        ramp.color_ramp.elements[1].position = 0.80
        ramp.color_ramp.elements[1].color = (0.14, 0.25, 0.14, 1)
        links.new(coord.outputs["Generated"], mapping.inputs[0])
        links.new(mapping.outputs[0], tex.inputs["Vector"])
        links.new(tex.outputs["Fac"], ramp.inputs[0])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.87

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

set_view((0, -10.8, 2.35), (0, 0, 1.84), lens=50, sensor=36)
area_emitter((-3.5, -4.5, 6.5), power=800, size=6, target=(0, 0, 1.6))
area_emitter((4, -1, 5), power=350, size=5, target=(0, 0, 1.6))
