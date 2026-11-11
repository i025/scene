import bpy
import random
from mathutils import Vector
from sceneact import *

# Reference inventory and comparison with the second full render, normalized:
# Cream wall and blue boundary: reference y=.61; render y=.62. Floor strip:
# reference begins near .93; render near .96. Both edges are nearly horizontal.
# Board: reference x=.11–.895, y=.28–.68; render x=.10–.90, y=.29–.70.
# The two panels meet at x=.50. Reference is dark green with irregular pale
# wiped patches, especially on the left; the render is uniformly pale and
# vertically striped. The board overlaps the wall-color boundary.
# Notice: reference x=.46–.61, y=.06–.23; render x=.46–.60, y=.07–.24.
# Rear desk: reference x=.19–.60, y=.79–.85; render x=.17–.57, y=.78–.84.
# Rear chair back: reference x=.29–.38, y=.73–.80; render x=.27–.37,
# y=.73–.79. The desk overlaps the chair's lower edge.
# Front left desktop: reference x=.09–.59, y=.89–.96; render is cropped at
# x=0 and extends to .62, y=.85–.92. Front right desktop: reference starts
# near x=.75 at y=.89; render starts near x=.84 at y=.85. Chair backs overlap
# the front edges and continue below the image. Legs and hidden furniture
# construction are uncertain. Vertical edges are close to upright.
#
# Ranked corrections:
# 1. Board material: reduce the ramp colors substantially and add broad,
# irregular lighter wiping on the left. This changes surface appearance, not
# the board's already close contour. Illumination also affects brightness.
# 2. Front desk widths and positions: narrow and shift the left desk right;
# shift the right desk left. Lower both tops to move their contours downward.
# This restores the gaps and crops without moving the background anchors.
# 3. Move the rear desk slightly right and down. Keep its chair nearly fixed.
# 4. Narrow the board slightly and raise its bottom edge, matching its observed
# bounds. Raise the floor and baseboard slightly to expose the reference strip.
# The camera remains fixed: its previously computed board landmarks were
# (.100,.286) and (.900,.691), separate from observed silhouette estimates.
#
# Estimated expanded primitive count: architecture 4, board 4, notice 15,
# chalk flecks 24, furniture 36 = about 83 meshes. Procedural nodes add none.

random.seed(19)
BOARD_WIDTH = 5.30
BOARD_BOTTOM = 1.33
BOARD_TOP = 3.10
BOARD_HEIGHT = BOARD_TOP - BOARD_BOTTOM
BLUE_HEIGHT = 1.62

CAMERA_POSITION = (0.0, -8.0, 2.13)
CAMERA_TARGET = (0.0, 0.0, 2.13)
CAMERA_LENS = 42.3

scene = Scene("Classroom")
cream = (.79, .78, .72)
blue = (.009, .055, .24)
wood = (.60, .30, .10)
wood_light = (.90, .65, .33)
wood_edge = (.72, .36, .10)
metal = (.42, .44, .42)

architecture = Asset("architecture")
architecture.include("cream_wall", box(
    (9, .10, 5), center=(0, .08, 2.5), color=cream))
architecture.include("blue_lower_wall", box(
    (9, .026, BLUE_HEIGHT), center=(0, .012, BLUE_HEIGHT/2), color=blue))
architecture.include("floor", box(
    (9, 8, .08), center=(0, -3.9, .055), color=(.60, .43, .31)))
architecture.include("baseboard", box(
    (9, .045, .055), center=(0, -.025, .135), color=(.78, .72, .61)))
scene.include("architecture", architecture)

board = Asset("chalkboard")
half = BOARD_WIDTH / 2
board.include("left_green_panel", box(
    (half, .075, BOARD_HEIGHT),
    center=(-half/2, -.035, (BOARD_TOP+BOARD_BOTTOM)/2),
    color=(.018, .055, .025)))
board.include("right_green_panel", box(
    (half, .075, BOARD_HEIGHT),
    center=(half/2, -.035, (BOARD_TOP+BOARD_BOTTOM)/2),
    color=(.012, .045, .020)))
board.include("center_joint", box(
    (.022, .025, BOARD_HEIGHT),
    center=(0, -.085, (BOARD_TOP+BOARD_BOTTOM)/2), color=(.12, .15, .10)))
board.include("bottom_edge", box(
    (BOARD_WIDTH, .036, .022), center=(0, -.083, BOARD_BOTTOM),
    color=(.32, .36, .28)))

chalk = Asset("chalk_accents")
for i in range(24):
    x = random.uniform(-2.58, 2.58)
    z = random.uniform(BOARD_BOTTOM+.05, BOARD_TOP-.05)
    chalk.include("fleck_%02d" % i, box(
        (random.uniform(.004, .012), .002, random.uniform(.025, .15)),
        center=(x, -.074, z),
        color=random.choice([(.16, .24, .15), (.23, .31, .21),
                             (.30, .36, .26)])))
board.include("chalk_accents", chalk)
scene.include("chalkboard", board)

notice = Asset("hanging_notice")
notice.include("sheet", box(
    (.96, .018, .75), center=(.20, -.045, 3.69), color=(.83, .81, .75)))
notice.include("top_edge", box(
    (.96, .012, .012), center=(.20, -.060, 4.065), color=(.67, .64, .57)))
notice.include("left_string", rod(
    .004, start=(-.27, -.052, 4.06), end=(.20, -.052, 4.42),
    color=(.60, .58, .51)))
notice.include("right_string", rod(
    .004, start=(.67, -.052, 4.06), end=(.20, -.052, 4.42),
    color=(.60, .58, .51)))
for i in range(10):
    notice.include("printed_row_%02d" % i, box(
        (random.uniform(.42, .78), .004, .006),
        center=(.20 + random.uniform(-.06, .06), -.058, 3.43+i*.057),
        color=(.50, .49, .45)))
notice.include("wall_hook", ball(
    .052, center=(-.46, -.055, 3.89), color=(.09, .09, .075)))
scene.include("notice", notice)

def add_desk(name, x, y, width, depth, top_z):
    desk = Asset(name)
    desk.include("wooden_top", box(
        (width, depth, .065), center=(x, y, top_z), color=wood_light))
    desk.include("front_wood_edge", box(
        (width, .025, .06), center=(x, y-depth/2-.012, top_z-.008),
        color=wood_edge))
    for side in (-1, 1):
        for fore in (-1, 1):
            lx = x + side*(width/2-.13)
            ly = y + fore*(depth/2-.10)
            desk.include("leg_%s_%s" % (side, fore), rod(
                .026, start=(lx, ly, .10), end=(lx, ly, top_z-.04),
                color=metal))
    desk.include("under_top_bar", rod(
        .018, start=(x-width/2+.10, y, top_z-.13),
        end=(x+width/2-.10, y, top_z-.13), color=metal))
    scene.include(name, desk)

def add_chair(name, x, y, width, back_bottom, back_top):
    chair = Asset(name)
    chair.include("plywood_back", box(
        (width, .055, back_top-back_bottom),
        center=(x, y, (back_bottom+back_top)/2), color=wood))
    chair.include("back_top_edge", box(
        (width, .06, .025), center=(x, y, back_top), color=(.84, .59, .31)))
    for side in (-1, 1):
        xx = x + side*(width/2-.05)
        chair.include("back_support_%s" % side, rod(
            .018, start=(xx, y+.025, .18), end=(xx, y+.025, back_top-.03),
            color=metal))
    chair.include("seat", box(
        (width, .42, .045), center=(x, y-.16, .47), color=wood_light))
    scene.include(name, chair)

add_chair("rear_chair", -.99, -1.42, .57, 1.00, 1.25)
add_desk("rear_desk", -.55, -1.72, 2.03, .54, 1.02)
add_desk("foreground_left_desk", -.64, -2.85, 2.05, .62, .90)
add_chair("foreground_left_chair", -1.42, -3.22, .70, .50, .88)
add_desk("foreground_right_desk", 2.10, -2.85, 1.75, .59, .90)
add_chair("foreground_right_chair", 2.05, -3.20, .73, .48, .86)

realize(scene)
sc = bpy.context.scene
sc.render.resolution_x = 512
sc.render.resolution_y = 337
sc.render.resolution_percentage = 100
set_view(CAMERA_POSITION, CAMERA_TARGET, lens=CAMERA_LENS, sensor=36)

def make_board_material(name, left):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Roughness"].default_value = .92

    coord = nodes.new("ShaderNodeTexCoord")
    stretch = nodes.new("ShaderNodeVectorMath")
    stretch.operation = 'MULTIPLY'
    stretch.inputs[1].default_value = (18.0, 1.0, 1.2 if left else .55)
    links.new(coord.outputs["Generated"], stretch.inputs[0])
    streak = nodes.new("ShaderNodeTexNoise")
    streak.inputs["Scale"].default_value = 3.0
    streak.inputs["Detail"].default_value = 3.0
    streak.inputs["Roughness"].default_value = .7
    links.new(stretch.outputs[0], streak.inputs["Vector"])

    broad = nodes.new("ShaderNodeTexNoise")
    broad.inputs["Scale"].default_value = 4.0
    broad.inputs["Detail"].default_value = 2.0
    links.new(coord.outputs["Generated"], broad.inputs["Vector"])
    mix = nodes.new("ShaderNodeMixRGB")
    mix.blend_type = 'MULTIPLY'
    mix.inputs[0].default_value = .45 if left else .12
    links.new(streak.outputs["Fac"], mix.inputs[1])
    links.new(broad.outputs["Fac"], mix.inputs[2])

    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .16
    ramp.color_ramp.elements[1].position = .72
    if left:
        ramp.color_ramp.elements[0].color = (.004, .018, .007, 1)
        ramp.color_ramp.elements[1].color = (.065, .115, .058, 1)
    else:
        ramp.color_ramp.elements[0].color = (.003, .014, .005, 1)
        ramp.color_ramp.elements[1].color = (.048, .085, .041, 1)
    links.new(mix.outputs[0], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return mat

left_mat = make_board_material("Left board wiped surface", True)
right_mat = make_board_material("Right board wiped surface", False)
for obj in sc.objects:
    if obj.type == 'MESH':
        d = obj.dimensions
        if abs(d.x-half) < .03 and abs(d.z-BOARD_HEIGHT) < .03 and d.y < .12:
            obj.data.materials.clear()
            obj.data.materials.append(left_mat if obj.location.x < 0 else right_mat)

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
background.inputs["Color"].default_value = (.78, .79, .76, 1)
background.inputs["Strength"].default_value = .8
area_emitter((-3, -4, 6), power=850, size=5,
             target=(0, 0, 1.5), color=(1.0, .94, .84))
area_emitter((4, -2, 5), power=350, size=4,
             target=(0, 0, 1.5), color=(.86, .91, 1.0))

# Same camera as the previous successful render; no camera trial is needed.
# Estimated reference points and computed projections are reported separately.
landmarks = [
    ("board upper left", (-half, -.075, BOARD_TOP), (.11, .28)),
    ("board lower right", (half, -.075, BOARD_BOTTOM), (.895, .68)),
    ("rear desk left top", (-1.565, -1.99, 1.0525), (.19, .79)),
    ("foreground left edge", (-1.665, -3.16, .9325), (.09, .89)),
]
bpy.context.view_layer.update()
cam = sc.camera
dg = bpy.context.evaluated_depsgraph_get()
projection = cam.calc_matrix_camera(
    dg, x=sc.render.resolution_x, y=sc.render.resolution_y,
    scale_x=sc.render.pixel_aspect_x, scale_y=sc.render.pixel_aspect_y)
print("Landmark                      reference       projected")
for name, point, reference in landmarks:
    clip = projection @ cam.matrix_world.inverted() @ Vector((*point, 1.0))
    uv = None if clip.w <= 1e-8 else (
        .5*(clip.x/clip.w+1), .5*(1-clip.y/clip.w))
    print("%-28s %s %s" % (
        name, reference, None if uv is None else tuple(round(v, 3) for v in uv)))
